import click
from click import STRING, INT
from transformers import AutoTokenizer, Trainer, BertForSequenceClassification, TrainingArguments

from src.common.data_preparation import KlejType
from src.models import MODEL_USED
from src.models.datasets import KlejDataset, FinancialDataset
from src.models.metrics import compute_metrics


@click.command()
@click.option(
    "-o",
    "--output_dir",
    type=STRING,
    required=True,
    help="Directory where a model and tokenizer will be stored stored."
)
@click.option(
    "--train_dataset",
    type=click.Choice(["klej_in", "financial_mixed", "financial"]),
    required=True,
    help="Choose the dataset for the training."
)
@click.option(
    "--epochs",
    type=INT,
    default=3,
    help="Choose the number of epochs."
)
@click.option(
    "--batch_size",
    type=INT,
    default=8,
    help="Choose the batch size."
)
@click.option(
    "--eval_batch_size",
    type=INT,
    default=8,
    help="Choose the eval batch size."
)
def main(
        output_dir: STRING,
        train_dataset: click.Choice,
        epochs: INT,
        batch_size: INT,
        eval_batch_size: INT
):
    tokenizer = AutoTokenizer.from_pretrained(MODEL_USED)

    model = BertForSequenceClassification.from_pretrained(MODEL_USED, num_labels=3)

    training_args = TrainingArguments(
        output_dir='./results',
        num_train_epochs=epochs,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=eval_batch_size,
        warmup_steps=500,
        weight_decay=0.01,
        logging_dir='./logs',
        logging_steps=10,
    )
    dataset = (
        KlejDataset(
            tokenizer=tokenizer,
            klej_type=KlejType.IN,
        )
        if "klej" in train_dataset
        else FinancialDataset(
            tokenizer=tokenizer,
            shuffle_companies="mixed" in train_dataset
        )
    )
    train, val, test = dataset.get()

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train,
        eval_dataset=val,
        compute_metrics=compute_metrics,

    )

    trainer.train()

    trainer.save_model(output_dir)

    tokenizer.save_pretrained(output_dir)

    print(trainer.evaluate(eval_dataset=test))


if __name__ == "__main__":
    main()
