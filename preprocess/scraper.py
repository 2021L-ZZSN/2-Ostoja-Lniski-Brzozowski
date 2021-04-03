import requests
from bs4 import BeautifulSoup
import re
from utils.files_io import write_json, load_json
from tqdm import tqdm
import time

COMPANY_NAME = 'Skrócona nazwa emitenta'
REPORT_TAG = 'Treść raportu'


class ScrapperError(Exception):
    pass


def get_report_content(token):
    report_content = token.text.strip()
    if not report_content:
        raise ScrapperError('No content')

    return report_content


def get_included_company_name(token, included_companies):
    company_name = token.text.strip().replace('.', '')
    if not company_name:
        raise ScrapperError('No company name')

    if company_name not in included_companies and company_name + ' SA' not in included_companies:
        raise ScrapperError('Company name excluded')

    return company_name


def scrape_company_info(soup, included_companies):
    prev_token_text = ''
    company_info = {}
    for token in soup.find_all(class_='nTekst'):

        if REPORT_TAG in prev_token_text:
            company_info['content'] = get_report_content(token)
        elif COMPANY_NAME in prev_token_text:
            company_info['company_name'] = get_included_company_name(token, included_companies)

        prev_token_text = token.text

    if 'content' not in company_info or 'company_name' not in company_info:
        raise ScrapperError('No company name or content')

    return company_info


def scrape_date(soup):
    regexp_date = re.compile("\d\d\d\d-\d\d-\d\d")
    for token in soup.find_all(class_='nDokument'):
        dates = regexp_date.findall(token.text)
        if dates:
            return dates[0]

    raise ScrapperError('No date found')


def scrape_company_info_from_infosfera(url, included_companies):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    company_info = scrape_company_info(soup, included_companies)
    company_info['date'] = scrape_date(soup)
    return company_info


def get_included_companies(filepath):
    included_companies = load_json(filepath)
    result = set()
    for included_company in included_companies:
        company_name = included_company.get('company_name').upper()
        result.add(company_name)

    return result


def scrape_sources_with_given_ids(url_base, first_included, first_excluded):
    infos = []
    failed_counter = 0
    requests_in_row = 10
    request_pause = 30

    for i in tqdm(range(first_excluded - first_included)):

        try:
            url = url_base + str(first_included + i)
            company_info = scrape_company_info_from_infosfera(url, get_included_companies('data/corresponding_stocks.json'))
            infos.append(company_info)
        except ScrapperError:
            failed_counter = failed_counter + 1

        if i % requests_in_row == requests_in_row - 1:
            time.sleep(request_pause)

    print('Nie pobrano danych dla ', failed_counter, ' firm')
    return infos


if __name__ == '__main__':
    scraped_data = scrape_sources_with_given_ids('http://infostrefa.com/espi/pl/reports/view/4,', 428320, 428329)
    write_json('data/infosfera/scrapped_messages.json', scraped_data)
