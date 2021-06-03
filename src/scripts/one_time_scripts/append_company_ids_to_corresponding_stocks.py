from typing import List

from src.common.utils.files_io import load_json, write_json

CORRESPONDING_STOCKS_PATH = 'data/corresponding_stocks.json'
COMPANY_NAME_TO_ID_PATH = 'data/infosfera/company_name_to_id_raw.json'


def add_infosfera_ids_to_corresponding_stocks(
        corresponding_stocks: List[dict],
        remove_non_matching=True) -> List[dict]:
    """
    Adds infosfera ids from API calls to corresponding stocks file.
    It is useful, because then you can make API calls directly for a given company.
    :param corresponding_stocks: Previous corresponding stocks with structure:
    {
        "company_name": "<company name>",
        "company_code": "<company code>"
    }
    :param remove_non_matching: The companies that were not found in a file
     located in COMPANY_NAME_TO_ID_PATH will be removed.
    :return: New corresponding stocks list with structure:
    {
        "company_name": "<company name>",
        "company_code": "<company code>",
        "company_infosfera_id": "<infosfera id>"
    }
    """
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
    # This script should not be used anymore, since its result is already stored in a file.
    # located in CORRESPONDING_STOCKS_PATH
    old_corresponding_stocks = load_json(CORRESPONDING_STOCKS_PATH)
    infosfera = add_infosfera_ids_to_corresponding_stocks(old_corresponding_stocks)
    write_json(CORRESPONDING_STOCKS_PATH, infosfera)
