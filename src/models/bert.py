from transformers import AutoTokenizer, Trainer, BertForSequenceClassification, TrainingArguments

from src.common.data_preparation import KlejType
from src.models import MODEL_USED
from src.models.metrics import compute_metrics
from src.models.datasets import KlejDataset, FinancialDataset

OUTPUT_DIR = "my_model"


def main():
    tokenizer = AutoTokenizer.from_pretrained(MODEL_USED)

    # dataset = KlejDataset(tokenizer=tokenizer, klej_type=KlejType.IN)
    dataset = FinancialDataset(tokenizer=tokenizer, positive_threshold=0.012, negative_threshold=-0.033,
                               shuffle_companies=False)
    train_dataset, val_dataset, test_dataset = dataset.get()

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

    trainer.save_model(OUTPUT_DIR)

    tokenizer.save_pretrained(OUTPUT_DIR)

    print(trainer.evaluate(eval_dataset=test_dataset))


if __name__ == "__main__":
    main()
