from api.generate_code import GenerateCode

# Function to generate code based on context, instruction, and template
def generate():   
    context = "You are to generate a small Python utility project."
    instruction = "Create a few Python files under src/ and tests/ that print hello."
    code_template = "src/main.py, src/utils/helpers.py, tests/test_helpers.py"

    try:
        response = GenerateCode().generate_code(context, instruction, code_template)
        print("\nCode generation response: \n", response)
    except Exception as e:
        print(f"Error generating code: {str(e)}")
        

if __name__ == "__main__":
    generate()
