from enum import Enum, auto
from typing import Dict, List, Tuple, Union


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


def read_klej(klej_type: KlejType) -> Dict[str, List[Dict[str, Union[str, int]]]]:
    """
    Reads klej dataset from klej_polemo2.0.
    :param klej_type: KlejType.IN or KlejType.OUT.
    :return: Train, dev, test data in a form of:
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
        'train': _read_klej_file(f'{dir_path}/train.tsv'),
        'dev': _read_klej_file(f'{dir_path}/dev.tsv')
    }


def _read_klej_file(filepath: str) -> List[Dict[str, Union[str, int]]]:
    result = []
    with open(filepath, "r") as f:
        lines = f.readlines()[1:]  # first line contains column names
        for line in lines:
            text, label = line.split('\t')
            result.append({
                "text": text.strip(),
                "label": KLEJ_FILE_LABEL_TO_LABEL.get(label.strip())
            })
    return result
