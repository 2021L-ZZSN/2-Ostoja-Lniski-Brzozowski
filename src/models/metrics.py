import numpy as np
from sklearn import metrics
from sklearn.metrics import classification_report, confusion_matrix


def compute_metrics(eval_pred: tuple):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    return {
        "f1": metrics.f1_score(y_pred=predictions, y_true=labels, average="weighted"),
        "recall": metrics.recall_score(y_pred=predictions, y_true=labels, average="weighted"),
        "precision": metrics.precision_score(y_pred=predictions, y_true=labels, average="weighted"),
        "accuracy": metrics.accuracy_score(y_pred=predictions, y_true=labels)
    }


def get_classification_report(eval_pred: tuple):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    return classification_report(labels, predictions)


def get_confusion_matrix(eval_pred: tuple):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    return confusion_matrix(labels, predictions)
