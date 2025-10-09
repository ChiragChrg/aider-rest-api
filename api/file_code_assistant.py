import os
import json
import tempfile
from flask import request
from flask_restful import Resource
from werkzeug.utils import secure_filename
from aider.coders import Coder, ArchitectCoder
from aider.models import Model
from aider.io import InputOutput
from config import Config


class FileCodeAssistant(Resource):
    def post(self):
        """
        The `post` function handles file uploads, processes the uploaded files using Aider, and returns
        the result along with relevant information.
        """
        original_dir = None
        temp_files = []
        try:
            # Handle file uploads
            uploaded_files = request.files.getlist("files")
            instruction = request.form.get("instruction", "")
            directory = request.form.get("directory", os.getcwd())
            model_name = request.form.get("model", Config.MODEL)
            # aider_mode_prefix = request.form.get('aider_mode_prefix', '/architect') # Always use /architect for now

            # Handle options parameter - it might be a JSON string
            options_param = request.form.get("options", "{}")
            try:
                if isinstance(options_param, str):
                    options = json.loads(options_param) if options_param else {}
                else:
                    options = options_param
            except json.JSONDecodeError:
                options = {}

            # Validate required fields
            if not uploaded_files:
                return {"error": "At least one file must be uploaded"}, 400

            # Create temporary files for Aider to read
            original_dir = os.getcwd()

            # Ensure directory exists and change to it
            try:
                if directory and directory != os.getcwd():
                    abs_directory = os.path.abspath(directory)
                    os.makedirs(abs_directory, exist_ok=True)
                    os.chdir(abs_directory)
                    print(f"Changed to directory: {abs_directory}")
            except Exception as e:
                return {"error": f"Failed to change directory: {str(e)}"}, 400

            # Create temporary files for Aider reference only
            for file in uploaded_files:
                if file.filename:
                    # Create temporary file
                    temp_file = tempfile.NamedTemporaryFile(
                        mode="w+b",
                        suffix=f"_{secure_filename(file.filename)}",
                        delete=False,
                    )
                    file.save(temp_file.name)
                    temp_files.append(temp_file.name)
                    print(f"Created temporary reference file: {temp_file.name}")

            if not temp_files:
                if original_dir:
                    os.chdir(original_dir)
                return {"error": "No files were successfully processed"}, 400

            # Configure Aider options with safe defaults
            auto_commits = options.get("auto_commits", False)
            dirty_commits = options.get("dirty_commits", False)
            dry_run = options.get("dry_run", False)

            # Create InputOutput for non-interactive mode with all confirmations disabled
            io = InputOutput(yes=True, pretty=False)

            # Create output directory and specify clear instructions
            output_dir = os.path.join(os.getcwd(), "output")
            os.makedirs(output_dir, exist_ok=True)

            # Create model and coder instances
            try:
                model = Model(model=model_name)

                # if aider_mode_prefix in ['/architect', 'architect']:
                coder = ArchitectCoder.create(
                    main_model=model,
                    io=io,
                    fnames=[],  # No files to edit
                    read_only_fnames=temp_files,  # Reference files only
                    auto_commits=auto_commits,
                    dirty_commits=dirty_commits,
                    dry_run=dry_run,
                )
                # else:
                #     coder = Coder.create(
                #         main_model=model,
                #         fnames=[],  # No files to edit
                #         read_only_fnames=temp_files,  # Reference files only
                #         io=io,
                #         auto_commits=auto_commits,
                #         dirty_commits=dirty_commits,
                #         dry_run=dry_run,
                #     )
            except Exception as e:
                # Clean up temp files
                for temp_file in temp_files:
                    try:
                        os.unlink(temp_file)
                    except:
                        pass
                if original_dir:
                    os.chdir(original_dir)
                return {"error": f"Failed to initialize model/coder: {str(e)}"}, 500

            # If no instruction provided, set a default one
            if not instruction:
                instruction = "Please analyze the uploaded specification files and implement the requirements."

            # Modify instruction to specify output location and prevent file modification
            instruction += f"\n\nIMPORTANT: Create all new implementation files in a new folder with meaningful name related to the implementation inside the 'output' directory: {output_dir}."

            # Execute the instruction
            try:
                result = coder.run(instruction)
                print(f"Coder execution completed successfully")
            except Exception as e:
                if original_dir:
                    os.chdir(original_dir)
                return {"error": f"Failed to execute coder: {str(e)}"}, 500
            finally:
                # Clean up temporary files
                for temp_file in temp_files:
                    try:
                        os.unlink(temp_file)
                        print(f"Cleaned up temporary file: {temp_file}")
                    except Exception as e:
                        print(f"Failed to clean up {temp_file}: {e}")

            # Return to original directory
            if original_dir:
                os.chdir(original_dir)

            return {
                "response": result,
                "status": "success",
                "directory": directory,
                "files_processed": [os.path.basename(f) for f in temp_files],
                "model_used": model_name,
                "output_directory": output_dir,
            }

        except Exception as e:
            # Clean up temporary files on error
            for temp_file in temp_files:
                try:
                    os.unlink(temp_file)
                except:
                    pass

            # Ensure we return to original directory on any error
            if original_dir and os.path.exists(original_dir):
                try:
                    os.chdir(original_dir)
                except:
                    pass  # If we can't change back, at least don't crash

            print(f"Error in FileCodeAssistant: {str(e)}")
            return {"error": str(e), "status": "error"}, 500
