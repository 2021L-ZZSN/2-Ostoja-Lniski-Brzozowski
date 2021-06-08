import numpy as np
from sklearn import metrics
from sklearn.metrics import classification_report, confusion_matrix

from src.models.datasets import DEFAULT_POSSIBLE_LABELS


def compute_metrics(eval_pred: tuple):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    print(get_confusion_matrix((predictions, labels)))
    return {
        "f1": metrics.f1_score(y_pred=predictions, y_true=labels, average="macro"),
        "recall": metrics.recall_score(y_pred=predictions, y_true=labels, average="macro"),
        "precision": metrics.precision_score(y_pred=predictions, y_true=labels, average="macro"),
        "accuracy": metrics.accuracy_score(y_pred=predictions, y_true=labels)
    }


def get_classification_report(eval_pred: tuple):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    # If our default 3 values are used, show target names, if not - don't
    target_names = DEFAULT_POSSIBLE_LABELS if len(logits) and len(logits[0]) == 3 else None
    return classification_report(labels, predictions, target_names=target_names)


def get_confusion_matrix(eval_pred: tuple):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    return confusion_matrix(labels, predictions)
