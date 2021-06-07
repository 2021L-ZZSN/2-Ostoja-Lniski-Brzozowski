from transformers import AutoTokenizer, Trainer, BertForSequenceClassification, TrainingArguments

from src.common.data_preparation import KlejType
from src.models import MODEL_USED
from src.models.metrics import compute_metrics
from src.models.datasets import get_klej_datasets


def main():
    tokenizer = AutoTokenizer.from_pretrained(MODEL_USED)

    train_dataset, val_dataset, test_dataset = get_klej_datasets(
        tokenizer=tokenizer,
        klej_type=KlejType.IN,
    )

    training_args = TrainingArguments(
        output_dir='./results',
        num_train_epochs=3,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=16,
        warmup_steps=500,
        weight_decay=0.01,
        logging_dir='./logs',
        logging_steps=10,
    )

    model = BertForSequenceClassification.from_pretrained(MODEL_USED, num_labels=3)

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        compute_metrics=compute_metrics,

    )

    trainer.train()

    trainer.save_model("model")

    print(trainer.evaluate(eval_dataset=test_dataset))
