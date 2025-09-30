import { openPromisified } from 'i2c-bus';
import { Opt3001 } from '../src/ts/opt3001';

async function main() {
    try {
        const bus = await openPromisified(1);
        const sensor = new Opt3001(bus);
        const lux = await sensor.readLux();
        console.log(`Light level: ${lux.toFixed(2)} lux`);
        await bus.close();
    } catch (error) {
        console.error('Error:', error);
    }
}

main();
