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
            message['content'] = raport_content

            if not raport_content:
                return None

        elif company_tag in prev_token_text:
            company_name = token.text.strip().replace('.', '')

            if not company_name:
                return None

            if company_name not in included_companies:
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


def get_included_companies(included_companies_path):
    included_companies = load_json(included_companies_path)
    included_companies_collection = set()
    for included_company in included_companies:
        company_name = included_company.get('company_name').upper()
        included_companies_collection.add(company_name)

    return included_companies_collection


start_id = 468320
end_id = 468330
url_base = 'http://infostrefa.com/espi/pl/reports/view/4,'
messages = []
failed_counter = 0

included_companies_path = 'data/corresponding_stocks.json'
included_companies_collection = get_included_companies(included_companies_path)
for i in tqdm(range(end_id - start_id)):

    url = url_base + str(start_id + i)
    message = scrape_message_from_infosfera(url, included_companies_collection)
    if message:
        messages.append(message)
    else:
        failed_counter = failed_counter + 1

    start_id = start_id + 1
    time.sleep(30)

write_json('data/infosfera/scrapped_messages.json', messages)
print('Nie pobrano danych dla ', failed_counter, ' firm')
