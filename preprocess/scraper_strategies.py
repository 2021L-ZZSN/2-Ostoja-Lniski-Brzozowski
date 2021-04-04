import time
from typing import List

from bs4.element import Tag
from tqdm import tqdm
import re
from preprocess.scraper import scrape_dispatch_from_url, scrape_dispatch_from_url_within_included_companies
from preprocess.scraper_utils import get_included_companies, ScrapperError, get_page_root
from utils.files_io import write_json, load_json

DOTTED_DATE_REGEX = re.compile('\d\d\.\d\d\.\d\d\d\d')

MIN_POSSIBLE_YEAR = 2004
MAX_POSSIBLE_YEAR = 2021

CORRESPONDING_STOCKS = load_json('data/corresponding_stocks.json')
COMPANY_NAME_TO_ID = {el['company_name']: el['company_infosfera_id'] for el in CORRESPONDING_STOCKS}
COMPANY_BASE_URL = 'http://infostrefa.com/infostrefa/pl/raporty/espi/firmy'


def scrape_dispatches_using_ids(
        url_base: str,
        first_included: int,
        first_excluded: int,
        requests_in_row: int = 10,
        sleep_between_requests: int = 30) -> List[dict]:
    """
    This function is used for scraping infosfera directly by dispatch IDs.
    :param url_base: str
    :param first_included: first id
    :param first_excluded: first not included id
    :param requests_in_row: How many requests in an iteration (This is for avoiding getting blocked by infosfera)
    :param sleep_between_requests: how long to sleep before hitting infosfera again
    :return: List of dispatches: date, content, company_name
    """
    company_infos = []
    failed_counter = 0

    for i in tqdm(range(first_excluded - first_included)):

        try:
            url = url_base + str(first_included + i)
            company_info = scrape_dispatch_from_url_within_included_companies(
                url=url,
                included_companies=get_included_companies())
            company_infos.append(company_info)
        except ScrapperError:
            failed_counter = failed_counter + 1

        if i % requests_in_row == requests_in_row - 1:
            time.sleep(sleep_between_requests)

    print('Nie pobrano danych dla ', failed_counter, ' firm')
    return company_infos


def scrape_dispatches_for_company(company_name: str, year_start=MIN_POSSIBLE_YEAR, year_end=MAX_POSSIBLE_YEAR):
    """
    This function is used for scraping infosfera by company_name between given years.
    :param company_name: str
    :param year_start: int
    :param year_end: int
    :return: List of dispatches: date, content, company_name
    """
    year_range = range(year_start, year_end + 1)
    scraped_dispatches_all = []
    for year in year_range:
        assert company_name in COMPANY_NAME_TO_ID, 'Such company name was not found in corresponding_stocks.json.'
        # currently only scraping first site (if too many stock dispatches for a given year, infosfera uses pagination)
        company_dispatches_tag = _get_tag_containing_company_dispatches(
            company_id=COMPANY_NAME_TO_ID[company_name], year=year, page=1)
        scraped_dispatches = _scrape_company_dispatches_from_company_dispatches_tag(company_dispatches_tag)
        if scraped_dispatches:
            scraped_dispatches_all.extend(scraped_dispatches)
    return scraped_dispatches_all


def scrape_company_name(company_id: int) -> str or None:
    """
    Scrap dispatches from a given date.
    """
    year_range = range(MIN_POSSIBLE_YEAR, MAX_POSSIBLE_YEAR + 1)
    for year in year_range:
        company_dispatches_tag = _get_tag_containing_company_dispatches(company_id=company_id, year=year, page=1)
        scraped_company_name = _scrape_company_name_from_company_dispatches_tag(company_dispatches_tag)
        if scraped_company_name:
            return scraped_company_name


def _get_tag_containing_company_dispatches(company_id, year, page=1):
    url = f'{COMPANY_BASE_URL}/{company_id},{year},0,0,{page}'
    page_root = get_page_root(url)
    # It's the easiest way to reach company dispatches info by using tbody tag.
    tbodies = page_root.find_all('tbody')
    # Each tested website had 3 tbody sections. For us, the important one was the second containing company dispatches.
    assert len(tbodies) == 3, 'Something went wrong. Each report should contain 3 tbody sections.'
    company_dispatches_tag = tbodies[1]
    return company_dispatches_tag


def _scrape_company_dispatches_from_company_dispatches_tag(company_dispatches_tag) -> List[dict]:
    company_dispatches_from_date_all = []
    tags = [el for el in company_dispatches_tag if type(el) is Tag]
    # There are two types of tags in our use case: - One contains date. - All other contain dispatches.
    dates_tag_idxs = [i for i in range(len(tags)) if DOTTED_DATE_REGEX.findall(tags[i].text)]
    for i in tqdm(range(len(dates_tag_idxs) - 1)):
        company_dispatches_from_date = _scrape_company_dispatches_from_a_given_day(
            tags[dates_tag_idxs[i]: dates_tag_idxs[i + 1]])
        if company_dispatches_from_date:
            company_dispatches_from_date_all.extend(company_dispatches_from_date)
    return company_dispatches_from_date_all


def _scrape_company_dispatches_from_a_given_day(tags) -> List[dict]:
    company_dispatches = []
    for i in range(1, len(tags)):
        hreftags = tags[i].find_all('a')
        # This might seem like a bad idea, but it's the easiest way to retrieve a dispatch URL
        tags_to_scrape = [tag for tag in hreftags if tag['href'].startswith('http://')]
        for tag in tags_to_scrape:
            try:
                company_dispatches.append(scrape_dispatch_from_url(url=tag['href']))
            except ScrapperError:
                pass
    return company_dispatches


def _scrape_company_name_from_company_dispatches_tag(company_dispatches_tag) -> str or None:
    tags = [el for el in company_dispatches_tag if type(el) is Tag]
    # There are two types of tags in our use case: - One contains date. - All other contain dispatches.
    dates_tag_idxs = [i for i in range(len(tags)) if DOTTED_DATE_REGEX.findall(tags[i].text)]
    for i in range(len(dates_tag_idxs) - 1):
        tags_from_single_day = tags[dates_tag_idxs[i]: dates_tag_idxs[i + 1]]
        company_name = _scrape_company_name_from_a_given_day(tags_from_single_day)
        # if for some reason tags from a given day does not contain company name, we continue searching.
        if company_name:
            return company_name


def _scrape_company_name_from_a_given_day(tags) -> str or None:
    # We start looking from the second tag, since 1st should always contain date - not company name.
    for i in range(1, len(tags)):
        href_tags = tags[i].find_all('a')
        # First tag after date should contain company name.
        company_name = href_tags[0].text
        return company_name


if __name__ == '__main__':
    year_start = 2015
    year_end = 2015
    first_idx_included = 0
    first_idx_exluded = 10
    for i, company_name in enumerate(COMPANY_NAME_TO_ID):
        if first_idx_included <= i < first_idx_exluded:
            print(f'Scraping dispatches for: {company_name} from {year_start} to {year_end}')
            company_infos = scrape_dispatches_for_company(company_name, year_start=year_start, year_end=year_end)
            write_json(f'{company_name}.json', company_infos)
