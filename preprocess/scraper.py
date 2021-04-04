import requests
from bs4 import BeautifulSoup
import re

COMPANY_NAME = 'Skrócona nazwa emitenta'
REPORT_TAG = 'Treść raportu'
DATE_REGEX = '\d\d\d\d-\d\d-\d\d'  # YYYY-MM-DD


def scrape_company_info_from_infosfera(url, included_companies) -> dict:
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    company_info = scrape_company_info(soup, included_companies)
    company_info['date'] = _scrape_date(soup)
    return company_info


def scrape_company_info(soup, included_companies):
    prev_token_text = ''
    company_info = {}
    for token in soup.find_all(class_='nTekst'):

        if REPORT_TAG in prev_token_text:
            company_info['content'] = _get_report_content(token)
        elif COMPANY_NAME in prev_token_text:
            company_info['company_name'] = _get_included_company_name(token, included_companies)

        prev_token_text = token.text

    if 'content' not in company_info or 'company_name' not in company_info:
        raise ScrapperError('No company name or content')

    return company_info


def _get_report_content(token):
    report_content = token.text.strip()
    if not report_content:
        raise ScrapperError('No content')

    return report_content


def _get_included_company_name(token, included_companies):
    company_name = token.text.strip().replace('.', '')
    if not company_name:
        raise ScrapperError('No company name')

    if company_name not in included_companies and company_name + ' SA' not in included_companies:
        raise ScrapperError('Company name excluded')

    return company_name


def _scrape_date(soup):
    regexp_date = re.compile(DATE_REGEX)
    for token in soup.find_all(class_='nDokument'):
        dates = regexp_date.findall(token.text)
        if dates:
            return dates[0]

    raise ScrapperError('No date found')


class ScrapperError(Exception):
    pass
