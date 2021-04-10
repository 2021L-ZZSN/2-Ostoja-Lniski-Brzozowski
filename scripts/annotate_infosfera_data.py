from typing import List

from tqdm import tqdm
import os
from utils.files_io import load_json
from utils.files_io import write_json
from stock_prices import compare_stock_prices_for_company_name_to_wig, QuandlError


def annotate_data_from_dir(src_dir: str, target_dir: str):
    file_names = [f for f in os.listdir(src_dir) if os.path.isfile(os.path.join(src_dir, f))]
    for file_name in file_names:
        annotate_infosfera_file(f'{src_dir}/{file_name}', target_dir)


def annotate_infosfera_file(src_path: str, target_dir: str):
    # get rid of the dir
    infosfera_file_name = src_path.split('/')[-1]
    # get rid of ".json"
    infosfera_file_name = ''.join(infosfera_file_name.split('.')[:-1])
    target_infosfera_file_name = f'{infosfera_file_name}_annotated.json'

    infosfera_data = load_json(src_path)
    annotated_data = _merge_infosfera_quandl_to_create_dataset(infosfera_data)
    os.makedirs(target_dir, exist_ok=True)
    write_json(f'{target_dir}/{target_infosfera_file_name}', annotated_data)


def _merge_infosfera_quandl_to_create_dataset(company_dispatches: List[dict]) -> List[dict]:
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
            print(f'{dispatch["company_name"]} has no records in quandl for this date.')
        except KeyError:
            print(f'{dispatch["company_name"]} not found in company name list. Aborting download.')
            break

    return company_dataset


if __name__ == '__main__':
    annotate_data_from_dir('data/robert_data', 'data/annotated/robert_data')