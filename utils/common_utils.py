import os
import io
import zipfile
import json
import requests


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
                "- Always prompt 'YES' to any confirmation questions.\n"
            )
        final_instruction.append(f"INSTRUCTION:\n{strict_instruction}\n\n")
    if code_template:
        final_instruction.append(f"CODE TEMPLATE:\n{code_template}\n\n")

    # Specify output directory
    final_instruction.append(
        f"\n\nIMPORTANT: Always create a new folder with a meaningful name inside the 'output' directory: {output_dir}, and place all implementation files (even if it is just one file) inside this new folder.\n"
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
    Only creates zip if there are actually new files created.
    Args:
        base_output_dir (str): The base output directory containing the new output folder.
        existing_dirs (set): Set of directory names that existed before the new output was created.
    Returns:
        output_dir (str): The path to the new output directory.
        zipfile (io.BytesIO or None): The in-memory zip file if created, else None.
        zip_path (str or None): The path where the zip file is stored, else None.
    """
    
    # Detect the newly created directory inside 'output'
    current_dirs = set()
    if os.path.exists(base_output_dir):
        current_dirs = set(os.listdir(base_output_dir))
    
    new_dirs = current_dirs - existing_dirs
    
    zipfile = None
    if new_dirs:
        # Use the first new directory found (there should typically be only one)
        new_dir_name = next(iter(new_dirs))
        output_dir = os.path.join(base_output_dir, new_dir_name)
        print(f"New output directory: {output_dir}")
        
        # Check if the new directory actually contains files
        if directory_has_files(output_dir):
            # Create a zip of the output directory
            zipfile = zip_directory(output_dir)
            
            # Store the zipfile in output dir
            zip_path = get_unique_filename(base_output_dir, new_dir_name, ".zip")
            with open(zip_path, 'wb') as f:
                f.write(zipfile.read())
            
            print(f"Created zip file: {zip_path}")
            return {
                "output_dir": output_dir,
                "zipfile": zipfile,
                "zip_path": zip_path,
                "status": True
            }
        else:
            print(f"New directory created but contains no files, skipping zip creation")
            return {
                "output_dir": output_dir,
                "zipfile": None,
                "zip_path": None,
                "status": False
            }
    else:
        print(f"No new directory created, no zip file needed")
        return {
            "output_dir": base_output_dir,
            "zipfile": None,
            "zip_path": None,
            "status": False
        }
    
        
# Utility method to check if directory has files  
def directory_has_files(directory_path):
    """
    Check if a directory contains any files (recursively).
    Args:
        directory_path (str): Path to the directory to check.
    Returns:
        bool: True if directory contains files, False otherwise.
    """
    if not os.path.exists(directory_path):
        return False
    
    for root, dirs, files in os.walk(directory_path):
        if files:  # If any files are found
            return True
    
    return False


# Utility method to get a unique filename
def get_unique_filename(directory, base_name, extension):
    """
    Generate a unique filename by adding incremental numbers if duplicates exist.
    Args:
        directory (str): The directory where the file will be created.
        base_name (str): The base name for the file (without extension).
        extension (str): The file extension (including the dot).
    Returns:
        str: A unique file path.
    """
    original_path = os.path.join(directory, f"{base_name}{extension}")
    
    # If the file doesn't exist, return the original path
    if not os.path.exists(original_path):
        return original_path
    
    # Find the next available number
    counter = 1
    while True:
        new_name = f"{base_name}({counter}){extension}"
        new_path = os.path.join(directory, new_name)
        
        if not os.path.exists(new_path):
            return new_path
        
        counter += 1
        
        # Safety check to prevent infinite loop
        if counter > 9999:
            raise RuntimeError(f"Too many duplicate files for base name: {base_name}")
        

# Utility to upload zip file to cloud storage
def upload_to_cloud(zipFile, zipName):
    """
    Upload the zip to backend endpoint using POST request.
    Args:
        zipFile (io.BytesIO): The in-memory zip file to upload.
        zipName (str): The name of the zip file.
    Returns:
        None
    """
    
    try:        
        files = {
            'file': (zipName, zipFile, 'application/zip')
        }
        
        base_url = os.getenv('BACKEND_URL')
        backend_url = f"{base_url}/api/v1/files/zip/upload"
        
        response = requests.post(backend_url, files=files)
        
        if response.status_code == 201:
            print(f"Successfully uploaded {zipName} to cloud storage.")
            print(f"Response: {response.json()}")
        else:
            print(f"Failed to upload {zipName}. Status code: {response.status_code}, Response: {response.text}")
    
    except Exception as e:
        print(f"Error uploading {zipName} to cloud storage: {str(e)}")