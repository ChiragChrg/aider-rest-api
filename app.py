from flask import Flask, jsonify
from flask_restful import Api
from dotenv import load_dotenv

from api.code_assistant import CodeAssistant
from api.file_code_assistant import FileCodeAssistant

# Load environment variables
load_dotenv(override=True)

app = Flask(__name__)
api = Api(app)

# Add the code assistant endpoint
api.add_resource(CodeAssistant, '/code/prompt')
api.add_resource(FileCodeAssistant, '/code/files')

@app.route('/')
def home():
    return jsonify({
        "message": "Aider REST API Server",
        "version": "1.0.0",
        "endpoints": {
            "/health": "GET - Health check",
            "/code/prompt": "POST - Execute Aider code generation using /code prompt",
            "/code/files": "POST - Upload files and execute Aider code generation using /architect prompt",
        }
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})


if __name__ == '__main__':
    port = app.config['FLASK_PORT']
    debug = app.config['FLASK_DEBUG']
    app.run(host='0.0.0.0', port=port, debug=debug)
