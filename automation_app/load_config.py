import os
from dotenv import load_dotenv

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_DATA_PATH = os.path.join(ROOT_DIR, "test_data")
ATTACHMENT_PATH = os.path.join(TEST_DATA_PATH, "attachments")

def get_configs():
    # Load environment variables from the .env file
    load_dotenv()

    # Create a dictionary to hold all the settings
    SETTINGS = {
        'Settings_Rest_api': {
            'testdata_file': os.getenv('REST_TESTDATA_FILE'),
            'api_key': os.getenv('REST_API_KEY'),
            'api_secret': os.getenv('REST_API_SECRET'),
            'signature': os.getenv('REST_API_SIGNATURE'),
            'base_url': os.getenv('REST_API_BASE_URL'),
            'username': os.getenv('REST_USERNAME'),
            'password': os.getenv('REST_PASSWORD')
        },
        'Settings_Graphql': {
            'testdata_file': os.getenv('GRAPHQL_TESTDATA_FILE'),
            'api_key': os.getenv('GRAPHQL_API_KEY'),
            'api_secret': os.getenv('GRAPHQL_API_SECRET'),
            'signature': os.getenv('GRAPHQL_API_SIGNATURE'),
            'base_url': os.getenv('GRAPHQL_API_BASE_URL'),
            'username': os.getenv('GRAPHQL_USERNAME'),
            'password': os.getenv('GRAPHQL_PASSWORD')
        },
        'Settings_Common': {
            'environment': os.getenv('ENVIRONMENT')
        },
    }

    # Return the settings dictionary
    return SETTINGS