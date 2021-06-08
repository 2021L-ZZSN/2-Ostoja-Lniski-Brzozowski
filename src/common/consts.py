from src.common.utils.files_io import load_json

CORRESPONDING_STOCKS = load_json('data/corresponding_stocks.json')
COMPANY_NAME_TO_ID = {el['company_name']: el['company_infosfera_id'] for el in CORRESPONDING_STOCKS}
COMPANY_NAME_TO_CODE = {el['company_name']: el['company_code'] for el in CORRESPONDING_STOCKS}

# For this to work, you need to copy apikey from github SECRETS and copy it inside QUANDL_AUTH_FILE file.
QUANDL_AUTH_FILE = "data/quandl/quandl_auth.json"
QUANDL_API_KEY = load_json(QUANDL_AUTH_FILE)['apikey']

RANDOM_STATE = 42
