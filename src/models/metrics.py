import numpy as np
from sklearn import metrics


def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    return {
        "f1": metrics.f1_score(y_pred=predictions, y_true=labels, average="weighted"),
        "recall": metrics.recall_score(y_pred=predictions, y_true=labels, average="weighted"),
        "precision": metrics.precision_score(y_pred=predictions, y_true=labels, average="weighted"),
        "accuracy": metrics.accuracy_score(y_pred=predictions, y_true=labels)
    }
