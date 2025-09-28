from flask import Flask, request, jsonify
from flask_restful import Api, Resource
import os
from dotenv import load_dotenv
from api.code_assistant import CodeAssistant

# Load environment variables
load_dotenv(override=True)

app = Flask(__name__)
api = Api(app)

# Add the code assistant endpoint
api.add_resource(CodeAssistant, '/code_assistant')

@app.route('/')
def home():
    return jsonify({
        "message": "Aider REST API Server",
        "version": "1.0.0",
        "endpoints": {
            "/code_assistant": "POST - Execute Aider code generation"
        }
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})


if __name__ == '__main__':
    port = app.config['FLASK_PORT']
    debug = app.config['FLASK_DEBUG']
    app.run(host='0.0.0.0', port=port, debug=debug)
