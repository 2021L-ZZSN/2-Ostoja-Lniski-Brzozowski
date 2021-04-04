from typing import List

from tqdm import tqdm

from utils.files_io import load_json
from utils.files_io import write_json
from stock_prices import compare_stock_prices_for_company_name_to_wig, QuandlError


def merge_infostrefa_quandl_to_create_dataset(company_dispatches: List[dict]) -> List[dict]:
    company_dataset = []
    for dispatch in tqdm(company_dispatches):
        try:
            sentiment = compare_stock_prices_for_company_name_to_wig(
                company_name=dispatch['company_name'],
                stock_dispatch_date=dispatch['date'])
            company_dataset.append({
                **dispatch,
                'sentiment': sentiment
            })
        except QuandlError:
            pass

    return company_dataset


if __name__ == '__main__':
    ac_sa_data = load_json('data/robert_data/LUBAWA SA.json')
    merged_with_quandl = merge_infostrefa_quandl_to_create_dataset(ac_sa_data)
    write_json('test.json', merged_with_quandl)
