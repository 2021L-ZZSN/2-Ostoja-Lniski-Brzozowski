from utils.files_io import load_json

DEFAULT_INCLUDED_COMPANIES_PATH = 'data/corresponding_stocks.json'


def get_included_companies(filepath=DEFAULT_INCLUDED_COMPANIES_PATH) -> set:
    included_companies = load_json(filepath)
    result = set()
    for included_company in included_companies:
        company_name = included_company.get('company_name').upper()
        result.add(company_name)

    return result
