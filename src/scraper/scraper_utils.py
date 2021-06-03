from typing import Set

import requests
from bs4 import BeautifulSoup

from src.common.utils.files_io import load_json

DEFAULT_INCLUDED_COMPANIES_PATH = 'data/corresponding_stocks.json'
HTTP_OK = 200


def get_included_companies(filepath=DEFAULT_INCLUDED_COMPANIES_PATH) -> Set[str]:
    included_companies = load_json(filepath)
    result = set()
    for included_company in included_companies:
        company_name = included_company.get('company_name').upper()
        result.add(company_name)

    return result


def get_page_root(url: str):
    company_page = requests.get(url)
    if company_page.status_code != HTTP_OK:
        raise ScrapperError(f'Error retrieving page. Status code: {company_page.status_code}')
    return BeautifulSoup(company_page.content, 'html.parser')


class ScrapperError(Exception):
    pass
