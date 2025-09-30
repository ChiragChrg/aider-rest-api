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
