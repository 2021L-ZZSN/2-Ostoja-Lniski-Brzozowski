from typing import Set

from src.utils.files_io import write_json

STOCK_NAMES_TO_CODES_PATH = 'data/infosfera/stock_names_to_codes.csv'
QUANDL_METADATA_PATH = 'data/quandl/WSE_metadata.csv'
CORRESPONDING_STOCKS_PATH = 'data/corresponding_stocks.json'


def read_stock_names_to_codes(path=STOCK_NAMES_TO_CODES_PATH, delimiter=';') -> dict:
    stock_names_to_codes = {}
    with open(path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            values = line.split(delimiter)
            stock_names_to_codes[values[0]] = values[1]
    return stock_names_to_codes


def read_quandl_possible_stock_codes(path=QUANDL_METADATA_PATH, delimiter=',') -> Set[str]:
    possible_stock_codes = set()
    with open(path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            possible_stock_code = line.split(delimiter)[0]
            possible_stock_codes.add(possible_stock_code)
    return possible_stock_codes


def find_corresponding_stocks_infosfera_quandl() -> list:
    corresponding_stocks = []
    stock_names_to_codes_infosfera = read_stock_names_to_codes()
    quandl_possible_codes = read_quandl_possible_stock_codes()
    for company_name, company_code in stock_names_to_codes_infosfera.items():
        if company_code in quandl_possible_codes:
            corresponding_stocks.append({
                'company_name': company_name.upper(),
                'company_code': company_code
            })

    return corresponding_stocks


if __name__ == '__main__':
    corresponding_stocks = find_corresponding_stocks_infosfera_quandl()
    write_json(CORRESPONDING_STOCKS_PATH, corresponding_stocks)
