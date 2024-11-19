import openai
import os

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

openai.api_key = OPENAI_API_KEY

GPT_MODEL = 'gpt-4o'
