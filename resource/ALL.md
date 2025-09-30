# Specification: OPT3001 Sensor Code Generation

## Objective
Generate reusable, modular, and efficient code to interface with the OPT3001 ambient light sensor across multiple environments.

## Supported Languages
- **C** for embedded microcontrollers (low-level register access, portability).
- **Python** for prototyping and quick testing (using SMBus/I²C libraries).
- **TypeScript/JavaScript** for Node.js applications (e.g., IoT gateways).

## Functional Requirements
1. **Initialization**
   - Configure I²C interface.
   - Set default operating mode (continuous conversions, default integration time).

2. **Reading Data**
   - Read raw register values from the OPT3001.
   - Convert raw values into lux units (per datasheet formula).

3. **Configuration**
   - Allow configurable integration time.
   - Enable threshold-based interrupts.

4. **Error Handling**
   - Handle communication errors (e.g., bus not available, read/write failures).
   - Validate register values.

## Non-Functional Requirements
- **Portability:** Code should be portable across multiple boards/platforms.
- **Maintainability:** Clear modular structure, separated by language.
- **Documentation:** Inline comments and Markdown-based usage guides.
- **Testing:** Mocked I²C layer for unit testing.

## Deliverables
- `opt3001.c` and `opt3001.h` (C driver).
- `opt3001.py` (Python driver).
- `opt3001.ts` (TypeScript library).
- `examples/` folder with sample usage for each language.


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



# Plan: OPT3001 Sensor Code Generation

## Architectural Overview
We will generate code in **layers**, ensuring separation of concerns:
1. **Hardware Abstraction Layer (HAL)**
   - Provides generic I²C read/write interface.
   - Replaced/overridden per platform.
2. **Driver Layer**
   - Implements OPT3001-specific logic (register map, lux conversion).
3. **Application Layer**
   - Exposes simple APIs to end users.
   - Example apps for embedded, Python, and Node.js.

## Directory Structure
/opt3001-driver
├── src/
│ ├── c/
│ │ ├── opt3001.c
│ │ └── opt3001.h
│ ├── python/
│ │ └── opt3001.py
│ └── ts/
│ └── opt3001.ts
├── examples/
│ ├── c_example/
│ ├── python_example/
│ └── ts_example/
├── tests/
├── docs/
└── CMakeLists.txt


## Data Flow
1. **Initialization**
   - User calls init → I²C HAL configures sensor.
2. **Data Read**
   - I²C read (register → raw value).
   - Driver converts raw → lux.
   - API returns lux.
3. **Configuration**
   - User sets integration time or thresholds.
   - Driver writes config registers via I²C.

## Error Handling Strategy
- All low-level errors bubbled up to the API level.
- Consistent error enums/exceptions across languages.
- Logging enabled in Python/TS; lightweight return codes in C.

## Timeline
- **Week 1**: Define register map, create C skeleton.
- **Week 2**: Implement C driver + examples.
- **Week 3**: Implement Python driver + unit tests.
- **Week 4**: Implement TypeScript driver + mock tests.
- **Week 5**: Documentation + polish.

## Deliverable Quality Gates
- ✅ All examples compile and run.
- ✅ Unit tests >80% coverage.
- ✅ Verified outputs against OPT3001 datasheet formulas.
- ✅ API consistency across languages.
