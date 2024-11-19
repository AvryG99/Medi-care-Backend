# LLM Agent

The LLM (Language Model) Agent is a Python-based assistant powered by OpenAI's GPT (Generative Pre-trained Transformer) model. It interacts with users, processes questions related to querying an Electronic Health Record (EHR) database, and executes Python code dynamically generated to retrieve data from the database.

## Features

- **Dynamic Code Generation**: Generates Python code based on user queries to interact with the EHR database.
- **Error Handling**: Handles errors when executing generated code and provides debugging support through interaction with the GPT model.
- **Logging**: Logs interactions, generated code, and execution results for debugging and audit purposes.
- **Customizable**: Easily extendable and configurable for different database schemas and requirements.

## Installation

1. Clone the repository:

   ```bash
   git clone <repository_url>
   cd EHRAgent

2. Install the needed packages

   ```bash
   pip install -r requirements.txt

3. Set Environment Variables: Configure your environment variables for database connection and model configuration:

   **chatgpt_config.py**
   ```
   OPENAI_API_KEY = '<Your API Key>'
   openai.api_key = OPENAI_API_KEY
   GPT_MODEL = '<Your Model's Name>'
   ```

   
