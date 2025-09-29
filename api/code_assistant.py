from flask_restful import Resource
from flask import request
import os
from aider.coders import Coder
from aider.models import Model
from aider.io import InputOutput
from config import Config

class CodeAssistant(Resource):
    def post(self):
        try:
            data = request.get_json()
            
            # Validate required fields
            if not data or 'instruction' not in data:
                return {"error": "Instruction is required"}, 400
            
            instruction = data['instruction']
            files = data.get('files', [])
            directory = data.get('directory', os.getcwd())
            model_name = data.get('model', Config.MODEL)
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
            auto_commits = options.get('auto_commits', True)
            dirty_commits = options.get('dirty_commits', True) 
            dry_run = options.get('dry_run', False)
            
            # Create InputOutput with yes=True for non-interactive mode
            io = InputOutput(
                yes=True,
                pretty=False
            )
            
            # Create model instance
            model = Model(model_name)
            print(f"\nUsing model: {model_name}")

            # Create coder instance
            coder = Coder.create(
                main_model=model,
                fnames=files,
                io=io,
                auto_commits=auto_commits,
                dirty_commits=dirty_commits,
                dry_run=dry_run
            )
            
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