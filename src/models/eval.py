from typing import Dict, List, Tuple, Union

import numpy as np
from tqdm import tqdm
from transformers import PreTrainedModel, PreTrainedTokenizer

from src.models.metrics import get_classification_report, get_confusion_matrix


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
        test_dataset: Tuple[List[str], List[int]],
        batch_size: int = 10) -> Dict[str, float]:
    """
    Evaluates the dataset and returns a dict containing classification_report and confusion matrix.
    :param tokenizer: tokenizer used for model training.
    :param model: model for evaluation.
    :param test_dataset: test dataset for evaluation.
    :param batch_size: evaluation batch size.
    :return: dict with keys: 'classification_report' and 'confusion_matrix'
    """
    texts, labels = test_dataset
    if not texts:
        return {}
    predictions = []
    stop = len(texts) if len(texts) % batch_size == 0 else len(texts) + batch_size
    for i in tqdm(range(batch_size, stop, batch_size)):
        texts_batch = texts[i - batch_size: i]
        prediction = _gather_prediction(texts_batch, tokenizer, model)
        predictions.append(prediction)
    predictions = np.array(predictions)
    predictions = np.concatenate(predictions, axis=0)
    eval_pred = (predictions, labels)
    return {
        'classification_report': get_classification_report(eval_pred),
        'confusion_matrix': get_confusion_matrix(eval_pred)
    }
