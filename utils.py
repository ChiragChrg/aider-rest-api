import os
import io
import zipfile

# Utility method to build instruction
def build_instruction(context:str, instruction:str, code_template:str, output_dir:str):
    """
    Build a comprehensive instruction string for the coder.
    Ensures critical rules are included and formats the instruction properly.
    Args:
        context (str): The context for the code generation.
        instruction (str): The main instruction for the coder.
        code_template (str): Optional code template to guide the generation.
        output_dir (str): The directory where output files should be created.
    Returns:
        str: The final instruction string.
    """
    final_instruction = []

    if context:
        final_instruction.append(f"CONTEXT:\n{context}\n\n")
    if instruction:
        strict_instruction = (
                f"{instruction}\n\n"
                "CRITICAL RULES:\n"
                "- Do not output any TODO placeholders or comments indicating incomplete code.\n"
                "- Do not leave functions, classes, methods, or modules unimplemented.\n"
                "- Always provide complete, working, production-ready code.\n"
                "- Do not return partial implementations or stubbed logic.\n"
                "- Validate and self-check the code before returning:\n"
                "  * Ensure there are no typos in identifiers or keywords.\n"
                "  * Ensure there are no syntax errors.\n"
                "  * Ensure that any type constraints, parameterized types, or contracts are satisfied.\n"
                "    For dynamically typed languages, ensure runtime checks or validations exist where needed.\n"
                "- Preserve consistency and correctness across all related constructs (types, functions, modules, interfaces, etc.).\n"
                "- If full implementation is not possible, stop and explain why instead of returning stubs or partial code.\n"
            )
        final_instruction.append(f"INSTRUCTION:\n{strict_instruction}\n\n")
    if code_template:
        final_instruction.append(f"CODE TEMPLATE:\n{code_template}\n\n")

    # Specify output directory
    final_instruction.append(
        f"\n\nIMPORTANT: Create all new implementation files in a new folder with a meaningful name "
        f"related to the implementation inside the 'output' directory: {output_dir}."
    )

    return str(''.join(final_instruction).strip())


# Utility method to zip a directory
def zip_directory(directory_path: str):
    """
    Zip the contents of a directory and return as an in-memory file.
    Args:
        directory_path (str): The path to the directory to be zipped.
    Returns:
        io.BytesIO: An in-memory bytes buffer containing the zip file.
    """

    memory_file = io.BytesIO()
    
    # Create a zip file in memory
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Walk the directory
        for root, _, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                
                # Add file to the zip file with relative path
                arcname = os.path.relpath(file_path, directory_path)
                zipf.write(file_path, arcname)
                
    memory_file.seek(0)
    
    return memory_file