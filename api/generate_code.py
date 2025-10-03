import os
import json
from flask import request
from flask_restful import Resource
from werkzeug.utils import secure_filename
from aider.coders import ArchitectCoder
from aider.models import Model
from aider.io import InputOutput
from config import Config

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
            output_dir = os.path.join(original_dir, 'output')
            os.makedirs(output_dir, exist_ok=True)
            
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
                full_instruction = self.build_instruction(context, instruction, code_template, output_dir)
                result = coder.run(full_instruction)
                print(f"Coder execution completed successfully")
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

    def build_instruction(self, context, instruction, code_template, output_dir):
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

        return ''.join(final_instruction).strip()