# Task: OPT3001 Sensor Code Generation

## Primary Goal
Develop a cross-platform driver/library for the OPT3001 ambient light sensor that can be reused in embedded, prototyping, and gateway-level projects.

## Tools & Stack
- **Embedded C**
  - Compiler: `gcc` or `arm-none-eabi-gcc`
  - Build system: `CMake`
  - I²C communication via `HAL` or `bare-metal` implementations.

- **Python**
  - Python 3.10+
  - Libraries: `smbus2` for I²C
  - Virtual environment with `pytest` for testing.

- **TypeScript (Node.js)**
  - Runtime: Node.js 20+
  - Libraries: `i2c-bus`
  - Bundler: `tsc` (TypeScript compiler)
  - Tests with `jest`.

## Tasks Breakdown
1. **Setup**
   - Define repository structure (`/src`, `/examples`, `/tests`, `/docs`).
   - Configure build/test workflows.

2. **C Driver**
   - Implement `opt3001_init()`, `opt3001_read_lux()`, `opt3001_configure()`.
   - Provide `example/main.c`.

3. **Python Driver**
   - Implement `OPT3001` class with `read_lux()`, `configure()`.
   - Provide `examples/opt3001_demo.py`.

4. **TypeScript Driver**
   - Implement `Opt3001` class with async methods `readLux()`, `configure()`.
   - Provide `examples/opt3001_demo.ts`.

5. **Testing**
   - Unit tests for all 3 environments.
   - Mock I²C interface for offline testing.

6. **Documentation**
   - Auto-generate API docs from comments.
   - Provide Markdown guides (`USAGE.md`, `DEVELOPER_GUIDE.md`).

## Constraints
- Code should match datasheet formulas exactly.
- Must support both synchronous and asynchronous read patterns where possible.
