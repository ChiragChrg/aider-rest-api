import os
from flask import request
from flask_restful import Resource
from werkzeug.utils import secure_filename
from aider.coders import Coder
from aider.models import Model
from aider.io import InputOutput
from config import Config

class FileCodeAssistant(Resource):
    def post(self):
        """
        The `post` function handles file uploads, processes the uploaded files using Aider, and returns
        the result along with relevant information.
        
        Returns:
          The code snippet is a Python function that handles file uploads, processes the uploaded files
        using a specified model and coder, and returns a response containing information about the
        processing status, directory used, files processed, and the model used. If an error occurs
        during the process, it returns an error message along with a status code.
        """
        try:
            # Handle file uploads
            uploaded_files = request.files.getlist('files')
            instruction = request.form.get('instruction', '')
            directory = request.form.get('directory', os.getcwd())
            model_name = request.form.get('model', Config.MODEL)
            aider_mode_prefix = request.form.get('aider_mode_prefix', '/architect')
            options = request.form.get('options', {})
            
            # Validate required fields
            if not uploaded_files:
                return {"error": "At least one file must be uploaded"}, 400
            
            # Save uploaded files
            saved_files = []
            original_dir = os.getcwd()
            
            if directory:
                abs_directory = os.path.abspath(directory)
                os.makedirs(abs_directory, exist_ok=True)
                os.chdir(abs_directory)
            
            for file in uploaded_files:
                if file.filename:
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(os.getcwd(), filename)
                    file.save(file_path)
                    saved_files.append(file_path)
            
            # Configure Aider options
            auto_commits = options.get('auto_commits', False)
            dirty_commits = options.get('dirty_commits', False) 
            dry_run = options.get('dry_run', False)

            # Create InputOutput for non-interactive mode
            io = InputOutput(yes=True, pretty=False)
            
            # Create model and coder instances
            model = Model(
                model=model_name,
                editor_model=model_name
            )
            coder = Coder.create(
                main_model=model,
                fnames=saved_files,
                io=io,
                auto_commits=auto_commits,
                dirty_commits=dirty_commits,
                dry_run=dry_run,
            )

            # If no instruction provided, set a default one
            instruction = instruction or "Please analyze the uploaded files and implement any requirements or tasks specified in the markdown files."

            # Define Aider mode based on prefix
            if aider_mode_prefix.startswith("/") and not instruction.startswith(f"/{aider_mode_prefix}"):
                instruction = f"{aider_mode_prefix} {instruction}"
            elif not aider_mode_prefix.startswith("/") and not instruction.startswith(aider_mode_prefix):
                instruction = f"/{aider_mode_prefix} {instruction}"

            # Specify to generate files in 'output' folder
            instruction += "\n\n Create a new directory for the generated files and save all the files inside the existing 'output' folder."
            
            # Execute the instruction (if provided) or let aider process the uploaded files
            result = coder.run(instruction)
            
            # Return to original directory
            os.chdir(original_dir)
            
            return {
                "response": result,
                "status": "success",
                "directory": directory,
                "files_processed": saved_files,
                "model_used": model_name
            }
            
        except Exception as e:
            if 'original_dir' in locals():
                os.chdir(original_dir)
            
            return {
                "error": str(e),
                "status": "error"
            }, 500