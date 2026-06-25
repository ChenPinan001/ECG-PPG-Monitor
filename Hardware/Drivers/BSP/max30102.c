#include "max30102.h"

static I2C_HandleTypeDef *pHi2c;

void MAX30102_WriteReg(uint8_t reg, uint8_t val)
{
    HAL_I2C_Mem_Write(pHi2c, MAX30102_I2C_ADDR, reg,
                      I2C_MEMADD_SIZE_8BIT, &val, 1, 100);
}

uint8_t MAX30102_ReadReg(uint8_t reg)
{
    uint8_t val = 0;
    HAL_I2C_Mem_Read(pHi2c, MAX30102_I2C_ADDR, reg,
                     I2C_MEMADD_SIZE_8BIT, &val, 1, 100);
    return val;
}

static void MAX30102_ReadRegs(uint8_t reg, uint8_t *buf, uint8_t len)
{
    HAL_I2C_Mem_Read(pHi2c, MAX30102_I2C_ADDR, reg,
                     I2C_MEMADD_SIZE_8BIT, buf, len, 100);
}

void MAX30102_Init(I2C_HandleTypeDef *hi2c)
{
    pHi2c = hi2c;
    HAL_Delay(100);

    /* reset */
    MAX30102_WriteReg(MAX30102_REG_MODE_CONFIG, 0x40);
    HAL_Delay(100);

    /* enable A_FULL interrupt */
    MAX30102_WriteReg(MAX30102_REG_INTR_ENABLE_1, 0x80);
    MAX30102_WriteReg(MAX30102_REG_INTR_ENABLE_2, 0x00);

    /* clear status */
    MAX30102_ReadReg(MAX30102_REG_INTR_STATUS_1);
    MAX30102_ReadReg(MAX30102_REG_INTR_STATUS_2);

    /* fifo: avg=1, almost_full=17 */
    MAX30102_WriteReg(MAX30102_REG_FIFO_CONFIG, 0x4F);

    /* SpO2 mode */
    MAX30102_WriteReg(MAX30102_REG_MODE_CONFIG, MAX30102_MODE_SPO2);

    /* SpO2: 200SPS, 18bit */
    MAX30102_WriteReg(MAX30102_REG_SPO2_CONFIG,
                      (MAX30102_SPO2_SR_200 << 5) | MAX30102_PW_411US);

    /* led current */
    MAX30102_WriteReg(MAX30102_REG_LED1_PA, 0x3F);
    MAX30102_WriteReg(MAX30102_REG_LED2_PA, 0x3F);

    MAX30102_WriteReg(MAX30102_REG_SLOT_1_2, 0x00);
    MAX30102_WriteReg(MAX30102_REG_SLOT_3_4, 0x00);

    HAL_Delay(100);
}

uint8_t MAX30102_GetFifoCount(void)
{
    uint8_t wr = MAX30102_ReadReg(MAX30102_REG_FIFO_WR_PTR);
    uint8_t rd = MAX30102_ReadReg(MAX30102_REG_FIFO_RD_PTR);
    return (wr - rd) & 0x1F;
}

uint8_t MAX30102_ReadFifo(MAX30102_Data *data)
{
    uint8_t buf[6];
    MAX30102_ReadRegs(MAX30102_REG_FIFO_DATA, buf, 6);
    data->red = ((uint32_t)buf[0] << 16) | ((uint32_t)buf[1] << 8) | buf[2];
    data->ir  = ((uint32_t)buf[3] << 16) | ((uint32_t)buf[4] << 8) | buf[5];
    data->red &= 0x3FFFF;
    data->ir  &= 0x3FFFF;
    return 0;
}

uint8_t MAX30102_ReadFifoAll(MAX30102_Data *buf, uint8_t max_samples)
{
    uint8_t count = MAX30102_GetFifoCount();
    uint8_t i;
    if (count > max_samples) count = max_samples;
    for (i = 0; i < count; i++) {
        MAX30102_ReadFifo(&buf[i]);
    }
    return count;
}
