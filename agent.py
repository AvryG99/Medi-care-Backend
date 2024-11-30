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
        self.gpt_model = GPT_MODEL
        self.max_tokens = 1000
        self.temperature = 0.7

    def setup_logging(self):
        logging.basicConfig(
            filename='agent_log.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def set_gpt_model(self, model):
        self.gpt_model = model
        logging.info(f"GPT model updated to: {model}")

    def set_max_tokens(self, max_tokens):
        self.max_tokens = max_tokens
        logging.info(f"Max tokens updated to: {max_tokens}")

    def set_temperature(self, temperature):
        self.temperature = temperature
        logging.info(f"Temperature updated to: {temperature}")

    def query_chatgpt(self, prompt):
        response = openai.ChatCompletion.create(
            model=self.gpt_model,
            messages=[{"role": "system", "content": "You are a Python programming assistant."},
                      {"role": "user", "content": prompt}],
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )
        # print(response['choices'][0]['message']['content'])
        # return response['choices'][0]['message']['content']
        
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
        answer = None  # To hold the captured print output
        
        for attempt in range(3):
            code = self.query_chatgpt(prompt)
            try:
                # Redirect stdout to capture print statements
                captured_output = io.StringIO()
                sys.stdout = captured_output  # Redirect print to the StringIO buffer
                
                # Execute the retrieved code
                exec_globals = {}
                exec_locals = {}
                exec(code, exec_globals, exec_locals)

                # Now captured_output contains the printed values
                answer = captured_output.getvalue().strip()  # Capture printed output
                final_code = code  # Store the final successfully executed code
                self.log_interaction(question, f"Execution successful, answer: {answer}", code, success=True)
                break
            except Exception as e:
                error_message = f"Error occurred with the generated code:\n{code}\nError details:\n{str(e)}\n"
                self.log_interaction(question, error_message, code, success=False)
                prompt = self.update_prompt(prompt, e)
            finally:
                # Reset stdout back to normal
                sys.stdout = sys.__stdout__

        current_time = datetime.now()
        formatted_time = current_time.strftime("%Y%m%d%H%M%S")
        #file_name = f'server2/Medi-care-Backend/result/result-{formatted_time}.py' 
        file_name = f'result/result-{formatted_time}.py' 

        if final_code:
            with open(file_name, 'w') as file:
                file.write(final_code)
        response_prompt = f"""
        The user given a question as follow: {question}.
        An LLM Agent answer that question by generating a python code as follow: {final_code} 
        with the following result from the code: {answer}.
        Can you help me generate a response to answer the question from the user?
        Please do not mention about the generated code in the response since user doesn't know about the code is exist.
        Answer by the format: "Based on your question and the current data record from the database, the answer is [the answer].
        """
        response = openai.ChatCompletion.create(
            model=self.gpt_model,
            messages=[{"role": "system", "content": "You are a response generation assistant."},
                      {"role": "user", "content": response_prompt}],
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )
        if answer is not None:
            return response['choices'][0]['message']['content']
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
