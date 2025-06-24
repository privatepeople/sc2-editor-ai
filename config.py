# Python Standard Library imports
import os

# Third-party Library imports
from dotenv import load_dotenv

# Custom Library imports
from utils import load_config


# Environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
NEO4J_URI = os.getenv('NEO4J_URI')
NEO4J_USERNAME = os.getenv('NEO4J_USERNAME')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD')

# config.yaml
CONFIG = load_config()
MODEL = CONFIG['llm']['model']
EMBEDDING = CONFIG['llm']['embedding']
MAXIMUM_INFORMATION_ACQUISITION_RATE = CONFIG['llm']['maximum_information_acquisition_rate']
MAXIMUM_RETRIEVER_ATTEMPTS = CONFIG['llm']['maximum_retriever_attempts']
API_LIMIT = CONFIG['fastapi']['api_limit']
SESSION_TIMEOUT = CONFIG['fastapi']['session_timeout']
SESSION_TIMEOUT_CHECK_PERIOD = CONFIG['fastapi']['session_timeout_check_period']

# Check config
assert (0 <= MAXIMUM_INFORMATION_ACQUISITION_RATE <= 1)
assert isinstance(MAXIMUM_RETRIEVER_ATTEMPTS, int) and MAXIMUM_RETRIEVER_ATTEMPTS > 0
assert isinstance(API_LIMIT, int) and API_LIMIT > 0
assert isinstance(SESSION_TIMEOUT, int) and SESSION_TIMEOUT > 0
assert isinstance(SESSION_TIMEOUT_CHECK_PERIOD, int) and SESSION_TIMEOUT_CHECK_PERIOD > 0