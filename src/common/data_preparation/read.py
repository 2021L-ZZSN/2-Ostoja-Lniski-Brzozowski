from enum import Enum, auto
from typing import Dict, List, Union, Tuple


class KlejType(Enum):
    IN = auto()
    OUT = auto()


KLEJ_TYPE_TO_PATH = {
    KlejType.IN: "data/klej_polemo2.0-in",
    KlejType.OUT: "data/klej_polemo2.0-out"
}

KLEJ_FILE_LABEL_TO_LABEL = {
    "__label__meta_amb": "amb",
    "__label__meta_plus_m": "positive",
    "__label__meta_zero": "neutral",
    "__label__meta_minus_m": "negative"
}


def read_klej(
        klej_type: KlejType,
        labels_to_return: Tuple[str, ...]
) -> Dict[str, List[Dict[str, Union[str, int]]]]:
    """
    Reads klej dataset from klej_polemo2.0.
    :param klej_type: KlejType.IN or KlejType.OUT.
    :param labels_to_return: List of labels to return. Possible values: "amb", "positive", "neutral", "negative".
    :return: Train, dev data in a form of:
    {
        "train": [
            {
                "text": "sample text",
                "label": One of: ["amb", "positive", "negative", "neutral"]
            }
            ...
        ],

        "dev": [...],
    }

    test_features.tsv are currently not used.
    """
    dir_path = KLEJ_TYPE_TO_PATH.get(klej_type)
    return {
        'train': _read_klej_file(f'{dir_path}/train.tsv', labels_to_return=labels_to_return),
        'dev': _read_klej_file(f'{dir_path}/dev.tsv', labels_to_return=labels_to_return)
    }


def _read_klej_file(
        filepath: str,
        labels_to_return: Tuple[str, ...]) -> List[Dict[str, Union[str, int]]]:
    result = []
    with open(filepath, "r") as f:
        lines = f.readlines()[1:]  # first line contains column names
        for line in lines:
            text, label = line.split('\t')
            label = KLEJ_FILE_LABEL_TO_LABEL.get(label.strip())
            if label in labels_to_return:
                result.append({
                    "text": text.strip(),
                    "label": label
                })
    return result
