import os
from flask import request
from flask_restful import Resource
from config import Config
from utils.common_utils import (
    build_instruction,
    setup_directory,
    create_zip_file,
    validate_json,
    upload_to_cloud,
)
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
            required_fields = ["context", "instruction"]
            is_valid, data = validate_json(payload, required_fields)

            # Return error if validation fails
            if not is_valid:
                raise ValueError(data)

            # Ensure data is a dictionary
            if not isinstance(data, dict):
                raise ValueError("Invalid JSON payload")

            # Extract parameters from validated data
            instruction = data.get("instruction", "")
            context = data.get("context", "")
            code_template = data.get("code_template", "")
            directory = data.get("directory", os.getcwd())
            model_name = data.get("model", Config.MODEL)
            options = data.get("options", {})

            # Configure Aider options with safe defaults
            auto_commits = options.get("auto_commits", False)
            dirty_commits = options.get("dirty_commits", False)
            dry_run = options.get("dry_run", False)

            # Change to specified directory if provided
            original_dir = os.getcwd()
            base_output_dir = setup_directory(directory, original_dir)

            # Get list of existing directories before execution
            existing_dirs = set()
            if os.path.exists(base_output_dir):
                existing_dirs = set(os.listdir(base_output_dir))

            # Create model and coder instances
            coder = create_coder(
                model_name=model_name,
                auto_commits=auto_commits,
                dirty_commits=dirty_commits,
                dry_run=dry_run,
            )

            # Build complete instruction
            full_instruction = build_instruction(
                context, instruction, code_template, base_output_dir
            )

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
                "output_directory": output_dir,
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

    # Functional Code Generation Methods
    def generate_code(
        self, context, instruction, code_template="", directory=None, options=None
    ):
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

        original_dir = None
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
                    "auto_commits": False,
                    "dirty_commits": False,
                    "dry_run": False,
                }
            else:
                options.setdefault("auto_commits", False)
                options.setdefault("dirty_commits", False)
                options.setdefault("dry_run", False)

            # Change to specified directory if provided
            original_dir = os.getcwd()
            base_output_dir = setup_directory(directory, original_dir)

            # Get list of existing directories before execution
            existing_dirs = set()
            if os.path.exists(base_output_dir):
                existing_dirs = set(os.listdir(base_output_dir))

            # Create model and coder instances
            coder = create_coder(
                model_name=model_name,
                auto_commits=options["auto_commits"],
                dirty_commits=options["dirty_commits"],
                dry_run=options["dry_run"],
            )

            # temp_instruction = """
            # # Aider Instructions for Python Implementation

            # ## Generated Instruction
            # Generate a Python implementation for the torque sensor transfer function analysis using the provided code template. Ensure to fill in the placeholders with appropriate logic for sensor specifications, error calculations, and performance assessments. Specifically, replace the following placeholders with relevant values:
            # - {{SENSOR_TYPE}}: e.g., "Torque Sensor"
            # - {{APPLICATION_NAME}}: e.g., "Torque Measurement"
            # - {{INPUT_PHYSICAL_QUANTITY}}: e.g., "Torque"
            # - {{OUTPUT_TYPES}}: e.g., ["Voltage", "Current"]
            # - {{SYSTEMATIC_ERROR_1}}: e.g., "Non-linearity"
            # - {{ERROR_1_DESCRIPTION}}: e.g., "Deviation from the ideal output"
            # - {{NONLINEARITY_SPEC}}: e.g., 0.01
            # - {{HYSTERESIS_SPEC}}: e.g., 0.005
            # - {{TEMP_DRIFT_SPEC}}: e.g., 0.002
            # - {{REPEATABILITY_SPEC}}: e.g., 0.001
            # - {{NOISE_SPEC}}: e.g., 0.0005
            # - {{CALIBRATION_METADATA}}: e.g., "Calibration performed on 2023-01-01"
            # - {{PARAMETER_INITIALIZATION_LOGIC}}: Logic to initialize parameters based on sensor specs
            # - {{OUTPUT_UNIT}}: e.g., "Nm"
            # - {{SENSITIVITY_UNIT}}: e.g., "V/Nm"
            # - {{INPUT_UNIT}}: e.g., "Nm"
            # - {{LINEAR_SENSITIVITY_CALCULATION}}: Logic for calculating linear sensitivity
            # - {{NOMINAL_OUTPUT_VALUE}}: e.g., 5.0
            # - {{ZERO_INPUT_OUTPUT}}: e.g., 0.0
            # - {{NONLINEAR_FITTING_METHOD}}: Logic for fitting non-linear models
            # - {{OFFSET_CALCULATION}}: Logic for calculating offset
            # - {{DEFAULT_OFFSET_VALUE}}: e.g., 0.0
            # - {{ADDITIONAL_SYSTEMATIC_ERRORS}}: Any extra systematic errors
            # - {{ADDITIONAL_RANDOM_ERRORS}}: Any extra random errors
            # - {{ADDITIONAL_SYSTEMATIC_CALCULATIONS}}: Additional calculations for systematic errors
            # - {{ADDITIONAL_RANDOM_ERROR_COMPONENTS}}: Additional components for random errors
            # - {{ADDITIONAL_RANDOM_ERROR_STD}}: Additional standard deviations for random errors
            # - {{ACCURACY_SPEC}}: e.g., "±0.1%"
            # - {{RESPONSE_TIME_SPEC}}: e.g., "50 ms"
            # - {{DRIFT_SPEC}}: e.g., "0.01 Nm per year"
            # - {{NOISE_LEVEL_SPEC}}: e.g., "0.0005 Nm"
            # - {{ADDITIONAL_PERFORMANCE_METRICS}}: Any extra performance metrics
            # - {{ACCURACY_ASSESSMENT_LOGIC}}: Logic for assessing accuracy
            # - {{RESPONSE_TIME_LOGIC}}: Logic for assessing response time

            # ## Implementation Steps
            # 1. Define the SensorSpecifications and ErrorParameters dataclasses to encapsulate sensor details and error characteristics.
            # 2. Implement the MathUtils class with methods for polynomial fitting, interpolation, filtering, and error calculations.
            # 3. Create the TransferFunctionAnalyzer class to handle the transfer function analysis, including methods for calculating ideal outputs, systematic errors, and measured outputs.
            # 4. In the TransferFunctionAnalyzer, initialize parameters based on sensor specifications and calibration data.
            # 5. Implement methods to calculate systematic errors and generate random errors based on defined error parameters.
            # 6. Create a PerformanceAnalyzer class to assess the sensor's performance against specified metrics.
            # 7. Implement methods in PerformanceAnalyzer to evaluate accuracy and response time based on test inputs and reference outputs.
            # 8. Use logging to track the initialization and calculations throughout the analysis process.

            # ## Required Libraries
            # numpy, matplotlib, typing, dataclasses, logging

            # ## Input Variables
            # nominal_torque: float, temperature: float, time: float

            # ## Output Variables
            # frequency_output: float, voltage_output: float
            # """

            # Build complete instruction
            # full_instruction = build_instruction(
            #     context, instruction, code_template, base_output_dir
            # )
            full_instruction = build_instruction(
                instruction, None, None, base_output_dir
            )

            # Execute the instruction
            result = execute_instruction(coder, full_instruction)

            # Create zip file of the new output directory
            zip_result = create_zip_file(base_output_dir, existing_dirs)

            output_dir = zip_result.get("output_dir")
            zipFile = zip_result.get("zipfile")
            zipName = zip_result.get("zip_path")
            zipStatus = zip_result.get("status", False)

            # Return error if zip creation failed
            if not zipStatus:
                raise ValueError("No new files were generated, zip file not created.")

            # Upload zip file to cloud storage
            if zipFile and zipName:
                upload_to_cloud(zipFile, zipName)

            return {
                "response": result,
                "status": 201,
                "directory": directory,
                "files_processed": [],
                "model_used": model_name,
                "output_directory": output_dir,
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
