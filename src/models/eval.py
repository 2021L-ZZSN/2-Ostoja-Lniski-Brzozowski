from typing import Dict

from transformers import PreTrainedModel

from src.common.data_preparation import KlejType
from src.models.datasets import SentimentAnalysisDataset, get_klej_datasets
from src.models.metrics import compute_metrics, get_classification_report, get_confusion_matrix
from src.models.read import read_from_dir
import numpy as np

MODEL_PATH = "klej_model"


def _get_model_predictions(model: PreTrainedModel,
                           encodings) -> np.array:
    model.eval()
    predictions = model(**encodings)
    return predictions.logits.detach().numpy()


def evaluate(
        model: PreTrainedModel,
        test_dataset: SentimentAnalysisDataset) -> Dict[str, float]:
    encodings = test_dataset.encodings
    labels = test_dataset.labels
    predictions = _get_model_predictions(model, encodings)
    eval_pred = (predictions, labels)
    print(get_classification_report(eval_pred))
    print(get_confusion_matrix(eval_pred))
    return compute_metrics(eval_pred)


if __name__ == '__main__':
    tokenizer, model = read_from_dir(MODEL_PATH)
    _, _, test_dataset = get_klej_datasets(tokenizer, KlejType.IN)
    print(evaluate(model, test_dataset))