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
    Generates a dataset
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
    data_counter = 0
    annotated_companies: Dict[str, DatasetLike] = {}  # name of a company to dataset.
    for filename in os.listdir(annotated_data_dir):
        fp = f"{annotated_data_dir}/{filename}"
        annotated_company = load_json(fp)
        annotated_companies[filename[:ENDING_CHARS_LEN]] = annotated_company
        data_counter += len(annotated_company)

    if not shuffle_companies:
        company_names = [company_name for company_name in annotated_companies]
        # Shuffle companies means that the companies are shuffled between train / dev / test sets.
        # Here, the datasets are shuffled, but the company data stays together.
        # So the result will be that company A is in train set, company B is in dev set,
        # company C is in test set.
        random.shuffle(company_names)
        test_data_amount = test_size * data_counter
        val_data_amount = val_size * data_counter

    if shuffle_companies:
        annotated_data = []
        for annotated_company in annotated_companies:
            annotated_data.extend(annotated_companies[annotated_company])
        random.shuffle(annotated_data)



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
    generate_financial_dataset(0.05, negative_threshold=-0.05, shuffle_companies=True)