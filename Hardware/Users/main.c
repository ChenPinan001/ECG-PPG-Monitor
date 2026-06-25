/**
 ******************************************************************************
 * @file     main.c
 * @brief    ECG(AD8232) + PPG(MAX30102) -> UART 12-byte frame
 ******************************************************************************
 */

#include "./SYSTEM/sys/sys.h"
#include "./SYSTEM/usart/usart.h"
#include "./SYSTEM/delay/delay.h"
#include "./BSP/ATK_MAX30102/atk_max30102.h"
#include <string.h>
#include <stdio.h>

#define FRAME_HEADER_0  0xAA
#define FRAME_HEADER_1  0x55
#define FRAME_TYPE_ECG_PPG  0x01
#define FRAME_TYPE_PPG_RED_IR  0x04
#define FRAME_LEN       12

#define DC_WINDOW       200
#define SIGNAL_LOST_THRESHOLD   50
#define SIGNAL_LOST_COUNT       2

ADC_HandleTypeDef g_adc1_handle;

/* DC removal buffers - global to avoid stack overflow */
#define DC_WINDOW 200
static uint32_t g_buf_red[DC_WINDOW];
static uint32_t g_buf_ir[DC_WINDOW];

static void adc1_init(void)
{
    GPIO_InitTypeDef gpio_init_struct;
    __HAL_RCC_GPIOA_CLK_ENABLE();
    __HAL_RCC_ADC1_CLK_ENABLE();
    gpio_init_struct.Pin = GPIO_PIN_0;
    gpio_init_struct.Mode = GPIO_MODE_ANALOG;
    HAL_GPIO_Init(GPIOA, &gpio_init_struct);
    g_adc1_handle.Instance = ADC1;
    g_adc1_handle.Init.ScanConvMode = ADC_SCAN_DISABLE;
    g_adc1_handle.Init.ContinuousConvMode = DISABLE;
    g_adc1_handle.Init.DiscontinuousConvMode = DISABLE;
    g_adc1_handle.Init.ExternalTrigConv = ADC_SOFTWARE_START;
    g_adc1_handle.Init.DataAlign = ADC_DATAALIGN_RIGHT;
    g_adc1_handle.Init.NbrOfConversion = 1;
    HAL_ADC_Init(&g_adc1_handle);
    ADC_ChannelConfTypeDef sConfig = {0};
    sConfig.Channel = ADC_CHANNEL_0;
    sConfig.Rank = ADC_REGULAR_RANK_1;
    sConfig.SamplingTime = ADC_SAMPLETIME_239CYCLES_5;
    HAL_ADC_ConfigChannel(&g_adc1_handle, &sConfig);
}

static uint16_t adc1_read(void)
{
    HAL_ADC_Start(&g_adc1_handle);
    HAL_ADC_PollForConversion(&g_adc1_handle, 10);
    return (uint16_t)HAL_ADC_GetValue(&g_adc1_handle);
}

static uint8_t xor_checksum(const uint8_t *data, uint8_t len)
{
    uint8_t sum = 0, i;
    for (i = 0; i < len; i++) sum ^= data[i];
    return sum;
}

static void send_frame(uint8_t type, int32_t val1, int32_t val2)
{
    uint8_t frame[FRAME_LEN];
    frame[0] = FRAME_HEADER_0; frame[1] = FRAME_HEADER_1; frame[2] = type;
    frame[3]  = (uint8_t)(val1);       frame[4]  = (uint8_t)(val1 >> 8);
    frame[5]  = (uint8_t)(val1 >> 16); frame[6]  = (uint8_t)(val1 >> 24);
    frame[7]  = (uint8_t)(val2);       frame[8]  = (uint8_t)(val2 >> 8);
    frame[9]  = (uint8_t)(val2 >> 16); frame[10] = (uint8_t)(val2 >> 24);
    frame[11] = xor_checksum(frame, 11);
    HAL_UART_Transmit(&g_uart1_handle, frame, FRAME_LEN, 20);
}

static void send_text(const char *msg)
{
    HAL_UART_Transmit(&g_uart1_handle, (uint8_t *)msg, strlen(msg), 100);
}

