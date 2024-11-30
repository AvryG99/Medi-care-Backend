from flask import Flask, request, jsonify, send_from_directory
from flask_restx import Api, Resource
from flask_swagger_ui import get_swaggerui_blueprint
from agent import LLM_Agent
from flask_cors import CORS
import os
from werkzeug.serving import WSGIRequestHandler

# Flask app
app = Flask(__name__)
CORS(app)

# Setup Swagger UI
SWAGGER_URL = '/swagger-ui'  # URL to access Swagger UI
API_URL = '/static/swagger.json'  # URL to the Swagger JSON file (provided by flask_restx)

# Initialize Flask-RESTX Api (for generating Swagger documentation)
api = Api(app, prefix='/flask', version='1.0', title='Hospital API', description='API documentation for Hospital Management System')

# Increase timeout to 5 minutes
WSGIRequestHandler.timeout = 300

# Database configuration
db_config = {
    'driver': '{ODBC Driver 17 for SQL Server}',
    'server': os.getenv('DB_SERVER'),
    'database': os.getenv('DB_DATABASE'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD')
}

# Initialize LLM Agent
agent = LLM_Agent(db_config)

@app.route('/flask/process_question', methods=['POST'])
class ProcessQuestion(Resource):
  def process_question():
      """
      Process the question and get the answer using the LLM Agent.
      ---
      parameters:
        - in: body
          name: question
          description: The question that needs to be processed
          required: true
          schema:
            type: object
            properties:
              question:
                type: string
                example: "What is the patient's age?"
      responses:
        200:
          description: Successfully processed the question and returned the answer
          schema:
            type: object
            properties:
              question:
                type: string
                example: "What is the patient's age?"
              answer:
                type: string
                example: "The patient is 32 years old."
        400:
          description: Missing 'question' field in the request
        500:
          description: Internal server error
      """
      try:
          data = request.get_json()
          if 'question' not in data:
              return jsonify({"error": "Missing 'question' field in request"}), 400
          
          question = data['question']
          answer = agent.process_question(question)  # Gets the actual answer
          
          return jsonify({
              "question": question,
              "answer": answer
          }), 200
      except Exception as e:
          return jsonify({"error": str(e)}), 500


@app.route('/flask/health', methods=['GET'])
class HealthCheck(Resource):
  def health_check():
      """
      Health check endpoint to verify the API is running.
      ---
      responses:
        200:
          description: API is running
          schema:
            type: object
            properties:
              status:
                type: string
                example: "API is running."
      """
      return jsonify({'status': 'API is running.'}), 200


@app.route('/flask/get_logs', methods=['GET'])
class GetLogs(Resource):
  def get_logs():
      """
      Fetch the contents of the log file.
      ---
      responses:
        200:
          description: Successfully retrieved logs
          schema:
            type: object
            properties:
              logs:
                type: string
                example: "Log content here..."
        404:
          description: Log file not found
        500:
          description: Server error
      """
      log_file_path = 'agent_log.log'
      try:
          with open(log_file_path, 'r') as log_file:
              logs = log_file.read()
          return jsonify({
              "logs": logs
          }), 200
      except FileNotFoundError:
          return jsonify({"error": "Log file not found."}), 404
      except Exception as e:
          return jsonify({"error": str(e)}), 500


@app.route('/flask/set_model', methods=['POST'])
class SetModel(Resource):
  def set_model():
      """
      Set a new model for the LLM Agent.
      ---
      parameters:
        - in: body
          name: model
          description: The model to be set for the agent
          required: true
          schema:
            type: object
            properties:
              model:
                type: string
                example: "gpt-4"
      responses:
        200:
          description: Successfully updated model
          schema:
            type: object
            properties:
              message:
                type: string
                example: "Model updated to gpt-4"
        400:
          description: Missing 'model' field in the request
        500:
          description: Internal server error
      """
      try:
          data = request.get_json()
          if 'model' not in data:
              return jsonify({"error": "Missing 'model' field in request"}), 400

          model = data['model']
          agent.set_gpt_model(model)
          return jsonify({"message": f"Model updated to {model}"}), 200
      except Exception as e:
          return jsonify({"error": str(e)}), 500


@app.route('/flask/set_max_tokens', methods=['POST'])
class SetMaxTokens(Resource):
  def set_max_tokens():
      """
      Set the max tokens for the LLM Agent.
      ---
      parameters:
        - in: body
          name: max_tokens
          description: The max tokens to be set for the agent
          required: true
          schema:
            type: object
            properties:
              max_tokens:
                type: integer
                example: 2048
      responses:
        200:
          description: Successfully updated max tokens
          schema:
            type: object
            properties:
              message:
                type: string
                example: "Max tokens updated to 2048"
        400:
          description: Missing 'max_tokens' field in the request
        500:
          description: Internal server error
      """
      try:
          data = request.get_json()
          if 'max_tokens' not in data:
              return jsonify({"error": "Missing 'max_tokens' field in request"}), 400

          max_tokens = int(data['max_tokens'])
          agent.set_max_tokens(max_tokens)
          return jsonify({"message": f"Max tokens updated to {max_tokens}"}), 200
      except Exception as e:
          return jsonify({"error": str(e)}), 500


@app.route('/flask/set_temperature', methods=['POST'])
class SetTemperature(Resource):
  def set_temperature():
      """
      Set the temperature for the LLM Agent.
      ---
      parameters:
        - in: body
          name: temperature
          description: The temperature to be set for the agent
          required: true
          schema:
            type: object
            properties:
              temperature:
                type: number
                format: float
                example: 0.7
      responses:
        200:
          description: Successfully updated temperature
          schema:
            type: object
            properties:
              message:
                type: string
                example: "Temperature updated to 0.7"
        400:
          description: Missing 'temperature' field in the request
        500:
          description: Internal server error
      """
      try:
          data = request.get_json()
          if 'temperature' not in data:
              return jsonify({"error": "Missing 'temperature' field in request"}), 400

          temperature = float(data['temperature'])
          agent.set_temperature(temperature)
          return jsonify({"message": f"Temperature updated to {temperature}"}), 200
      except Exception as e:
          return jsonify({"error": str(e)}), 500

# Swagger UI configuration
swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={'app_name': "Flask API"}
)

@app.route('/static/swagger.json')
def swagger_json():
    return send_from_directory('static', 'swagger.json')  # Serve the swagger.json file from static folder

# Register the Swagger UI blueprint
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)

