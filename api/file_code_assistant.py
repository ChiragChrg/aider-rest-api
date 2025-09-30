from flask_restful import Resource
from flask import request
import os
from werkzeug.utils import secure_filename
from aider.coders import Coder
from aider.models import Model
from aider.io import InputOutput
from config import Config

class FileCodeAssistant(Resource):
    def post(self):
        try:
            # Handle file uploads
            uploaded_files = request.files.getlist('files')
            instruction = request.form.get('instruction', '')
            directory = request.form.get('directory', os.getcwd())
            model_name = request.form.get('model', Config.MODEL)
            
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
            
            # Create InputOutput for non-interactive mode
            io = InputOutput(yes=True, pretty=False)
            
            # Create model and coder instances
            model = Model(model_name)
            coder = Coder.create(
                main_model=model,
                fnames=saved_files,
                io=io,
                auto_commits=True,
                dirty_commits=True
            )

            # If no instruction provided, set a default one
            instruction = instruction or "Please analyze the uploaded files and implement any requirements or tasks specified in the markdown files."
            instruction += "\n\nGenerate all the files inside the 'output' folder."
            
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