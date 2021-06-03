import time
from typing import List, Optional

from bs4.element import Tag
from tqdm import tqdm
import re

from src.common.consts import COMPANY_NAME_TO_ID
from src.common.stock_dispatch import StockExchangeDispatch
from src.api.scraper.scrapers import scrape_dispatch_from_url, scrape_dispatch_from_url_within_included_companies
from src.api.scraper.scraper_utils import get_included_companies, ScrapperError, get_page_root

DOTTED_DATE_REGEX = re.compile('\d\d\.\d\d\.\d\d\d\d')


_COMPANY_BASE_URL = 'http://infostrefa.com/infostrefa/pl/raporty/espi/firmy'


def scrape_dispatches_using_ids(
        url_base: str,
        first_included: int,
        first_excluded: int,
        requests_in_row: int = 10,
        sleep_between_requests: int = 30) -> List[StockExchangeDispatch]:
    """
    This function is used for scraping infosfera dispatches directly by dispatch IDs.
    :param url_base: base url from which the scraping will be performed.
    :param first_included: first id included.
    :param first_excluded: first id excluded.
    :param requests_in_row: How many requests in an iteration (This is for avoiding getting blocked by infosfera)
    :param sleep_between_requests: sleeptime between sending requests to infosfera website (in sec).
    :return: List of StockExchangeDispatch objects without sentiment field.
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


def scrape_dispatches_for_company(
        company_name: str,
        year_start: int,
        year_end: int,
        sleep_time: int = 10) -> List[StockExchangeDispatch]:
    """
    This function is used for scraping infosfera by company_name between given years.
    :param company_name: The name of the company to be scraped.
    :param year_start: starting year for the scraping process.
    :param year_end: last year for the scraping process (inclusive).
    :param sleep_time: sleep between scraping given days (in sec).
    :return: List of StockExchangeDispatch objects without sentiment field.
    """
    year_range = range(year_start, year_end + 1)
    scraped_dispatches_all = []
    for year in year_range:
        assert company_name in COMPANY_NAME_TO_ID, 'Such company name was not found in corresponding_stocks.json.'
        # currently only scraping first site (if too many stock dispatches for a given year, infosfera uses pagination)
        company_dispatches_tag = _get_tag_containing_company_dispatches(
            company_id=COMPANY_NAME_TO_ID[company_name], year=year, page=1)
        scraped_dispatches = _scrape_company_dispatches_from_company_dispatches_tag(
            company_dispatches_tag, sleep_time=sleep_time)
        if scraped_dispatches:
            scraped_dispatches_all.extend(scraped_dispatches)
    return scraped_dispatches_all


def _get_tag_containing_company_dispatches(company_id, year, page=1):
    url = f'{_COMPANY_BASE_URL}/{company_id},{year},0,0,{page}'
    page_root = get_page_root(url)
    # It's the easiest way to reach company dispatches info by using tbody tag.
    tbodies = page_root.find_all('tbody')
    # Each tested website had 3 tbody sections. For us, the important one was the second containing company dispatches.
    assert len(tbodies) == 3, 'Something went wrong. Each report should contain 3 tbody sections.'
    company_dispatches_tag = tbodies[1]
    return company_dispatches_tag


def _scrape_company_dispatches_from_company_dispatches_tag(
        company_dispatches_tag, sleep_time: int) -> List[StockExchangeDispatch]:
    company_dispatches_from_date_all = []
    tags = [el for el in company_dispatches_tag if type(el) is Tag]
    # There are two types of tags in our use case: - One contains date. - All other contain dispatches.
    dates_tag_idxs = [i for i in range(len(tags)) if DOTTED_DATE_REGEX.findall(tags[i].text)]
    for i in tqdm(range(len(dates_tag_idxs) - 1)):
        company_dispatches_from_date = _scrape_company_dispatches_from_a_given_day(
            tags[dates_tag_idxs[i]: dates_tag_idxs[i + 1]], sleep_time=sleep_time)
        if company_dispatches_from_date:
            company_dispatches_from_date_all.extend(company_dispatches_from_date)
    return company_dispatches_from_date_all


def _scrape_company_dispatches_from_a_given_day(tags, sleep_time: int) -> List[StockExchangeDispatch]:
    company_dispatches = []
    for i in range(1, len(tags)):
        hreftags = tags[i].find_all('a')
        # This might seem like a bad idea, but it's the easiest way to retrieve a dispatch URL
        tags_to_scrape = [tag for tag in hreftags if tag['href'].startswith('http://')]
        for tag in tags_to_scrape:
            try:
                time.sleep(sleep_time)
                company_dispatches.append(scrape_dispatch_from_url(url=tag['href']))
            except ScrapperError:
                pass
    return company_dispatches


def scrape_company_name(
        company_id: int,
        min_possible_year: int,
        max_possible_year: int) -> Optional[str]:
    """
    Scrap dispatches in search of a match between a company name and id.
    :param company_id id of a company for which the company name will be returned.
    :param min_possible_year year to start the search with.
    :param max_possible_year year to end the search with (inclusive).
    :return company name if found between given years. None otherwise.

    Note:
    This was used to create a match between a company id and name.
    It's usage is not recommended anymore.
    """
    year_range = range(min_possible_year, max_possible_year + 1)
    for year in year_range:
        company_dispatches_tag = _get_tag_containing_company_dispatches(company_id=company_id, year=year, page=1)
        scraped_company_name = _scrape_company_name_from_company_dispatches_tag(company_dispatches_tag)
        if scraped_company_name:
            return scraped_company_name


def _scrape_company_name_from_company_dispatches_tag(company_dispatches_tag) -> Optional[str]:
    tags = [el for el in company_dispatches_tag if type(el) is Tag]
    # There are two types of tags in our use case: - One contains date. - All other contain dispatches.
    dates_tag_idxs = [i for i in range(len(tags)) if DOTTED_DATE_REGEX.findall(tags[i].text)]
    for i in range(len(dates_tag_idxs) - 1):
        tags_from_single_day = tags[dates_tag_idxs[i]: dates_tag_idxs[i + 1]]
        company_name = _scrape_company_name_from_a_given_day(tags_from_single_day)
        # if for some reason tags from a given day does not contain company name, we continue searching.
        if company_name:
            return company_name


def _scrape_company_name_from_a_given_day(tags) -> Optional[str]:
    # We start looking from the second tag, since 1st should always contain date - not company name.
    for i in range(1, len(tags)):
        href_tags = tags[i].find_all('a')
        # First tag after date should contain company name.
        company_name = href_tags[0].text
        return company_name
