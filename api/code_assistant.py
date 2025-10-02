import os
from flask import request
from flask_restful import Resource
from aider.coders import Coder
from aider.models import Model
from aider.io import InputOutput
from config import Config

class CodeAssistant(Resource):
    def post(self):
        """
        This Python function processes a POST request by executing an instruction with specified options
        and returning the result along with relevant information.
        
        Returns:
          The code snippet is a Python method for handling a POST request. It receives JSON data,
        validates required fields, sets various parameters based on the input data, configures options,
        creates instances of classes, executes a given instruction using a coder instance, and returns a
        response object containing the result of the instruction execution along with other relevant
        information such as the status, directory used, files processed, and model used
        """
        try:
            data = request.get_json()

            # Validate required fields
            if not data or 'instruction' not in data:
                return {"error": "Instruction is required"}, 400
            
            instruction = data['instruction']
            files = data.get('files', [])
            directory = data.get('directory', os.getcwd())
            model_name = data.get('model', Config.MODEL)
            aider_mode_prefix = data.get('aider_mode_prefix', '/code')
            options = data.get('options', {})
            
            # Change to specified directory if provided
            original_dir = os.getcwd()
            if directory:
                # Convert to absolute path and create if it doesn't exist
                abs_directory = os.path.abspath(directory)
                os.makedirs(abs_directory, exist_ok=True)
                os.chdir(abs_directory)
                print(f"Changed to directory: {abs_directory}")
            
            # Configure Aider options
            auto_commits = options.get('auto_commits', False)
            dirty_commits = options.get('dirty_commits', False) 
            dry_run = options.get('dry_run', False)
            
            # Create InputOutput with yes=True for non-interactive mode
            io = InputOutput(
                yes=True,
                pretty=False
            )
            
            # Create model instance
            model = Model(
                model=model_name,
                editor_model=model_name
            )
            print(f"\nUsing model: {model_name}")

            # Create coder instance
            coder = Coder.create(
                main_model=model,
                fnames=files,
                io=io,
                auto_commits=auto_commits,
                dirty_commits=dirty_commits,
                dry_run=dry_run,
                
            )

            # Define Aider mode based on prefix
            if aider_mode_prefix.startswith("/") and not instruction.startswith(f"/{aider_mode_prefix}"):
                instruction = f"{aider_mode_prefix} {instruction}"
            elif not aider_mode_prefix.startswith("/") and not instruction.startswith(aider_mode_prefix):
                instruction = f"/{aider_mode_prefix} {instruction}"
            
            # Specify to generate files in 'output' folder
            instruction += "\n\n Create a new directory for the generated files and save all the files inside the existing 'output' folder."

            # Execute the instruction
            result = coder.run(instruction)
            
            # Return to original directory
            os.chdir(original_dir)
            
            return {
                "response": result,
                "status": "success",
                "directory": directory,
                "files_processed": files,
                "model_used": model_name
            }
            
        except Exception as e:
            # Ensure we return to original directory on error
            if 'original_dir' in locals():
                os.chdir(original_dir)
            
            return {
                "error": str(e),
                "status": "error"
            }, 500