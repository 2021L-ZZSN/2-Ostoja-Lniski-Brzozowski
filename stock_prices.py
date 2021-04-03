import quandl

from utils.dates import previous_working_day, next_working_day
from utils.files_io import load_json

api_key = load_json('data/quandl/quandl_auth.json')['apikey']
quandl.ApiConfig.api_key = api_key

corresponding_stocks = load_json('data/corresponding_stocks.json')

company_name_to_code = {el['company_name']: el['company_code'] for el in corresponding_stocks}


def get_stock_prices(company_name: str, stock_dispatch_date: str) -> dict:
    """
    :param company_name: name of stock
    :param stock_dispatch_date: date of dispatch: 'YYYY-MM-DD'
    Retrieves a stock price for a given stock code, Day before - And day after a given date.
    :return {'before': <price>, 'after': <price>}
    """
    company_code = company_name_to_code[company_name]
    previous_working_day_data = quandl.get(f'WSE/{company_code}',
                                           start_date=previous_working_day(stock_dispatch_date),
                                           end_date=previous_working_day(stock_dispatch_date))
    next_working_day_data = quandl.get(f'WSE/{company_code}',
                                       start_date=next_working_day(stock_dispatch_date),
                                       end_date=next_working_day(stock_dispatch_date))
    assert len(previous_working_day_data) == len(next_working_day_data) == 1, \
        'Some data must be missing! Check if it\'s not a holiday'

    return {
        'previous_day': previous_working_day_data.iloc[0]['Close'],
        'next_day': next_working_day_data.iloc[0]['Close']
    }


if __name__ == '__main__':
    print(get_stock_prices('CCC SA', '2005-12-31'))
