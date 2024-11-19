from flask import Flask, request, jsonify
from agent import LLM_Agent
import os

# Flask app
app = Flask(__name__)

# Database configuration
db_config = {
    'driver': '{ODBC Driver 17 for SQL Server}',
    'server': os.getenv('SERVER'),
    'database': os.getenv('DATABASE')
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
