from typing import Tuple, Dict, Union, List

import torch
from abc import ABC, abstractmethod
from sklearn.model_selection import train_test_split

from src.common.data_preparation import read_klej, KlejType, generate_financial_dataset

TorchDataset = torch.utils.data.Dataset
DatasetLike = List[Dict[str, Union[str, int]]]


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


class Dataset(ABC):

    def __init__(self, tokenizer):
        self.tokenizer = tokenizer

    def prepare_data_sets(
            self,
            train_data: DatasetLike,
            test_data: DatasetLike,
            val_data: DatasetLike
    ) -> Tuple[SentimentAnalysisDataset, SentimentAnalysisDataset, SentimentAnalysisDataset]:
        """
        Returns train, dev, test datasets ready to pass into Trainer API for transformers.
        :param tokenizer: Transformers tokenizer.
        :param train_data: Training labelled data
        :param test_data: Test labelled data
        :param val_data: Validation labelled data
        :return: Tuple of datasets objects in order: Train, Dev, Test.
        """
        train_texts, train_labels = _get_texts_labels_from_data(train_data)
        val_texts, val_labels = _get_texts_labels_from_data(val_data)
        test_texts, test_labels = _get_texts_labels_from_data(test_data)

        label_mapper = {label: i for i, label in enumerate(set(train_labels))}

        train_labels = [label_mapper[label] for label in train_labels]
        val_labels = [label_mapper[label] for label in val_labels]
        test_labels = [label_mapper[label] for label in test_labels]

        train_encodings = self.tokenizer(train_texts, truncation=True, padding=True)
        val_encodings = self.tokenizer(val_texts, truncation=True, padding=True)
        test_encodings = self.tokenizer(test_texts, truncation=True, padding=True)

        train_dataset = SentimentAnalysisDataset(train_encodings, train_labels)
        val_dataset = SentimentAnalysisDataset(val_encodings, val_labels)
        test_dataset = SentimentAnalysisDataset(test_encodings, test_labels)

        return train_dataset, val_dataset, test_dataset

    @abstractmethod
    def get(self) -> Tuple[SentimentAnalysisDataset, SentimentAnalysisDataset, SentimentAnalysisDataset]:
        pass


class KlejDataset(Dataset):

    def __init__(
            self,
            tokenizer,
            klej_type: KlejType,
            klej_labels: Tuple[str, ...] = ("positive", "negative", "neutral"),
            validation_size: float = 0.1,
            random_state: int = 42):
        """
        :param tokenizer: Transformers tokenizer.
        :param klej_type: One of KlejType values.
        :param klej_labels: Tuple of klej type labels that will be used for the training / eval.
        :param validation_size: A part of training dataset that will be used as validation set.
        :param random_state: random state that makes the experiments repeatable.
        """
        self.klej_type = klej_type
        self.klej_labels = klej_labels
        self.validation_size = validation_size
        self.random_state = random_state

        super().__init__(tokenizer)

    def get(self) -> Tuple[SentimentAnalysisDataset, SentimentAnalysisDataset, SentimentAnalysisDataset]:
        """
        Returns train, dev, test datasets generated from klej_dataset ready to pass into Trainer API for transformers.
        :return: Tuple of datasets objects in order: Train, Dev, Test.
        """
        klej_in = read_klej(self.klej_type, self.klej_labels)
        train_data, test_data = klej_in["train"], klej_in["dev"]

        train_data, val_data = train_test_split(
            train_data,
            test_size=self.validation_size,
            random_state=self.random_state,
            stratify=[d["label"] for d in train_data])

        return super().prepare_data_sets(train_data, test_data, val_data)


class FinancialDataset(Dataset):

    def __init__(
            self,
            tokenizer,
            positive_threshold: float = 0.2,
            negative_threshold: float = -0.2,
            shuffle_companies: bool = False,
            test_size: float = 0.2,
            val_size: float = 0.1,
            random_state: int = 42,
            annotated_data_dir: str = "data/annotated"):
        """
        :param tokenizer: Transformer tokenizer
        :param positive_threshold: Lowest value for positive sentiment
        :param negative_threshold: Highest value for negative sentiment
        :param shuffle_companies: Decides whether companies should be shuffled between
        train / dev / test sets or used in only one of them.
        :param test_size: float between 0-1. A fraction of the dataset that should be used as test set.
        :param val_size: float between 0-1. A fraction of the dataset that should be used as validation set.
        :param random_state: Seed used for generating random split of companies
        :param annotated_data_dir: path to the annotated data.
        """

        self.positive_threshold = positive_threshold
        self.negative_threshold = negative_threshold
        self.shuffle_companies = shuffle_companies
        self.test_size = test_size
        self.val_size = val_size
        self.random_state = random_state
        self.annotated_data_dir = annotated_data_dir

        super().__init__(tokenizer)

    def get(self) -> Tuple[SentimentAnalysisDataset, SentimentAnalysisDataset, SentimentAnalysisDataset]:
        """
        Prepares financial data_sets to be passed to Bert model
        :return: Tuple of datasets objects in order: Train, Dev, Test.
        """

        train_data, test_data, val_data = generate_financial_dataset(self.positive_threshold, self.negative_threshold,
                                                                     self.shuffle_companies, self.test_size,
                                                                     self.val_size, self.random_state,
                                                                     self.annotated_data_dir)
        return super().prepare_data_sets(train_data, test_data, val_data)


def get_klej_test_set(
        klej_type: KlejType,
        klej_labels: Tuple[str, ...] = ("positive", "negative", "neutral")) -> Tuple[List[str], List[int]]:
    klej = read_klej(klej_type, klej_labels)
    label_mapper = {label: i for i, label in enumerate(klej_labels)}
    test_data = klej["dev"]
    test_texts, test_labels = _get_texts_labels_from_data(test_data)
    return test_texts, [label_mapper[label] for label in test_labels]


def _get_texts_labels_from_data(
        data: List[Dict[str, Union[str, int]]]) -> Tuple[List[str], List[int]]:
    texts = [d["text"] for d in data]
    labels = [d["label"] for d in data]
    return texts, labels
