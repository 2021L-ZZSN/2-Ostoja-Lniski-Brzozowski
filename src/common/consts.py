from src.common.utils.files_io import load_json

CORRESPONDING_STOCKS = load_json('data/corresponding_stocks.json')
COMPANY_NAME_TO_ID = {el['company_name']: el['company_infosfera_id'] for el in CORRESPONDING_STOCKS}
