#include "./BSP/ATK_MAX30102/atk_max30102.h"
#include "./BSP/IIC/myiic.h"
#include "./SYSTEM/usart/usart.h"
#include "./SYSTEM/delay/delay.h"

uint8_t g_max30102_int_flag = 0;

uint8_t atk_max30102_write_byte(uint8_t reg, uint8_t data)
{
    iic_start();
    iic_send_byte(MAX30102_I2C_ADDR | 0x00);
    if (iic_wait_ack() != 0) { iic_stop(); return 1; }
    iic_send_byte(reg);
    if (iic_wait_ack() != 0) { iic_stop(); return 1; }
    iic_send_byte(data);
    if (iic_wait_ack() != 0) { iic_stop(); return 1; }
    iic_stop();
    return 0;
}

uint8_t atk_max30102_read_byte(uint8_t reg)
{
    uint8_t temp = 0;

    iic_start();
    iic_send_byte(MAX30102_I2C_ADDR | 0x00);
    if (iic_wait_ack() != 0) { iic_stop(); return 0; }
    iic_send_byte(reg);
    if (iic_wait_ack() != 0) { iic_stop(); return 0; }

    iic_start();
    iic_send_byte(MAX30102_I2C_ADDR | 0x01);
    if (iic_wait_ack() != 0) { iic_stop(); return 0; }
    temp = iic_read_byte(0);
    iic_stop();

    return temp;
}

int atk_max30102_read_nbytes(uint8_t reg, uint8_t *date, uint8_t len)
{
    uint8_t i;

    iic_start();
    iic_send_byte(MAX30102_I2C_ADDR | 0x00);
    if (iic_wait_ack() != 0) { iic_stop(); return 1; }
    iic_send_byte(reg);
    if (iic_wait_ack() != 0) { iic_stop(); return 1; }

    iic_start();
    iic_send_byte(MAX30102_I2C_ADDR | 0x01);
    if (iic_wait_ack() != 0) { iic_stop(); return 1; }
    for (i = 0; i < len; i++)
    {
        date[i] = iic_read_byte((i == (len - 1)) ? 0 : 1);
    }
    iic_stop();

    return 0;
}

void atk_max30102_reset(void)
{
    atk_max30102_write_byte(MAX30102_MODE_CONFIG, 0x40);
    delay_ms(10);
}

void atk_max30102_fifo_read(uint32_t *red_data, uint32_t *ir_data)
{
    uint8_t receive_data[6];

    atk_max30102_read_byte(MAX30102_INTR_STATUS_1);
    atk_max30102_read_byte(MAX30102_INTR_STATUS_2);

    atk_max30102_read_nbytes(MAX30102_FIFO_DATA, receive_data, 6);
    *red_data = ((receive_data[0] << 16 | receive_data[1] << 8 | receive_data[2]) & 0x03ffff);
    *ir_data  = ((receive_data[3] << 16 | receive_data[4] << 8 | receive_data[5]) & 0x03ffff);
}

void atk_max30102_init(void)
{
    GPIO_InitTypeDef gpio_init_struct;

    INT_GPIO_CLK_ENABLE();
    gpio_init_struct.Pin = INT_GPIO_PIN;
    gpio_init_struct.Mode = GPIO_MODE_IT_FALLING;
    gpio_init_struct.Pull = GPIO_PULLUP;
    HAL_GPIO_Init(INT_GPIO_PORT, &gpio_init_struct);

    HAL_NVIC_SetPriority(INT_IRQn, 0, 2);
    HAL_NVIC_EnableIRQ(INT_IRQn);

    iic_init();

    atk_max30102_reset();

    atk_max30102_write_byte(MAX30102_INTR_ENABLE_1, 0xC0);
    atk_max30102_write_byte(MAX30102_INTR_ENABLE_2, 0x00);

    atk_max30102_write_byte(MAX30102_FIFO_WR_PTR, 0x00);
    atk_max30102_write_byte(MAX30102_OVF_COUNTER, 0x00);
    atk_max30102_write_byte(MAX30102_FIFO_RD_PTR, 0x00);

    atk_max30102_write_byte(MAX30102_FIFO_CONFIG, 0x4F);
    atk_max30102_write_byte(MAX30102_MODE_CONFIG, 0x03);
    atk_max30102_write_byte(MAX30102_SPO2_CONFIG, 0x2A);

    atk_max30102_write_byte(MAX30102_LED1_PA, 0x2F);
    atk_max30102_write_byte(MAX30102_LED2_PA, 0x2F);

    delay_ms(100);

    atk_max30102_read_byte(MAX30102_INTR_STATUS_1);
    atk_max30102_read_byte(MAX30102_INTR_STATUS_2);
}

void INT_IRQHandler(void)
{
    HAL_GPIO_EXTI_IRQHandler(INT_GPIO_PIN);
    __HAL_GPIO_EXTI_CLEAR_IT(INT_GPIO_PIN);
}

void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin)
{
    if (GPIO_Pin == INT_GPIO_PIN)
    {
        g_max30102_int_flag = 1;
    }
}
