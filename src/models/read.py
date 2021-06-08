from typing import Tuple

from transformers import PreTrainedTokenizer, PreTrainedModel, AutoConfig, AutoTokenizer, BertForSequenceClassification


def read_from_dir(model_dir: str) -> Tuple[PreTrainedTokenizer, PreTrainedModel]:
    """
    Reads model and tokenizer from a path on the local machine.
    :param model_dir: path to the dir where tokenizer and model are stored
    :return: tokenizer and model saved in the src dir.
    """
    print('Loading configuraiton...')
    model_config = AutoConfig.from_pretrained(model_dir)
    print('Loading tokenizer...')
    tokenizer = AutoTokenizer.from_pretrained(model_dir)
    print('Loading model...')
    model = BertForSequenceClassification.from_pretrained(
        model_dir,
        config=model_config
    )
    return tokenizer, model
