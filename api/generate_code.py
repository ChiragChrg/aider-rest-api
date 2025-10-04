import os
import json
from flask import request
from flask_restful import Resource
from aider.coders import ArchitectCoder
from aider.models import Model
from aider.io import InputOutput
from config import Config
from utils.common_utils import build_instruction, zip_directory, setup_directory, create_zip_file
from utils.aider_utils import create_coder, execute_instruction

class GenerateCode(Resource):
    def post(self):
        """
        Generate code based on provided context and instructions.
        """

        original_dir = None
        try:
            data = request.get_json()

             # Validate required fields
            if not data or (not data.get('context') and not data.get('instruction')):
                return {"error": "'context' or 'instruction' is required"}, 400
            
            instruction = data.get('instruction', '')
            context = data.get('context', '')
            code_template = data.get('code_template', '')
            directory = data.get('directory', os.getcwd())
            model_name = data.get('model', Config.MODEL)
            
            # Handle options parameter - it might be a JSON string
            options = data.get('options', {})
            if isinstance(options, str):
                try:
                    options = json.loads(options)
                except json.JSONDecodeError:
                    options = {}
            
            # Get current directory
            original_dir = os.getcwd()
            
            # Ensure directory exists and change to it
            try:
                if directory and directory != original_dir:
                    abs_directory = os.path.abspath(directory)
                    os.makedirs(abs_directory, exist_ok=True)
                    os.chdir(abs_directory)
                    print(f"Changed to directory: {abs_directory}")
            except Exception as e:
                return {"error": f"Failed to change directory: {str(e)}"}, 400
            
            # Configure Aider options with safe defaults
            auto_commits = options.get('auto_commits', False)
            dirty_commits = options.get('dirty_commits', False)
            dry_run = options.get('dry_run', False)

            # Create InputOutput for non-interactive mode with all confirmations disabled
            io = InputOutput(
                yes=True,
                pretty=False
            )
            
            # Create output directory and specify clear instructions
            base_output_dir = os.path.join(original_dir, 'output')
            os.makedirs(base_output_dir, exist_ok=True)
            
            # Get list of existing directories before execution
            existing_dirs = set()
            if os.path.exists(base_output_dir):
                existing_dirs = set(os.listdir(base_output_dir))

            # Create model and coder instances
            try:
                model = Model(model=model_name)

                # Create ArchitectCoder instance
                coder = ArchitectCoder.create(
                    main_model=model,
                    io=io,
                    fnames=[],
                    auto_commits=auto_commits,
                    dirty_commits=dirty_commits,
                    dry_run=dry_run,
                )
            except Exception as e:
                return {"error": f"Failed to initialize model/coder: {str(e)}"}, 500
            
            # Execute the instruction
            try:
                # The line `full_instruction = build_instruction(context, instruction, code_template,
                # base_output_dir)` is calling a function named `build_instruction` with four
                # arguments: `context`, `instruction`, `code_template`, and `base_output_dir`. This
                # function is likely responsible for constructing a complete instruction or command
                # based on the provided context, instruction, code template, and output directory.
                full_instruction = build_instruction(context, instruction, code_template, base_output_dir)
                result = coder.run(full_instruction)
                print(f"Coder execution completed successfully")

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
                    
                # Zip the generated code directory and store in output_dir
                output_dir = create_zip_file(base_output_dir, existing_dirs)
                
            except Exception as e:
                return {"error": f"Failed to execute coder: {str(e)}"}, 500
            
            return {
                "response": result,
                "status": "success",
                "directory": directory,
                "files_processed": [],
                "model_used": model_name,
                "output_directory": output_dir
            }
            
        except Exception as e:           
            print(f"Error in GenerateCode: {str(e)}")
            return {
                "error": str(e),
                "status": "error"
            }, 500
        finally:
            # Return to original directory
            if original_dir:
                os.chdir(original_dir)
                

    #Functional Code Generation Methods
    def generate_code(self, context, instruction, code_template='', directory=None, options=None):
        """
        Function to Generate code based on provided context and instructions.
        
        Args:
            context (str): The context or existing code to consider.
            instruction (str): The instruction for code generation.
            code_template (str, optional): A template to guide code generation. Defaults to ''.
            directory (str, optional): The working directory for code generation. Defaults to None.
            options (dict, optional): Additional options like auto_commits, dirty_commits, dry_run. Defaults to None.
            
        Returns:
            dict: A dictionary containing the response, status, directory, files processed and output directory.
        """
        
        try:
            if context is None and instruction is None:
                raise ValueError("'context' or 'instruction' is required")
            
            # Get model name from config
            model_name = Config.MODEL
            if model_name is None:
                raise ValueError("Model name must be specified in ENV or config")
            
            # Change to specified directory if provided
            original_dir = os.getcwd()
            base_output_dir =setup_directory(directory, original_dir)
            
            # Configure Aider options
            if options is None:
                options = {
                    'auto_commits': False,
                    'dirty_commits': False,
                    'dry_run': False
                }
            else:
                options.setdefault('auto_commits', False)
                options.setdefault('dirty_commits', False)
                options.setdefault('dry_run', False)
            
            # Get list of existing directories before execution
            existing_dirs = set()
            if os.path.exists(base_output_dir):
                existing_dirs = set(os.listdir(base_output_dir))
            
            # Create model and coder instances
            coder = create_coder(
                model_name=model_name,
                auto_commits=options['auto_commits'],
                dirty_commits=options['dirty_commits'],
                dry_run=options['dry_run']
            )
            
            # Build complete instruction
            full_instruction = build_instruction(context,instruction,code_template, base_output_dir)
            
            # Execute the instruction
            result = execute_instruction(coder, full_instruction)
            
            # Create zip file of the new output directory
            output_dir = create_zip_file(base_output_dir, existing_dirs)
            
            return {
                "response": result,
                "status": 201,
                "directory": directory,
                "files_processed": [],
                "model_used": model_name,
                "output_directory": output_dir
            }
        
        except ValueError as e:
            return {"ValueError": str(e)}, 400
        
        except Exception as e:           
            print(f"Error in GenerateCode: {str(e)}")
            return {"error": str(e), "status": "error"}, 500
        finally:
            # Return to original directory
            if original_dir:
                os.chdir(original_dir)
            
