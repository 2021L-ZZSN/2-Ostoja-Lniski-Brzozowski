from dataclasses import asdict
from pathlib import Path
from typing import List

from click import STRING
from tqdm import tqdm
import os

from src.common.stock_dispatch import StockExchangeDispatch
from src.common.utils.files_io import load_json
from src.common.utils.files_io import write_json
from src.api.stock_prices import compare_stock_prices_for_company_name_to_wig, QuandlError
import click


def annotate_infosfera_files_from_dir(
        src_dir: str,
        target_dir: str,
        start_from: str = 'a',
        end_with: str = 'z') -> None:
    """
    Searches within src_dir for files containing stock exchange dispatches
    that were downloaded from infosfera website.
    Then annotates the data using quandl stock prices from a day before and after a given dispatch.
    The results are stored in a target_dir, each file changes name to '<company_name>_annotated.json'
    :param src_dir: source directory, from which the infosfera dispatches will be loaded.
    :param target_dir: target directory to which the annotated data will be stored.
    :param start_from: a letter(s) from which the annotation will be started. It is useful,
     if you want to annotate batches of data starting with a given letter.
    :param end_with: a letter(s) to which the annotation will be ended (inclusive).
    """
    file_names = [f for f in os.listdir(src_dir) if os.path.isfile(os.path.join(src_dir, f))]
    file_names.sort()
    file_names = [fn for fn in file_names if fn[0:len(start_from)].lower() >= start_from]
    file_names = [fn for fn in file_names if fn[0:len(end_with)].lower() <= end_with]
    for file_name in file_names:
        annotate_infosfera_file(f'{src_dir}/{file_name}', target_dir)


def annotate_infosfera_file(src_path: str, target_dir: str) -> None:
    """
    Annotates a file using quandl stock prices from a day before and after a given dispatch.
    :param src_path: Name of the file with infosfera dispatch data.
    :param target_dir: File where the annotated data will be stored.
    If the given directory does not exist, it will be automatically created.
    """
    # get rid of the dir
    infosfera_file_name = src_path.split('/')[-1]
    # get rid of ".json"
    infosfera_file_name = ''.join(infosfera_file_name.split('.')[:-1])
    target_infosfera_file_name = f'{infosfera_file_name}_annotated.json'

    infosfera_data = load_json(src_path)
    infosfera_dispatches = [StockExchangeDispatch(
        infosfera_dispatch['company_name'],
        infosfera_dispatch['content'],
        infosfera_dispatch['date']
    ) for infosfera_dispatch in infosfera_data]
    annotated_dispatches = _merge_infosfera_using_quadl_stock_prices(infosfera_dispatches)
    os.makedirs(target_dir, exist_ok=True)
    write_json(f'{target_dir}/{target_infosfera_file_name}',
               [asdict(annotated_dispatch) for annotated_dispatch in annotated_dispatches])


def _merge_infosfera_using_quadl_stock_prices(
        company_dispatches: List[StockExchangeDispatch]) -> List[StockExchangeDispatch]:
    """
    Fills in the sentiment of StockExchangeDispatch objects.
    :param company_dispatches StockExchangeDispatch objects without sentiment field.
    :return: StockExchangeDispatch objects with sentiment field.
    """
    company_dataset = []
    for dispatch in tqdm(company_dispatches):
        try:
            sentiment = compare_stock_prices_for_company_name_to_wig(
                company_name=dispatch.company_name,
                stock_dispatch_date=dispatch.date)
            company_dataset.append(
                StockExchangeDispatch(
                    dispatch.company_name,
                    dispatch.content,
                    dispatch.date,
                    sentiment
                )
            )
        except QuandlError:
            print(f'{dispatch.company_name} has no records in quandl for this date.')
        except KeyError:
            print(f'{dispatch.company_name} not found in company name list. Aborting download.')
            break

    return company_dataset


@click.command()
@click.option(
    "-i",
    "--input_dir",
    type=Path,
    required=True,
    help="Directory name from which the infosfera files will be loaded."
)
@click.option(
    "-o",
    "--output_dir",
    type=Path,
    required=True,
    help="Directory where the annotated data will be stored.",
)
@click.option(
    "-s",
    "--start_from",
    type=STRING,
    default="a",
    help="Letter(s) from which the annotation will be started.",
)
@click.option(
    "-e",
    "--end_with",
    type=STRING,
    default="z",
    help="Letter(s) to which the annotation will be performed (inclusive)."
)
def main(
        input_dir: Path, output_dir: Path, start_from: STRING, end_with: STRING
) -> None:
    annotate_infosfera_files_from_dir(
        src_dir=str(input_dir),
        target_dir=str(output_dir),
        start_from=start_from,
        end_with=end_with
    )


if __name__ == '__main__':
    main()
