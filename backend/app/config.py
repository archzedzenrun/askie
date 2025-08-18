import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

class Config:
    DEBUG = os.getenv("DEBUG", "False") == "True"
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_CLIENT = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_NAME = "video_transcripts"
