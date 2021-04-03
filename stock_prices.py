import quandl

from utils.dates import previous_working_day, next_working_day
from utils.files_io import load_json

api_key = load_json('data/quandl/quandl_auth.json')['apikey']
quandl.ApiConfig.api_key = api_key

corresponding_stocks = load_json('data/corresponding_stocks.json')

company_name_to_code = {el['company_name']: el['company_code'] for el in corresponding_stocks}


def get_stock_prices_for_company_name(
        company_name: str,
        stock_dispatch_date: str,
        stock_exchange_name: str = 'WSE') -> dict:
    company_code = company_name_to_code[company_name]
    return get_stock_prices(company_code, stock_dispatch_date, stock_exchange_name)


def get_stock_prices(company_code: str, stock_dispatch_date: str, stock_exchange_name: str = 'WSE') -> dict:
    """
    :param stock_exchange_name: str
    :param company_code: code od a company matching in quandl database.
    :param stock_dispatch_date: date of dispatch: 'YYYY-MM-DD'
    Retrieves a stock price for a given stock code, Day before - And day after a given date.
    :return {'before': <price>, 'after': <price>}
    """
    previous_working_day_data = quandl.get(f'{stock_exchange_name}/{company_code}',
                                           start_date=previous_working_day(stock_dispatch_date),
                                           end_date=previous_working_day(stock_dispatch_date))
    next_working_day_data = quandl.get(f'{stock_exchange_name}/{company_code}',
                                       start_date=next_working_day(stock_dispatch_date),
                                       end_date=next_working_day(stock_dispatch_date))
    assert len(previous_working_day_data) == len(next_working_day_data) == 1, \
        'Some data must be missing! Check if it\'s not a holiday'

    return {
        'previous_day': previous_working_day_data.iloc[0]['Close'],
        'next_day': next_working_day_data.iloc[0]['Close']
    }


def compare_stock_prices_for_company_name_to_wig(
        company_name: str,
        stock_dispatch_date: str,
        stock_exchange_name: str = 'WSE') -> float:
    company_code = company_name_to_code[company_name]
    return compare_stock_prices_to_wig(
        company_code=company_code,
        stock_dispatch_date=stock_dispatch_date,
        stock_exchange_name=stock_exchange_name)


def compare_stock_prices_to_wig(company_code: str, stock_dispatch_date: str, stock_exchange_name: str = 'WSE') -> float:
    company_prices = get_stock_prices(company_code, stock_dispatch_date, stock_exchange_name)
    wig_prices = get_stock_prices('WIG', stock_dispatch_date, 'WSE')
    return _calculate_score_using_formula(
        x1=company_prices['previous_day'],
        x2=company_prices['next_day'],
        y1=wig_prices['previous_day'],
        y2=wig_prices['next_day']
    )


def _calculate_score_using_formula(x1: float, x2: float, y1: float, y2: float):
    """
    Calculating score by using our formula: ((x2-x1)/x1) - ((y2-y1)/y1)
    Where:
        - 1 means the previous day,
        - 2 means the following day,
        - x means the company stock price
        - y means some index (usually wig) price
    """
    return ((x2 - x1) / x1) - ((y2 - y1) / y1)


if __name__ == '__main__':
    print(compare_stock_prices_to_wig('CCC', '2021-01-12'))
