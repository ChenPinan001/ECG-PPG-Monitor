#ifndef _ATK_MAX30102_H
#define _ATK_MAX30102_H
#include "./SYSTEM/sys/sys.h"

#define INT_GPIO_PORT                   GPIOB
#define INT_GPIO_PIN                    GPIO_PIN_5
#define INT_GPIO_CLK_ENABLE()           do{ __HAL_RCC_GPIOB_CLK_ENABLE(); }while(0)
#define INT_IRQn                        EXTI9_5_IRQn
#define INT_IRQHandler                  EXTI9_5_IRQHandler

#define MAX30102_I2C_ADDR               (0xAE)

#define MAX30102_INTR_STATUS_1          0x00
#define MAX30102_INTR_STATUS_2          0x01
#define MAX30102_INTR_ENABLE_1          0x02
#define MAX30102_INTR_ENABLE_2          0x03

#define MAX30102_FIFO_WR_PTR            0x04
#define MAX30102_OVF_COUNTER            0x05
#define MAX30102_FIFO_RD_PTR            0x06
#define MAX30102_FIFO_DATA              0x07

#define MAX30102_FIFO_CONFIG            0x08
#define MAX30102_MODE_CONFIG            0x09
#define MAX30102_SPO2_CONFIG            0x0A
#define MAX30102_LED1_PA                0x0C
#define MAX30102_LED2_PA                0x0D

#define MAX30102_MULTI_LED_CTRL1        0x11
#define MAX30102_MULTI_LED_CTRL2        0x12

#define MAX30102_TEMP_INTR              0x1F
#define MAX30102_TEMP_FRAC              0x20
#define MAX30102_TEMP_CONFIG            0x21

#define MAX30102_PROX_INT_THRESH        0x30

#define MAX30102_REV_ID                 0xFE
#define MAX30102_PART_ID                0xFF

extern uint8_t g_max30102_int_flag;

uint8_t atk_max30102_write_byte(uint8_t reg, uint8_t data);
uint8_t atk_max30102_read_byte(uint8_t reg);
int atk_max30102_read_nbytes(uint8_t reg, uint8_t *date, uint8_t len);
void atk_max30102_reset(void);
void atk_max30102_init(void);
void atk_max30102_fifo_read(uint32_t *red_data, uint32_t *ir_data);

#endif
