from typing import Dict, List, Tuple, Union

import numpy as np
from transformers import PreTrainedModel, PreTrainedTokenizer

from src.common.data_preparation import KlejType
from src.models.datasets import get_klej_test_set
from src.models.metrics import compute_metrics, get_classification_report, get_confusion_matrix
from src.models.read import read_from_dir

MODEL_PATH = "klej_model"


def _get_model_predictions(model: PreTrainedModel,
                           encodings) -> np.array:
    model.eval()
    predictions = model(**encodings)
    return predictions.logits.detach().numpy()


def _gather_prediction(text: Union[str, List[str]], tokenizer: PreTrainedTokenizer, model: PreTrainedModel) -> np.array:
    encoding = tokenizer(text, padding=True, truncation=True, return_tensors="pt")
    return _get_model_predictions(model, encoding)


def evaluate(
        tokenizer: PreTrainedTokenizer,
        model: PreTrainedModel,
        test_dataset: Tuple[List[str], List[int]]) -> Dict[str, float]:
    texts, labels = test_dataset
    if not texts:
        return {}
    predictions = []
    for text in texts:
        prediction = _gather_prediction(text, tokenizer, model)
        predictions.append(prediction)
    predictions = np.squeeze(np.array(predictions), axis=1)
    eval_pred = (predictions, labels)
    print(get_classification_report(eval_pred))
    print(get_confusion_matrix(eval_pred))
    return compute_metrics(eval_pred)


if __name__ == '__main__':
    tokenizer, model = read_from_dir(MODEL_PATH)
    test_dataset = get_klej_test_set(KlejType.IN)
    print(evaluate(tokenizer, model, test_dataset))