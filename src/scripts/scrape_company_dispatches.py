from dataclasses import asdict
from pathlib import Path

import click
from click import INT, STRING
import os
from src.common.consts import COMPANY_NAME_TO_ID
from src.common.utils.files_io import write_json
from src.api.scraper import scrape_dispatches_for_company


def _store_scrape_for_company(
        company_name: str,
        year_start: int,
        year_end: int,
        sleep_time: int,
        output_dir: Path) -> None:
    print(f'Scraping dispatches for: {company_name} from {year_start} to {year_end}.')
    company_infos = scrape_dispatches_for_company(
        company_name,
        year_start=year_start,
        year_end=year_end,
        sleep_time=sleep_time)
    os.makedirs(str(output_dir), exist_ok=True)
    write_json(f"{str(output_dir)}/{company_name}.json",
               [asdict(company_info) for company_info in company_infos])


@click.command()
@click.option(
    "-s",
    "--year_start",
    type=INT,
    required=True,
    help="Start year for the scraping."
)
@click.option(
    "-e",
    "--year_end",
    type=INT,
    required=True,
    help="End year for the scraping (inclusive).",
)
@click.option(
    "--company_idx_start",
    type=INT,
    required=False,
    help="If you want to run for many companies, provide a start idx and end idx.",
)
@click.option(
    "--company_idx_end",
    type=INT,
    required=False,
    help="If you want to run for many companies, provide an end idx and start idx."
         "end idx is the first idx that will be excluded."
)
@click.option(
    "-c",
    "--company_name",
    type=STRING,
    required=False,
    help="If you want to scrape just for one company, provide its name here."
         " It has to match the company name from data/corresponding_stocks.json."
)
@click.option(
    "-o",
    "--output_dir",
    type=Path,
    required=False,
    default=Path("scraped/"),
    help="Output dir where your file will be stored. The name of the file is taken from a company name."
)
@click.option(
    "--sleep_time",
    type=INT,
    required=False,
    default=10,
    help="Sleep time between request sent to infosfera."
)
def main(
        year_start: INT,
        year_end: INT,
        company_idx_start: INT,
        company_idx_end: INT,
        company_name: STRING,
        output_dir: Path,
        sleep_time: INT):
    if company_name:
        _store_scrape_for_company(
            company_name,
            year_start=year_start,
            year_end=year_end,
            sleep_time=sleep_time,
            output_dir=output_dir)

    elif company_idx_start and company_idx_end:
        for i, company_name in enumerate(COMPANY_NAME_TO_ID):
            if company_idx_start <= i < company_idx_end:
                _store_scrape_for_company(
                    company_name,
                    year_start=year_start,
                    year_end=year_end,
                    sleep_time=sleep_time,
                    output_dir=output_dir)
            elif company_idx_end <= i:
                break
    else:
        print("Wrong arguments provided.")


if __name__ == '__main__':
    main()
