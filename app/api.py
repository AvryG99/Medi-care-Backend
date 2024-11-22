from flask import Flask, request, jsonify
from agent import LLM_Agent

# Flask app
app = Flask(__name__)

# Database configuration
db_config = {
    'driver': '{ODBC Driver 17 for SQL Server}',
    'server': 'MSI',
    'database': 'EHR'
}

# Initialize LLM Agent
agent = LLM_Agent(db_config)

@app.route('/process_question', methods=['POST'])
def process_question():
    try:
        data = request.get_json()
        if 'question' not in data:
            return jsonify({"error": "Missing 'question' field in request"}), 400
        
        question = data['question']
        answer = agent.process_question(question)  # Gets the actual answer
        

        # Return the properly structured response
        return jsonify({
            "question": question,
            "answer": answer
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint to verify the API is running.
    """
    return jsonify({'status': 'API is running.'}), 200


@app.route('/get_logs', methods=['GET'])
def get_logs():
    """
    Endpoint to fetch the contents of the log file.
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

@app.route('/set_model', methods=['POST'])
def set_model():
    try:
        data = request.get_json()
        if 'model' not in data:
            return jsonify({"error": "Missing 'model' field in request"}), 400

        model = data['model']
        agent.set_gpt_model(model)
        return jsonify({"message": f"Model updated to {model}"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/set_max_tokens', methods=['POST'])
def set_max_tokens():
    try:
        data = request.get_json()
        if 'max_tokens' not in data:
            return jsonify({"error": "Missing 'max_tokens' field in request"}), 400

        max_tokens = int(data['max_tokens'])
        agent.set_max_tokens(max_tokens)
        return jsonify({"message": f"Max tokens updated to {max_tokens}"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/set_temperature', methods=['POST'])
def set_temperature():
    try:
        data = request.get_json()
        if 'temperature' not in data:
            return jsonify({"error": "Missing 'temperature' field in request"}), 400

        temperature = float(data['temperature'])
        agent.set_temperature(temperature)
        return jsonify({"message": f"Temperature updated to {temperature}"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500