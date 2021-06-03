import re
from typing import Set

from src.preprocess.scraper_utils import ScrapperError, get_page_root

COMPANY_NAME = 'Skrócona nazwa emitenta'
REPORT_TAG = 'Treść raportu'
DATE_REGEX = '\d\d\d\d-\d\d-\d\d'  # YYYY-MM-DD


def scrape_dispatch_from_url_within_included_companies(url: str, included_companies: Set[str]) -> dict:
    dispatch = scrape_dispatch_from_url(url)
    company_name = dispatch['company_name']
    if company_name not in included_companies and company_name + ' SA' not in included_companies:
        raise ScrapperError('Company name excluded')
    return dispatch


def scrape_dispatch_from_url(url) -> dict:
    page_root = get_page_root(url)
    dispatch = {}
    prev_token_text = ''
    for nTekst_tag in page_root.find_all(class_='nTekst'):

        if REPORT_TAG in prev_token_text:
            dispatch['content'] = _get_dispatch_content(nTekst_tag)
        elif COMPANY_NAME in prev_token_text:
            dispatch['company_name'] = _get_company_name(nTekst_tag)

        prev_token_text = nTekst_tag.text

    dispatch['date'] = _get_date(page_root)

    if 'content' not in dispatch or 'company_name' not in dispatch or 'date' not in dispatch:
        raise ScrapperError('Data incomplete.')

    return dispatch


def _get_dispatch_content(nTekst_tag):
    report_content = nTekst_tag.text.strip()
    if not report_content:
        raise ScrapperError('No content')

    return report_content


def _get_company_name(nTekst_tag):
    company_name = nTekst_tag.text.strip().replace('.', '')
    if not company_name:
        raise ScrapperError('No company name')

    return company_name


def _get_date(page_root):
    regexp_date = re.compile(DATE_REGEX)
    for token in page_root.find_all(class_='nDokument'):
        dates = regexp_date.findall(token.text)
        if dates:
            return dates[0]

    raise ScrapperError('No date found')
