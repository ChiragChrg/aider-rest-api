import os
from flask import request
from flask_restful import Resource
from config import Config
from utils.common_utils import (
    validate_json,
    setup_directory,
    build_instruction,
    create_zip_file,
)
from utils.aider_utils import create_coder, execute_instruction


class CodeAssistant(Resource):
    def post(self):
        """
        Route to handle code assistance requests.
        Expects JSON payload with:
        - instruction (str): The instruction to execute.
        - files (list, optional): List of filenames to be read-only.
        - directory (str, optional): Directory to operate in.
        - model (str, optional): Model name to use.
        - options (dict, optional): Additional options like auto_commits, dirty_commits, dry_run.
        Returns:
            dict: Response containing execution result, status, and output directory info.
        """

        original_dir = None
        try:
            payload = request.get_json()

            # Validate required fields
            required_fields = ["instruction"]
            is_valid, data = validate_json(payload, required_fields)

            # Return error if validation fails
            if not is_valid:
                raise ValueError(data)

            # Ensure data is a dictionary
            if not isinstance(data, dict):
                raise ValueError("Validated data is not a dictionary")

            # Extract fields from the validated data
            instruction = data["instruction"]
            files = data.get("files", [])
            directory = data.get("directory", os.getcwd())
            model_name = data.get("model", Config.MODEL)
            options = data.get("options", {})

            # Change to specified directory if provided
            original_dir = os.getcwd()
            base_output_dir = setup_directory(directory, original_dir)

            # Configure Aider options
            auto_commits = options.get("auto_commits", False)
            dirty_commits = options.get("dirty_commits", False)
            dry_run = options.get("dry_run", False)

            # Get list of existing directories before execution
            existing_dirs = set()
            if os.path.exists(base_output_dir):
                existing_dirs = set(os.listdir(base_output_dir))

            # Create model and coder instances
            coder = create_coder(
                model_name=model_name,
                files=files,
                auto_commits=auto_commits,
                dirty_commits=dirty_commits,
                dry_run=dry_run,
            )

            # Build complete instruction
            full_instruction = build_instruction(
                None, instruction, None, base_output_dir
            )

            # Execute the instruction
            result = execute_instruction(coder, full_instruction)

            # Create zip file of the new output directory
            output_dir = create_zip_file(base_output_dir, existing_dirs)

            return {
                "response": result,
                "status": 201,
                "directory": directory,
                "files_processed": [os.path.basename(f) for f in files],
                "model_used": model_name,
                "output_directory": output_dir,
            }

        except ValueError as e:
            return {"ValueError": str(e)}, 400

        except Exception as e:
            print(f"Error in CodeAssistant: {str(e)}")
            return {"error": str(e), "status": "error"}, 500
        finally:
            # Return to original directory
            if original_dir:
                os.chdir(original_dir)