int main(void)
{
    uint32_t raw_red, raw_ir;
    uint16_t buf_idx = 0;
    uint8_t  buf_filled = 0;
    uint32_t sum_red = 0, sum_ir = 0;
    uint16_t warmup = 0;

    /* 3-point moving average */
    int32_t ma_red[3] = {0}, ma_ir[3] = {0};
    uint8_t ma_idx = 0, ma_cnt = 0;

    int32_t ppg_peak = -32768, ppg_trough = 32767;
    uint16_t sample_count = 0;
    uint8_t lost_count = 0, alarm_sent = 0;

    HAL_Init();
    sys_stm32_clock_init(RCC_PLL_MUL9);
    delay_init(72);
    usart_init(115200);

    send_text("UART OK\r\n");

    adc1_init();
    send_text("ADC OK\r\n");

    atk_max30102_init();
    send_text("MAX30102 INIT DONE\r\n");

    /* Test I2C: read PART_ID (should be 0x15) */
    uint8_t part_id = atk_max30102_read_byte(MAX30102_PART_ID);
    char buf[32];
    int len = sprintf(buf, "PART_ID=0x%02X\r\n", part_id);
    HAL_UART_Transmit(&g_uart1_handle, (uint8_t *)buf, len, 100);

    atk_max30102_read_byte(MAX30102_INTR_STATUS_1);
    atk_max30102_read_byte(MAX30102_INTR_STATUS_2);

    memset(g_buf_red, 0, sizeof(g_buf_red));
    memset(g_buf_ir, 0, sizeof(g_buf_ir));

    while (1)
    {
        if (g_max30102_int_flag || (HAL_GPIO_ReadPin(INT_GPIO_PORT, INT_GPIO_PIN) == GPIO_PIN_RESET))
        {
            g_max30102_int_flag = 0;
            atk_max30102_fifo_read(&raw_red, &raw_ir);

            /* Skip first 400 samples for sensor warmup */
            if (warmup < 400) {
                warmup++;
                continue;
            }

            /* Update sliding window sum */
            if (buf_filled) {
                sum_red -= g_buf_red[buf_idx];
                sum_ir  -= g_buf_ir[buf_idx];
            }
            g_buf_red[buf_idx] = raw_red;
            g_buf_ir[buf_idx]  = raw_ir;
            sum_red += raw_red;
            sum_ir  += raw_ir;
            buf_idx++;
            if (buf_idx >= DC_WINDOW) {
                buf_idx = 0;
                buf_filled = 1;
            }

            /* Skip until buffer is full */
            if (!buf_filled) continue;

            /* DC = window mean, AC = raw - DC */
            int32_t dc_red = sum_red / DC_WINDOW;
            int32_t dc_ir  = sum_ir / DC_WINDOW;
            int32_t ac_red = (int32_t)raw_red - dc_red;
            int32_t ac_ir  = (int32_t)raw_ir  - dc_ir;

            /* 3-point moving average */
            ma_red[ma_idx] = ac_red;
            ma_ir[ma_idx]  = ac_ir;
            ma_idx = (ma_idx + 1) % 3;
            if (ma_cnt < 3) ma_cnt++;
            int32_t sr = 0, si = 0;
            for (uint8_t k = 0; k < ma_cnt; k++) { sr += ma_red[k]; si += ma_ir[k]; }
            ac_red = sr / ma_cnt;
            ac_ir  = si / ma_cnt;

            int32_t ecg_val = (int32_t)adc1_read();

            send_frame(FRAME_TYPE_ECG_PPG, ecg_val, ac_red);

            if (sample_count % 50 == 0) {
                send_frame(FRAME_TYPE_PPG_RED_IR, ac_red, ac_ir);
            }

            if (ac_red > ppg_peak)  ppg_peak = ac_red;
            if (ac_red < ppg_trough) ppg_trough = ac_red;
            sample_count++;

            if (sample_count >= 200)
            {
                int32_t amplitude = ppg_peak - ppg_trough;
                if (amplitude < SIGNAL_LOST_THRESHOLD)
                {
                    lost_count++;
                    if (lost_count >= SIGNAL_LOST_COUNT && !alarm_sent)
                    {
                        send_text("[ALARM] PPG signal lost\r\n");
                        alarm_sent = 1;
                    }
                }
                else
                {
                    lost_count = 0;
                    if (alarm_sent) {
                        send_text("[INFO] PPG signal recovered\r\n");
                        alarm_sent = 0;
                    }
                }
                ppg_peak = -32768;
                ppg_trough = 32767;
                sample_count = 0;
            }
        }
    }
}
