# Aider REST API Server

A Flask-based REST API server that provides code generation capabilities using the Aider AI coding assistant. This server allows you to generate code through various endpoints with different input methods.

## Features

- **Code Generation via Prompts**: Generate code using text instructions
- **File-based Code Generation**: Upload specification files and generate code based on them
- **Context-aware Generation**: Provide context, instructions, and code templates for precise output
- **Multiple AI Models**: Support for various AI models including Claude and others
- **Automatic Output Management**: Generated code is automatically organized and zipped
- **Cross-platform Support**: Works on Windows, macOS, and Linux

## Setup

### Prerequisites

- Python 3.10 or higher
- Git (for cloning the repository)

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd aider-rest-api
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv aider-env
   ```

3. **Activate the virtual environment**:
   - **Windows**: `aider-env\Scripts\activate`
   - **macOS/Linux**: `source aider-env/bin/activate`

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure environment variables**:
   Create a `.env` file in the root directory:
   ```env
   FLASK_PORT=5000
   FLASK_DEBUG=true

   DEFAULT_MODEL=claude-3-5-sonnet-20241022

   # Add your AI model API keys here
   GEMINI_API_KEY=your_gemini_key_here
   ANTHROPIC_API_KEY=your_api_key_here
   OPENAI_API_KEY=your_openai_key_here
   ```

## Running the Server

Start the server with:
```bash
python app.py
```

The server will be available at `http://localhost:5000` (or the port specified in your `.env` file).

## API Endpoints

### 1. Health Check
```
GET /health
```
Returns server health status.

### 2. Code Generation via Prompt
```
POST /code/prompt
```

Generate code using a text instruction.

**Request Body** (JSON):
```json
{
  "instruction": "Create a Python calculator class with basic operations",
  "files": ["optional_reference_file.py"],
  "directory": "/path/to/working/directory",
  "model": "claude-3-5-sonnet-20241022",
  "options": {
    "auto_commits": false,
    "dirty_commits": false,
    "dry_run": false
  }
}
```

### 3. File-based Code Generation
```
POST /code/files
```

Upload specification files and generate code based on them.

**Request** (Form Data):
- `files`: Multiple files (specification documents, etc.)
- `instruction`: Text instruction (optional)
- `directory`: Working directory (optional)
- `model`: AI model to use (optional)
- `options`: JSON string with additional options (optional)

**Example using curl**:
```bash
curl -X POST http://localhost:5000/code/files \
  -F "files=@resource/SPEC.md" \
  -F "files=@resource/PLAN.md" \
  -F "instruction=Implement the OPT3001 sensor driver" \
  -F "model=claude-3-5-sonnet-20241022"
```

### 4. Context-aware Code Generation
```
POST /code/generate
```

Generate code with detailed context and templates.

**Request Body** (JSON):
```json
{
  "context": "Building a sensor driver library for IoT applications",
  "instruction": "Create a complete OPT3001 ambient light sensor driver",
  "code_template": "Use modular design with HAL abstraction",
  "directory": "/path/to/project",
  "model": "claude-3-5-sonnet-20241022",
  "options": {
    "auto_commits": false,
    "dirty_commits": false,
    "dry_run": false
  }
}
```

## Response Format

All endpoints return JSON responses with the following structure:

```json
{
  "response": "AI-generated response text",
  "status": "success",
  "directory": "/working/directory/path",
  "files_processed": ["file1.md", "file2.py"],
  "model_used": "claude-3-5-sonnet-20241022",
  "output_directory": "/path/to/generated/code"
}
```

## Output Management

- Generated code is automatically placed in an `output/` directory
- Each generation creates a new subfolder with a meaningful name
- A ZIP file of the generated code is automatically created
- Original files are never modified (read-only mode)

## Configuration Options

### Environment Variables

- `FLASK_PORT`: Server port (default: 5000)
- `FLASK_DEBUG`: Enable debug mode (default: False)
- `DEFAULT_MODEL`: Default AI model to use

### Request Options

- `auto_commits`: Enable automatic git commits
- `dirty_commits`: Allow commits with uncommitted changes
- `dry_run`: Simulate execution without making changes

## Supported AI Models

The server supports various AI models through the Aider framework:
- Claude 3.5 Sonnet
- GPT-4 and variants
- Other models supported by Aider

## Example Usage

### Python Example
```python
import requests

# Generate code via prompt
response = requests.post('http://localhost:5000/code/prompt', json={
    "instruction": "Create a REST API for user management with Flask",
    "model": "claude-3-5-sonnet-20241022"
})

print(response.json())
```

### JavaScript Example
```javascript
// Upload files and generate code
const formData = new FormData();
formData.append('files', fileInput.files[0]);
formData.append('instruction', 'Implement the specification');

fetch('http://localhost:5000/code/files', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(data => console.log(data));
```

## Project Structure

```
aider-rest-api/
├── app.py                 # Main Flask application
├── config.py             # Configuration settings
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables (create this)
├── api/                  # API endpoint implementations
│   ├── code_assistant.py
│   ├── file_code_assistant.py
│   └── generate_code.py
├── utils/                # Utility functions
│   ├── aider_utils.py
│   └── common_utils.py
├── resource/             # Example specification files
├── output/               # Generated code output (auto-created)
└── README.md            # This file
```

## Troubleshooting

1. **Server won't start**: Check that the port isn't already in use
2. **Model errors**: Ensure your API keys are correctly set in the `.env` file
3. **Permission errors**: Make sure the server has write access to the working directory
4. **Memory issues**: Some models require significant memory; consider using smaller models for testing
5. **Cache issues**:  Clear Python cache files (`__pycache__` directories) if you encounter unexpected behavior