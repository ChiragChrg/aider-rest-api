#include <stdio.h>
#include "opt3001.h"

// Mock I2C functions for example
bool i2c_read(uint8_t dev_addr, uint8_t reg_addr, uint16_t *data) {
    // In a real implementation, this would read from the I2C bus
    // For this example, we'll just return a fixed value
    *data = 0xC410; // Example reading that should give ~100 lux
    return true;
}

bool i2c_write(uint8_t dev_addr, uint8_t reg_addr, uint16_t data) {
    // In a real implementation, this would write to the I2C bus
    printf("Writing 0x%04X to register 0x%02X\n", data, reg_addr);
    return true;
}

int main() {
    opt3001_hal_t hal = {
        .i2c_read = i2c_read,
        .i2c_write = i2c_write
    };
    
    if (opt3001_init(&hal) != OPT3001_OK) {
        printf("Failed to initialize OPT3001\n");
        return 1;
    }
    
    float lux;
    if (opt3001_read_lux(&hal, &lux) == OPT3001_OK) {
        printf("Light level: %.2f lux\n", lux);
    } else {
        printf("Failed to read light level\n");
    }
    
    return 0;
}
