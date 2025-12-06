import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'change-me')
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'postgresql://usuario:senha@localhost:5432/ilhas_de_calor'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True
