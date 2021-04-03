import requests
from bs4 import BeautifulSoup
import re
from utils.files_io import write_json, load_json
from tqdm import tqdm
import time


def scrape_message_from_infosfera(url, included_companies):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    company_tag = 'Skrócona nazwa emitenta'
    raport_tag = 'Treść raportu'

    prev_token_text = ''
    message = {}

    for token in soup.find_all(class_='nTekst'):

        if raport_tag in prev_token_text:
            raport_content = token.text.strip()
            if not raport_content:
                return None

            message['content'] = raport_content

        elif company_tag in prev_token_text:
            company_name = token.text.strip().replace('.', '')

            if not company_name:
                return None

            if company_name not in included_companies and company_name + ' SA' not in included_companies:
                return None

            message['company_name'] = company_name

        prev_token_text = token.text

    regexp_date = re.compile("\d\d\d\d-\d\d-\d\d")
    for token in soup.find_all(class_='nDokument'):
        dates = regexp_date.findall(token.text)
        if dates:
            message['date'] = dates[0]
            break

    return message


def get_included_companies(filepath):
    included_companies = load_json(filepath)
    result = set()
    for included_company in included_companies:
        company_name = included_company.get('company_name').upper()
        result.add(company_name)

    return result


def scrape_sources_with_given_ids(url_base, first_included, first_excluded):

    messages = []
    failed_counter = 0
    requests_in_row = 10
    request_pause = 30

    for i in tqdm(range(first_excluded - first_included)):

        url = url_base + str(first_included + i)
        message = scrape_message_from_infosfera(url, get_included_companies('data/corresponding_stocks.json'))
        if message:
            messages.append(message)
        else:
            failed_counter = failed_counter + 1

        if i % requests_in_row == requests_in_row - 1:
            time.sleep(request_pause)

    print('Nie pobrano danych dla ', failed_counter, ' firm')
    return messages


if __name__ == '__main__':
    scraped_data = scrape_sources_with_given_ids('http://infostrefa.com/espi/pl/reports/view/4,', 468220, 468330)
    write_json('data/infosfera/scrapped_messages.json', scraped_data)
