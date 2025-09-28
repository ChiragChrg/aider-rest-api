# config.py
import os
from dotenv import load_dotenv

load_dotenv(override=True)

class Config:
    FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    MODEL = os.getenv('DEFAULT_MODEL', 'claude-3-5-sonnet-20241022')

class DevelopmentConfig(Config):
    DEBUG = True
    
class ProductionConfig(Config):
    DEBUG = False