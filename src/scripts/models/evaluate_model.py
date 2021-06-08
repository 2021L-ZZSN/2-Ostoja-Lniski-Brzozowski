import click
from click import STRING, INT

from src.common.data_preparation import KlejType
from src.models import read_from_dir
from src.models.datasets import get_klej_test_set, get_financial_test_set
from src.models.eval import evaluate


@click.command()
@click.option(
    "-i",
    "--input_dir",
    type=STRING,
    required=True,
    help="Directory where a model and tokenizer is stored."
)
@click.option(
    "--test_dataset",
    type=click.Choice(["klej_in", "klej_out", "financial_mixed", "financial"]),
    required=True,
    help="Choose the dataset for the evaluation."
)
@click.option(
    "--eval_batch",
    type=INT,
    default=10,
    help="Choose your evaluation batch size. Default to 10."
)
def main(
        input_dir: STRING,
        test_dataset: click.Choice,
        eval_batch: INT
):
    tokenizer, model = read_from_dir(input_dir)
    if "klej" in test_dataset:
        test_dataset = get_klej_test_set(
            klej_type=KlejType.IN if test_dataset == "klej_in" else KlejType.OUT
        )
    else:
        test_dataset = get_financial_test_set(
            shuffle_companies="mixed" in test_dataset,
        )
    evaluation_result = evaluate(
        test_dataset=test_dataset,
        tokenizer=tokenizer,
        model=model,
        batch_size=eval_batch
    )
    print(f"Confusion matrix: \n {evaluation_result['confusion_matrix']}")
    print(f"Classification report \n {evaluation_result['classification_report']}")


if __name__ == '__main__':
    main()
