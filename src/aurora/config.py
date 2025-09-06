from pathlib import Path
from dotenv import load_dotenv
import os

# Load .env file if it exists
env_path = Path(__file__).parents[1] / '.env'
load_dotenv(env_path)

# Database configuration
DB_USER = os.getenv('POSTGRES_USER', 'aurora')
DB_PASS = os.getenv('POSTGRES_PASSWORD', 'change_me')
DB_NAME = os.getenv('POSTGRES_DB', 'aurora')
DB_HOST = os.getenv('POSTGRES_HOST', 'localhost')
DB_PORT = os.getenv('POSTGRES_PORT', '5432')

# SQLAlchemy database URL
SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Other configurations
DISCLAIMER = """Research for informational and educational purposes only; not investment advice. 
Past performance is not indicative of future results."""
