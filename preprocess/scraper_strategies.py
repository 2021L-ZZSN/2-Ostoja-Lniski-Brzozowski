import time
from typing import List

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
from tqdm import tqdm
import re
from preprocess.scraper import scrape_company_info_from_infosfera, ScrapperError
from preprocess.scraper_utils import get_included_companies
from utils.files_io import write_json, append_json

date_regex_with_dots = re.compile('\d\d\.\d\d\.\d\d\d\d')


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


def scrape_company_name(company_id: int) -> str or None:
    """
    Scrap dispatches from a given date.
    :param date: 'YYYY-MM-DD'
    """
    year_range = range(2004, 2022)  # last excluded
    #   http://infostrefa.com/infostrefa/pl/raporty/espi/firmy/3,2007,0,0,1
    url_base = 'http://infostrefa.com/infostrefa/pl/raporty/espi/firmy'
    for year in year_range:
        url = f'{url_base}/{company_id},{year},0,0,1'
        page = requests.get(url)
        if page.status_code != 200:
            print(f'page not found. {page.status_code}')
            return None
        soup = BeautifulSoup(page.content, 'html.parser')
        hrefs = soup.find_all('tbody')
        assert len(hrefs) == 3, 'Something went wrong. Bad assumption.'
        href = hrefs[1]
        scraped_company_name = scrape_company_name_from_tbody_href(href)
        if scraped_company_name:
            return scraped_company_name


def scrape_company_name_from_tbody_href(href) -> str or None:
    tags = [el for el in href if type(el) is Tag]
    dates_idxs = [i for i in range(len(tags)) if date_regex_with_dots.findall(tags[i].text)]
    for i in range(len(dates_idxs) - 1):
        company_name_from_date = scrape_company_name_from_a_given_date(tags[dates_idxs[i]: dates_idxs[i + 1]])
        if company_name_from_date:
            return company_name_from_date


def scrape_company_name_from_a_given_date(tags) -> str or None:
    date = date_regex_with_dots.findall(tags[0].text)
    for i in range(1, len(tags)):
        hrefs = tags[i].find_all('a')
        company_name = hrefs[0].text
        return company_name


if __name__ == '__main__':
    # scraped_data = scrape_sources_with_given_ids('http://infostrefa.com/espi/pl/reports/view/4,', 428320, 428329)
    # write_json('data/infosfera/scrapped_messages.json', scraped_data)
    for i in range(1821, 2101):
        company_name = scrape_company_name(i)
        append_json('200_companies.json', {i: company_name})
