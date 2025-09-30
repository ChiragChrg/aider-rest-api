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