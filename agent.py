import openai
import logging
import unicodedata
import pyodbc
from chatgpt_config import GPT_MODEL
from prompt import generate_prompt
from datetime import datetime
import io
import sys

class LLM_Agent:
    def __init__(self, db_config):
        self.db_config = db_config
        self.setup_logging()

    def setup_logging(self):
        logging.basicConfig(
            filename='agent_log.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def query_chatgpt(self, prompt):
        response = openai.ChatCompletion.create(
            model=GPT_MODEL,
            messages=[{"role": "system", "content": "You are a Python programming assistant."},
                      {"role": "user", "content": prompt}],
            max_tokens=1000
        )
        
        # Extract the generated code from the response
        generated_code = self.extract_generated_code(response.choices[0].message['content'])
        
        # Ensure only the code itself is returned
        sanitized_code = self.sanitize_code(generated_code)
        return sanitized_code

    def extract_generated_code(self, full_response):
        # This method extracts the generated Python code from the full response
        code_start_index = full_response.find("```python")
        code_end_index = full_response.rfind("```")
        if code_start_index != -1 and code_end_index != -1:
            return full_response[code_start_index + 9:code_end_index].strip()
        else:
            return ""

    def sanitize_code(self, code):
        normalized_code = unicodedata.normalize('NFKD', code).encode('ascii', 'ignore').decode('utf-8')
        return normalized_code

    def process_question(self, question):
        prompt = generate_prompt(question, self.db_config)
        final_code = None
        for attempt in range(3):
            code = self.query_chatgpt(prompt)
            result = ""
            try:
                # Execute the retrieved code
                result = exec(code)
                final_code = code  # Store the final successfully executed code
                self.log_interaction(question, "Execution successful", code, success=True)
                break
            except Exception as e:
                error_message = f"Error occurred with the generated code:\n{code}\nError details:\n{str(e)}\n"
                self.log_interaction(question, error_message, code, success=False)
                prompt = self.update_prompt(prompt, e)
        
        current_time = datetime.now()
        formatted_time = current_time.strftime("%Y%m%d%H%M%S")
        file_name = f'result/result-{formatted_time}.py'  
        print(f'result: {result}')
        if final_code:
            with open(file_name, 'w') as file:
                file.write(final_code)
            return result
        else:
            return "Unable to retrieve the data after 3 attempts."

    def log_interaction(self, question, result, code, success=True):
        if success:
            log_message = f"Question: {question}\nResult:\n{result}\n"
            logging.info(log_message)
        else:
            log_message = f"Question: {question}\nError Message:\n{result}\n"
            logging.error(log_message)

    def update_prompt(self, prompt, error):
        error_prompt = f"{prompt}\nThe following error occurred:\n{str(error)}\nPlease fix the code."
        return error_prompt
