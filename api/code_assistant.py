import os
import json
from flask import request
from flask_restful import Resource
from aider.coders import Coder, ArchitectCoder
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
            # aider_mode_prefix = data.get('aider_mode_prefix', '/code') # Always use /architect for now

            # Handle options parameter - it might be a JSON string
            options_param = data.get('options', '{}')
            try:
                if isinstance(options_param, str):
                    options = json.loads(options_param) if options_param else {}
                else:
                    options = options_param
            except json.JSONDecodeError:
                options = {}
            
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
                pretty=False,
                chat_history_file=None,
                input_history_file=None,
            )

            # Create output directory and specify clear instructions
            output_dir = os.path.join(os.getcwd(), 'output')
            os.makedirs(output_dir, exist_ok=True)
            
            # Create model and coder instances
            try:
                model = Model(model=model_name)

                # if aider_mode_prefix in ['/architect', 'architect']:
                coder = ArchitectCoder.create(
                    main_model=model,
                    fnames=[],  
                    read_only_fnames=files,
                    io=io,
                    auto_commits=auto_commits,
                    dirty_commits=dirty_commits,
                    dry_run=dry_run,
                )
                # else:
                #     coder = Coder.create(
                #         main_model=model,
                #         fnames=[],
                #         read_only_fnames=files,
                #         io=io,
                #         auto_commits=auto_commits,
                #         dirty_commits=dirty_commits,
                #         dry_run=dry_run,
                #     )
            except Exception as e:
                if original_dir:
                    os.chdir(original_dir)
                return {"error": f"Failed to initialize model/coder: {str(e)}"}, 500
            
            # Specify to generate files in 'output' folder
            instruction += f"\n\nIMPORTANT: Create all new implementation files in a new folder with meaningful name related to the implementation inside the 'output' directory: {output_dir}."

            # Execute the instruction
            try:
                result = coder.run(instruction)
                print(f"Coder execution completed successfully")
            except Exception as e:
                if original_dir:
                    os.chdir(original_dir)
                return {"error": f"Failed to execute coder: {str(e)}"}, 500
            
            # Return to original directory
            if original_dir:
                os.chdir(original_dir)
            
            return {
                "response": result,
                "status": "success",
                "directory": directory,
                "files_processed": [os.path.basename(f) for f in files],
                "model_used": model_name,
                "output_directory": output_dir
            }
            
        except Exception as e:
            # Ensure we return to original directory on error
            if 'original_dir' in locals():
                os.chdir(original_dir)
            
            return {
                "error": str(e),
                "status": "error"
            }, 500