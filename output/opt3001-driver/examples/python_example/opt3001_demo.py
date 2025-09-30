#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'python'))

from opt3001 import OPT3001

def main():
    try:
        sensor = OPT3001(bus_number=1)
        lux = sensor.read_lux()
        print(f"Light level: {lux:.2f} lux")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
