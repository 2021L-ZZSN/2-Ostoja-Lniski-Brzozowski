from typing import Dict, Union, List, Tuple
import os
from random import shuffle, random
import random
from src.common.utils.files_io import load_json

random.seed(42)

DatasetLike = List[Dict[str, Union[str, int]]]

ENDING_CHARS_LEN = len("_annotated.json")


def generate_financial_dataset(
        positive_threshold: float,
        negative_threshold: float,
        shuffle_companies: bool,
        test_size: float = 0.2,
        val_size: float = 0.1,
        annotated_data_dir: str = "data/annotated"
) -> Tuple[DatasetLike, DatasetLike, DatasetLike]:
    """
    Generates a tuple of datasets
    :param positive_threshold: A threshold for "sentiment" attribute from which
    we say that the StockExchangeDispatch is a positive one.
    :param negative_threshold: A threshold for "sentiment" attribute to which
    we say that the StockExchangeDispatch is a negative one. For values between
    positive_threshold and negative_threshold we say that it is a neutral one.
    :param shuffle_companies: Decides whether companies should be shuffled between
    train / dev / test sets or used in only one of them.
    :param test_size: float between 0-1. A fraction of the dataset that should be used as test set.
    :param val_size: float between 0-1. A fraction of the dataset that should be used as validation set.
    :param annotated_data_dir: path to the annotated data.
    :return: Train, val, test datasets. Each of them is a list of dict with items:
    {
        "text": "the text",
        "label": "positive / neutral / negative"
    }
    """

    if test_size < 0 or val_size < 0 or test_size + val_size >= 1:
        raise ValueError('Test size and val size should be non-negative and sum up to less than one')

    annotated_data_num = 0
    annotated_companies_data: Dict[str, DatasetLike] = {}  # name of a company to dataset.
    for filename in os.listdir(annotated_data_dir):
        file_path = f"{annotated_data_dir}/{filename}"
        annotated_companies = load_json(file_path)

        for annotated_company in annotated_companies:
            company_name, content, sentiment = _read_single_annotated_data_file(
                annotated_company, positive_threshold, negative_threshold)

            if company_name not in annotated_companies_data.keys():
                annotated_companies_data[company_name] = []

            annotated_companies_data[company_name].append({'text': content, 'label': sentiment})
            annotated_data_num += 1

    train_data = []
    val_data = []
    test_data = []

    # Shuffle companies means that the companies are shuffled between train / dev / test sets.
    # Here, the datasets are shuffled, but the company data stays together.
    # So the result will be that company A is in train set, company B is in dev set,
    # company C is in test set.
    if not shuffle_companies:
        company_names = [company_name for company_name in annotated_companies_data]
        random.shuffle(company_names)

        next_id = 0
        next_id, test_data = _get_non_shuffled_required_data(annotated_companies_data, company_names,
                                                             next_id, annotated_data_num * test_size)

        next_id, val_data = _get_non_shuffled_required_data(annotated_companies_data, company_names,
                                                            next_id, annotated_data_num * val_size)

        _, train_data = _get_non_shuffled_required_data(annotated_companies_data, company_names,
                                                        next_id, annotated_data_num)

        return train_data, test_data, val_data

    if shuffle_companies:
        annotated_data = []
        for annotated_company in annotated_companies_data:
            annotated_data.extend(annotated_companies_data[annotated_company])
        random.shuffle(annotated_data)


def _read_single_annotated_data_file(
        annotated_company: dict,
        positive_threshold: float,
        negative_threshold: float):
    """
    Reads the content of annotated data file
    :param annotated_company: current company
    :param positive_threshold: Lowest value for positive sentiment
    :param negative_threshold: Highest value for negative sentiment
    :return: company_name, content, sentiment
    """
    company_name = annotated_company['company_name']
    report_content = annotated_company['content']
    sentiment_value = annotated_company['sentiment']
    sentiment_label = _apply_label_for_sentiment(sentiment_value, positive_threshold, negative_threshold)

    return company_name, report_content, sentiment_label


def _get_non_shuffled_required_data(
        annotated_companies_data: Dict[str, DatasetLike],
        companies: list,
        company_id: int,
        requirement: float):
    """
    Returns data starting from a company of given id, until requirement is met
    :param companies: A dictionary of annotations for given company
    :param companies: Companies to be analysed
    :param company_id: Highest value for negative sentiment
    :param requirement: minimal number of needed annotated data items
    :return: first not analysed company, List of dicts containing content and message for given company
    """
    companies_data = []
    current_data_size = 0
    while current_data_size < requirement and company_id < len(companies):
        company_name = companies[company_id]
        annotated_info = annotated_companies_data[company_name]
        companies_data += _generate_company_full_data(annotated_companies_data, company_name)

        current_data_size += len(annotated_info)
        company_id += 1

    return company_id, companies_data


def _generate_company_full_data(
        annotated_companies_data: Dict[str, DatasetLike],
        company_name: str
):
    """
    Returns full annotated information for given company name
    :param annotated_companies_data: Annotated companies
    :param company_name: Company name
    :return: List of dicts containing content and message for given company
    """

    company_full_data = []
    for company_data in annotated_companies_data[company_name]:
        company_full_data.append({'text': company_data['text'],
                                  'label': company_data['label']})

    return company_full_data


def _create_labels_for_data(
        positive_threshold: float,
        negative_threshold: float,
        dataset: DatasetLike) -> DatasetLike:
    return [
        {
            "text": sample["text"],
            "label": _apply_label_for_sentiment(
                sentiment=sample["sentiment"],
                positive_threshold=positive_threshold,
                negative_threshold=negative_threshold)
        }
        for sample in dataset
    ]


def _apply_label_for_sentiment(
        sentiment: float,
        positive_threshold: float,
        negative_threshold: float) -> str:
    if negative_threshold >= positive_threshold:
        raise ValueError("Negative threshold cannot be equal or greater than positive threshold!")
    if sentiment <= negative_threshold:
        return "negative"
    if negative_threshold < sentiment < positive_threshold:
        return "neutral"
    return "positive"


if __name__ == '__main__':
    generate_financial_dataset(0.05, negative_threshold=-0.05, shuffle_companies=False)
