# Specification
- Language: Python 3
- Output: Single file `hello.py`
- Behavior: Print the text `Hello Devs` to stdout.

# Task
- Create a Python script with:
  - Shebang (`#!/usr/bin/env python3`)
  - A `main()` function that prints the message.
  - A standard Python `if __name__ == "__main__": main()` entry point.

# Plan
1. Define `main()` function.
2. Use `print("Hello Devs")`.
3. Add entry point guard to call `main()` when run directly.
4. Save as `hello.py`.

# Example Output
```bash
$ python hello.py
Hello Devs
