from typing import Tuple, Dict, Union, List

import torch
from sklearn.model_selection import train_test_split

from src.common.data_preparation import read_klej, KlejType

TorchDataset = torch.utils.data.Dataset


class SentimentAnalysisDataset(TorchDataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.labels)


def get_klej_datasets(
        tokenizer,
        klej_type: KlejType,
        klej_labels: Tuple[str, ...] = ("positive", "negative", "neutral"),
        validation_size: float = 0.1,
        random_state: int = 42,
) -> Tuple[SentimentAnalysisDataset, SentimentAnalysisDataset, SentimentAnalysisDataset]:
    """
    Returns train, dev, test datasets ready to pass into Trainer API for transformers.
    :param tokenizer: Transformers tokenizer.
    :param klej_type: One of KlejType values.
    :param klej_labels: Tuple of klej type labels that will be used for the training / eval.
    :param validation_size: A part of training dataset that will be used as validation set.
    :param random_state: random state that makes the experiments repeatable.
    :return: Tuple of datasets objects in order: Train, Dev, Test.
    """
    klej_in = read_klej(klej_type, klej_labels)
    train_data, test_data = klej_in["train"], klej_in["dev"]

    train_data, val_data = train_test_split(
        train_data,
        test_size=validation_size,
        random_state=random_state,
        stratify=[d["label"] for d in train_data])

    train_texts, train_labels = _get_texts_labels_from_data(train_data)
    val_texts, val_labels = _get_texts_labels_from_data(val_data)
    test_texts, test_labels = _get_texts_labels_from_data(test_data)

    label_mapper = {label: i for i, label in enumerate(set(train_labels))}

    train_labels = [label_mapper[label] for label in train_labels]
    val_labels = [label_mapper[label] for label in val_labels]
    test_labels = [label_mapper[label] for label in test_labels]

    train_encodings = tokenizer(train_texts, truncation=True, padding=True)
    val_encodings = tokenizer(val_texts, truncation=True, padding=True)
    test_encodings = tokenizer(test_texts, truncation=True, padding=True)

    train_dataset = SentimentAnalysisDataset(train_encodings, train_labels)
    val_dataset = SentimentAnalysisDataset(val_encodings, val_labels)
    test_dataset = SentimentAnalysisDataset(test_encodings, test_labels)

    return train_dataset, val_dataset, test_dataset


def _get_texts_labels_from_data(
        data: List[Dict[str, Union[str, int]]]) -> Tuple[List[str], List[int]]:
    texts = [d["text"] for d in data]
    labels = [d["label"] for d in data]
    return texts, labels
