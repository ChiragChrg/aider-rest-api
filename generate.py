from api.generate_code import GenerateCode

# function print hello world
def generate():   
    context = "We are building a small modular Python utility package for basic data processing and logging. The system should include a main entry point that orchestrates operations, several utility modules for handling different concerns, and a testing setup to ensure correctness. The design should be lightweight, extensible, and follow Python best practices with clean separation of responsibilities.\n\nThe package will contain functions for string manipulation, numerical computations, and logging. It should include minimal error handling for invalid inputs and provide clear log messages for debugging and usage tracking.\n\nThe project must be structured in a way that scales easily as new features are added."
    instruction = "Generate a fully functional implementation of the described Python project. Follow these strict rules:\n\nCRITICAL RULES:\n- Maintain the exact directory and file structure defined below.\n- Implement all files completely — do not output placeholders, comments like TODO, or partial logic.\n- Validate all input parameters and handle errors gracefully.\n- Follow Pythonic conventions and PEP8 formatting.\n- Include meaningful logging in key parts of the logic.\n- Include simple unit tests that validate all core utilities.\n- Ensure there are no typos, syntax errors, or broken imports.\n- The final output should represent a working, production-ready codebase.\n- If full implementation is not possible, stop and explain why instead of returning incomplete files."
    code_template = ""

    try:
        response = GenerateCode().generate_code(context, instruction, code_template)
        print("\nCode generation response: \n", response)
    except Exception as e:
        print(f"Error generating code: {str(e)}")
        

# run on initialization
if __name__ == "__main__":
    generate()
