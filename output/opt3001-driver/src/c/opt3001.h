#ifndef OPT3001_H
#define OPT3001_H

#include <stdint.h>
#include <stdbool.h>

// I2C address
#define OPT3001_I2C_ADDR 0x44

// Register addresses
#define OPT3001_REG_RESULT 0x00
#define OPT3001_REG_CONFIG 0x01
#define OPT3001_REG_LOW_LIMIT 0x02
#define OPT3001_REG_HIGH_LIMIT 0x03
#define OPT3001_REG_MANUFACTURER_ID 0x7E
#define OPT3001_REG_DEVICE_ID 0x7F

// Configuration register settings
#define OPT3001_CONFIG_RN_MASK 0xF000
#define OPT3001_CONFIG_CT_MASK 0x0800
#define OPT3001_CONFIG_M_MASK 0x0600
#define OPT3001_CONFIG_OVF_MASK 0x0100
#define OPT3001_CONFIG_CRF_MASK 0x0080
#define OPT3001_CONFIG_FH_MASK 0x0040
#define OPT3001_CONFIG_FL_MASK 0x0020
#define OPT3001_CONFIG_L_MASK 0x0010
#define OPT3001_CONFIG_POL_MASK 0x0008
#define OPT3001_CONFIG_ME_MASK 0x0008
#define OPT3001_CONFIG_FC_MASK 0x0003

// Operating modes
#define OPT3001_MODE_SHUTDOWN 0x0000
#define OPT3001_MODE_SINGLE_SHOT 0x2000
#define OPT3001_MODE_CONTINUOUS 0x4000

// Integration times
#define OPT3001_INT_TIME_100MS 0x0000
#define OPT3001_INT_TIME_800MS 0x0800

// Error codes
typedef enum {
    OPT3001_OK,
    OPT3001_ERROR_I2C,
    OPT3001_ERROR_INVALID_DATA,
    OPT3001_ERROR_CONFIG
} opt3001_error_t;

// Function prototypes
typedef struct {
    bool (*i2c_read)(uint8_t dev_addr, uint8_t reg_addr, uint16_t *data);
    bool (*i2c_write)(uint8_t dev_addr, uint8_t reg_addr, uint16_t data);
} opt3001_hal_t;

opt3001_error_t opt3001_init(opt3001_hal_t *hal);
opt3001_error_t opt3001_read_lux(opt3001_hal_t *hal, float *lux);
opt3001_error_t opt3001_configure(opt3001_hal_t *hal, uint16_t configuration);

#endif // OPT3001_H
