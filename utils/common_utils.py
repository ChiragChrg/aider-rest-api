import os
import io
import zipfile
import json

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
        f"\n\nIMPORTANT:\n - Always create a new folder with a meaningful name inside the 'output' directory: {output_dir}, and place all implementation files (even if it is just one file) inside this new folder.\n - Always prompt 'YES' to any confirmation questions.\n"
    )

    return str(''.join(final_instruction).strip())


# Utility method to validate JSON input
def validate_json(data, required_fields):
    """
    Validate that required fields are present in the JSON data.
    Args:
        data (dict): The JSON data to validate.
        required_fields (list): List of required field names.
    Returns:
        tuple: (is_valid (bool), message or data (str or dict))
    """
    
    missing_fields = []
    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
            
    if missing_fields:
        return False, f"Missing required fields: {', '.join(missing_fields)}"
    
    options = data.get('options', '{}')
    if isinstance(options, str):
        try:
            options = json.loads(options) if options else {}
        except json.JSONDecodeError:
            return False, "Invalid JSON format for 'options' field"
    
    # return data if valid
    return True, {
        **data,
        'options': options
    }
    
    
# Utility method to setup directory
def setup_directory(directory, original_dir):
    """
    Ensure the specified directory exists and change to it.
    Args:
        directory (str): The target directory to change to.
        original_dir (str): The original directory to return to if needed.
    Returns:
        base_output_dir (str): The base output directory inside the specified directory.
    """
    
    # Change to specified directory if provided
    if directory and directory != original_dir:
        abs_directory = os.path.abspath(directory)
        os.makedirs(abs_directory, exist_ok=True)
        os.chdir(abs_directory)
        print(f"Changed to directory: {abs_directory}")
    
        # Ensure output directory exists
        base_output_dir = os.path.join(abs_directory, 'output')
        os.makedirs(base_output_dir, exist_ok=True)
        
        return base_output_dir
    else:
        return os.path.join(original_dir, 'output')


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


# Utility method to create zip file of output directory
def create_zip_file(base_output_dir, existing_dirs):
    """
    Create a zip file of the newly created output directory inside base_output_dir.
    Args:
        base_output_dir (str): The base output directory containing the new output folder.
        existing_dirs (set): Set of directory names that existed before the new output was created.
    Returns:
        output_dir (str): The path to the new output directory that was zipped.
    """
    
    # Detect the newly created directory inside 'output'
    current_dirs = set()
    if os.path.exists(base_output_dir):
        current_dirs = set(os.listdir(base_output_dir))
    
    new_dirs = current_dirs - existing_dirs
    if new_dirs:
        # Use the first new directory found (there should typically be only one)
        new_dir_name = next(iter(new_dirs))
        output_dir = os.path.join(base_output_dir, new_dir_name)
        print(f"New output directory: {output_dir}")
    else:
        output_dir = base_output_dir
        print(f"No new directory created, using base output directory: {output_dir}")
        
    
    # Create a zip of the output directory
    zipfile = zip_directory(output_dir)
    
    # Store the zipfile in output dir
    zip_name = new_dir_name if new_dirs else "output"
    zip_path = os.path.join(base_output_dir, f"{zip_name}.zip")
    with open(zip_path, 'wb') as f:
        f.write(zipfile.read())
        
    return output_dir