import { promisify } from 'util';
import { I2CBus } from 'i2c-bus';

export class Opt3001 {
    private static readonly I2C_ADDR: number = 0x44;
    
    // Register addresses
    private static readonly REG_RESULT: number = 0x00;
    private static readonly REG_CONFIG: number = 0x01;
    
    // Configuration settings
    static readonly MODE_CONTINUOUS: number = 0x4000;
    static readonly INT_TIME_100MS: number = 0x0000;
    
    private bus: I2CBus;
    private readByte: (addr: number, cmd: number) => Promise<number>;
    private writeByte: (addr: number, cmd: number, byte: number) => Promise<void>;
    private readWord: (addr: number, cmd: number) => Promise<number>;
    private writeWord: (addr: number, cmd: number, word: number) => Promise<void>;
    
    constructor(bus: I2CBus) {
        this.bus = bus;
        this.readByte = promisify(bus.readByte.bind(bus));
        this.writeByte = promisify(bus.writeByte.bind(bus));
        this.readWord = promisify(bus.readWord.bind(bus));
        this.writeWord = promisify(bus.writeWord.bind(bus));
        
        // Configure with default settings
        this.configure(Opt3001.MODE_CONTINUOUS | Opt3001.INT_TIME_100MS);
    }
    
    async readLux(): Promise<number> {
        // Read result register
        const rawResult = await this.readWord(Opt3001.I2C_ADDR, Opt3001.REG_RESULT);
        
        // Extract exponent and mantissa
        const exponent = (rawResult >> 12) & 0x0F;
        const mantissa = rawResult & 0x0FFF;
        
        // Calculate lux according to datasheet formula
        const lux = 0.01 * (1 << exponent) * mantissa;
        return lux;
    }
    
    async configure(configuration: number): Promise<void> {
        await this.writeWord(Opt3001.I2C_ADDR, Opt3001.REG_CONFIG, configuration);
    }
}
