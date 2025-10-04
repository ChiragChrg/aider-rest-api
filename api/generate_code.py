import os
from flask import request
from flask_restful import Resource
from config import Config
from utils.common_utils import build_instruction, setup_directory, create_zip_file, validate_json
from utils.aider_utils import create_coder, execute_instruction

class GenerateCode(Resource):
    def post(self):
        """
        Generate code based on provided context and instructions.
        """

        original_dir = None
        try:
            payload = request.get_json()
            
            # Validate required fields
            required_fields = ['context','instruction']
            is_valid, data = validate_json(payload, required_fields)
            
            # Return error if validation fails
            if not is_valid:
                raise ValueError(data)
            
            # Extract parameters from validated data
            instruction = data.get('instruction', '')
            context = data.get('context', '')
            code_template = data.get('code_template', '')
            directory = data.get('directory', os.getcwd())
            model_name = data.get('model', Config.MODEL)
            options = data.get('options', {})
            
            # Configure Aider options with safe defaults
            auto_commits = options.get('auto_commits', False)
            dirty_commits = options.get('dirty_commits', False)
            dry_run = options.get('dry_run', False)

            # Change to specified directory if provided
            original_dir = os.getcwd()
            base_output_dir =setup_directory(directory, original_dir)
            
            # Get list of existing directories before execution
            existing_dirs = set()
            if os.path.exists(base_output_dir):
                existing_dirs = set(os.listdir(base_output_dir))
            
              # Create model and coder instances
            coder = create_coder(
                model_name=model_name,
                auto_commits=auto_commits,
                dirty_commits=dirty_commits,
                dry_run=dry_run
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
            
            # Change to specified directory if provided
            original_dir = os.getcwd()
            base_output_dir =setup_directory(directory, original_dir)
            
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
            
