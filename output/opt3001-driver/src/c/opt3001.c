#include "opt3001.h"
#include <math.h>

opt3001_error_t opt3001_init(opt3001_hal_t *hal) {
    if (hal == NULL || hal->i2c_read == NULL || hal->i2c_write == NULL) {
        return OPT3001_ERROR_CONFIG;
    }
    
    // Set default configuration: continuous conversion, 100ms integration time
    uint16_t config = OPT3001_MODE_CONTINUOUS | OPT3001_INT_TIME_100MS;
    return opt3001_configure(hal, config);
}

opt3001_error_t opt3001_read_lux(opt3001_hal_t *hal, float *lux) {
    if (hal == NULL || lux == NULL) {
        return OPT3001_ERROR_CONFIG;
    }
    
    // Read result register
    uint16_t raw_result;
    if (!hal->i2c_read(OPT3001_I2C_ADDR, OPT3001_REG_RESULT, &raw_result)) {
        return OPT3001_ERROR_I2C;
    }
    
    // Extract exponent and mantissa
    uint16_t exponent = (raw_result >> 12) & 0x0F;
    uint16_t mantissa = raw_result & 0x0FFF;
    
    // Calculate lux according to datasheet formula
    *lux = 0.01 * (1 << exponent) * mantissa;
    
    return OPT3001_OK;
}

opt3001_error_t opt3001_configure(opt3001_hal_t *hal, uint16_t configuration) {
    if (hal == NULL) {
        return OPT3001_ERROR_CONFIG;
    }
    
    // Write to configuration register
    if (!hal->i2c_write(OPT3001_I2C_ADDR, OPT3001_REG_CONFIG, configuration)) {
        return OPT3001_ERROR_I2C;
    }
    
    return OPT3001_OK;
}
