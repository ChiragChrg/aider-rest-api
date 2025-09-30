import smbus2
import time

class OPT3001:
    # I2C address
    I2C_ADDR = 0x44
    
    # Register addresses
    REG_RESULT = 0x00
    REG_CONFIG = 0x01
    REG_LOW_LIMIT = 0x02
    REG_HIGH_LIMIT = 0x03
    REG_MANUFACTURER_ID = 0x7E
    REG_DEVICE_ID = 0x7F
    
    # Configuration settings
    MODE_SHUTDOWN = 0x0000
    MODE_SINGLE_SHOT = 0x2000
    MODE_CONTINUOUS = 0x4000
    
    INT_TIME_100MS = 0x0000
    INT_TIME_800MS = 0x0800
    
    def __init__(self, bus_number=1):
        self.bus = smbus2.SMBus(bus_number)
        self.configure(self.MODE_CONTINUOUS | self.INT_TIME_100MS)
    
    def read_lux(self):
        """Read the light level in lux"""
        # Read result register
        data = self.bus.read_i2c_block_data(self.I2C_ADDR, self.REG_RESULT, 2)
        raw_result = (data[0] << 8) | data[1]
        
        # Extract exponent and mantissa
        exponent = (raw_result >> 12) & 0x0F
        mantissa = raw_result & 0x0FFF
        
        # Calculate lux according to datasheet formula
        lux = 0.01 * (1 << exponent) * mantissa
        return lux
    
    def configure(self, configuration):
        """Configure the sensor with the given settings"""
        # Split 16-bit configuration into two bytes
        msb = (configuration >> 8) & 0xFF
        lsb = configuration & 0xFF
        self.bus.write_i2c_block_data(self.I2C_ADDR, self.REG_CONFIG, [msb, lsb])
    
    def __del__(self):
        self.bus.close()
