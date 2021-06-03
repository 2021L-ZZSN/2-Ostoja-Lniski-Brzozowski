from typing import List

from utils.files_io import load_json, write_json

CORRESPONDING_STOCKS_PATH = 'data/corresponding_stocks.json'
COMPANY_NAME_TO_ID_PATH = 'data/infosfera/company_name_to_id_raw.json'


def add_infosfera_ids_to_corresponding_stocks(corresponding_stocks: List[dict], remove_non_matching=True):
    company_name_to_id = load_json(COMPANY_NAME_TO_ID_PATH)
    updated_corresponding_stocks = []
    for stock in corresponding_stocks:
        if stock['company_name'] in company_name_to_id or not remove_non_matching:
            updated_corresponding_stocks.append({
                'company_name': stock['company_name'],
                'company_code': stock['company_code'],
                'company_infosfera_id': company_name_to_id[stock['company_name']]
            })
    return updated_corresponding_stocks


if __name__ == '__main__':
    infosfera = add_infosfera_ids_to_corresponding_stocks(load_json(CORRESPONDING_STOCKS_PATH))
    write_json('data/corresponding_stocks.json', infosfera)
    print(len(infosfera))