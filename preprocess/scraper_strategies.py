import time
from typing import List

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
from tqdm import tqdm
import re
from preprocess.scraper import scrape_company_info_from_infosfera, ScrapperError
from preprocess.scraper_utils import get_included_companies
from utils.files_io import write_json, append_json, load_json

date_regex_with_dots = re.compile('\d\d\.\d\d\.\d\d\d\d')
MIN_POSSIBLE_YEAR = 2004
MAX_POSSIBLE_YEAR = 2021

CORRESPONDING_STOCKS = load_json('data/corresponding_stocks.json')
COMPANY_NAME_TO_ID = {el['company_name']: el['company_infosfera_id'] for el in CORRESPONDING_STOCKS}


def scrape_sources_with_given_ids(
        url_base: str,
        first_included: int,
        first_excluded: int,
        requests_in_row: int = 10,
        sleep_between_requests: int = 30) -> List[dict]:
    company_infos = []
    failed_counter = 0

    for i in tqdm(range(first_excluded - first_included)):

        try:
            url = url_base + str(first_included + i)
            company_info = scrape_company_info_from_infosfera(
                url=url,
                included_companies=get_included_companies())
            company_infos.append(company_info)
        except ScrapperError:
            failed_counter = failed_counter + 1

        if i % requests_in_row == requests_in_row - 1:
            time.sleep(sleep_between_requests)

    print('Nie pobrano danych dla ', failed_counter, ' firm')
    return company_infos


def scrape_sources_for_company(company_name: str, year_start=MIN_POSSIBLE_YEAR, year_end=MAX_POSSIBLE_YEAR):
    year_range = range(year_start, year_end + 1)
    scraped_dispatches_all = []
    for year in year_range:
        url_base = 'http://infostrefa.com/infostrefa/pl/raporty/espi/firmy'
        assert company_name in COMPANY_NAME_TO_ID, 'Sorry, such company name was not found in corresponding_stocks.json.'
        url = f'{url_base}/{COMPANY_NAME_TO_ID[company_name]},{year},0,0,1'
        page = requests.get(url)
        if page.status_code != 200:
            print(f'Error retrieving page. Status code: {page.status_code}')
            return None
        soup = BeautifulSoup(page.content, 'html.parser')
        hrefs = soup.find_all('tbody')
        assert len(hrefs) == 3, 'Something went wrong. Bad assumption.'
        href = hrefs[1]
        scraped_dispatches = _scrape_company_dispatches_from_tbody_href(href)
        if scraped_dispatches:
            scraped_dispatches_all.extend(scraped_dispatches)
    return scraped_dispatches_all


def _scrape_company_dispatches_from_tbody_href(href):
    company_dispatches_from_date_all = []
    tags = [el for el in href if type(el) is Tag]
    dates_idxs = [i for i in range(len(tags)) if date_regex_with_dots.findall(tags[i].text)]
    for i in tqdm(range(len(dates_idxs) - 1)):
        company_dispatches_from_date = _scrape_company_dispatches_from_a_given_date(
            tags[dates_idxs[i]: dates_idxs[i + 1]])
        if company_dispatches_from_date:
            company_dispatches_from_date_all.extend(company_dispatches_from_date)
    return company_dispatches_from_date_all


def _scrape_company_dispatches_from_a_given_date(tags):
    company_infos = []
    for i in range(1, len(tags)):
        hrefs = tags[i].find_all('a')
        tags_to_scrape = [tag for tag in hrefs if tag['href'].startswith('http://')]
        for tag in tags_to_scrape:
            try:
                company_infos.append(
                    scrape_company_info_from_infosfera(url=tag['href'], included_companies=get_included_companies()))
            except ScrapperError:
                pass
    return company_infos


def scrape_company_name(company_id: int) -> str or None:
    """
    Scrap dispatches from a given date.
    :param date: 'YYYY-MM-DD'
    """
    year_range = range(MIN_POSSIBLE_YEAR, MAX_POSSIBLE_YEAR + 1)  # last excluded
    #   http://infostrefa.com/infostrefa/pl/raporty/espi/firmy/3,2007,0,0,1
    url_base = 'http://infostrefa.com/infostrefa/pl/raporty/espi/firmy'
    for year in year_range:
        url = f'{url_base}/{company_id},{year},0,0,1'
        page = requests.get(url)
        if page.status_code != 200:
            print(f'Error retrieving page. Status code: {page.status_code}')
            return None
        soup = BeautifulSoup(page.content, 'html.parser')
        hrefs = soup.find_all('tbody')
        assert len(hrefs) == 3, 'Something went wrong. Bad assumption.'
        href = hrefs[1]
        scraped_company_name = _scrape_company_name_from_tbody_href(href)
        if scraped_company_name:
            return scraped_company_name


def _scrape_company_name_from_tbody_href(href) -> str or None:
    tags = [el for el in href if type(el) is Tag]
    dates_idxs = [i for i in range(len(tags)) if date_regex_with_dots.findall(tags[i].text)]
    for i in range(len(dates_idxs) - 1):
        company_name_from_date = _scrape_company_name_from_a_given_date(tags[dates_idxs[i]: dates_idxs[i + 1]])
        if company_name_from_date:
            return company_name_from_date


def _scrape_company_name_from_a_given_date(tags) -> str or None:
    date = date_regex_with_dots.findall(tags[0].text)
    for i in range(1, len(tags)):
        hrefs = tags[i].find_all('a')
        company_name = hrefs[0].text
        return company_name


if __name__ == '__main__':
    for i, company_name in enumerate(COMPANY_NAME_TO_ID):
        company_infos = scrape_sources_for_company(company_name, year_start=2015, year_end=2015)
        write_json(f'{company_name}.json', company_infos)
        if i == 5:
            break
