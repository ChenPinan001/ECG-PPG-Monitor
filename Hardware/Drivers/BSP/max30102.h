#ifndef __MAX30102_H
#define __MAX30102_H

#include "./SYSTEM/sys/sys.h"

#define MAX30102_I2C_ADDR       0xAE
#define MAX30102_I2C_ADDR_R     0xAF

#define MAX30102_REG_INTR_STATUS_1   0x00
#define MAX30102_REG_INTR_STATUS_2   0x01
#define MAX30102_REG_INTR_ENABLE_1   0x02
#define MAX30102_REG_INTR_ENABLE_2   0x03
#define MAX30102_REG_FIFO_WR_PTR     0x04
#define MAX30102_REG_OVF_COUNTER     0x05
#define MAX30102_REG_FIFO_RD_PTR     0x06
#define MAX30102_REG_FIFO_DATA       0x07
#define MAX30102_REG_FIFO_CONFIG     0x08
#define MAX30102_REG_MODE_CONFIG     0x09
#define MAX30102_REG_SPO2_CONFIG     0x0A
#define MAX30102_REG_LED1_PA         0x0C
#define MAX30102_REG_LED2_PA         0x0D
#define MAX30102_REG_SLOT_1_2        0x11
#define MAX30102_REG_SLOT_3_4        0x12
#define MAX30102_REG_REV_ID          0xFE
#define MAX30102_REG_PART_ID         0xFF

#define MAX30102_MODE_SPO2      0x03
#define MAX30102_SPO2_SR_200    0x03
#define MAX30102_PW_411US       0x03

typedef struct {
    uint32_t red;
    uint32_t ir;
} MAX30102_Data;

void     MAX30102_Init(I2C_HandleTypeDef *hi2c);
uint8_t  MAX30102_ReadReg(uint8_t reg);
void     MAX30102_WriteReg(uint8_t reg, uint8_t val);
uint8_t  MAX30102_GetFifoCount(void);
uint8_t  MAX30102_ReadFifo(MAX30102_Data *data);
uint8_t  MAX30102_ReadFifoAll(MAX30102_Data *buf, uint8_t max_samples);

#endif
