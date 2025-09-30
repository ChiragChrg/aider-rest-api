import unittest
from unittest.mock import Mock, patch
from src.python.opt3001 import OPT3001

class TestOPT3001(unittest.TestCase):
    @patch('smbus2.SMBus')
    def test_read_lux(self, mock_smbus):
        # Mock the I2C bus
        mock_bus = Mock()
        mock_bus.read_i2c_block_data.return_value = [0xC4, 0x10]
        mock_smbus.return_value = mock_bus
        
        sensor = OPT3001(bus_number=1)
        lux = sensor.read_lux()
        
        # Verify the calculation
        self.assertAlmostEqual(lux, 100.0, delta=0.1)
        
        # Verify I2C was called correctly
        mock_bus.read_i2c_block_data.assert_called_with(0x44, 0x00, 2)

if __name__ == '__main__':
    unittest.main()
