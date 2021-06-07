from transformers import AutoConfig, AutoTokenizer, BertForSequenceClassification

from src.common.data_preparation import KlejType
from src.models.datasets import get_klej_datasets
MODEL_PATH = "klej_model"

print('Loading configuraiton...')
model_config = AutoConfig.from_pretrained(MODEL_PATH)
print('Loading tokenizer...')

tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)

print('Loading model...')
model = BertForSequenceClassification.from_pretrained(MODEL_PATH,
                                                      config=model_config)

prompt = "Bardzo fajna restauracja polecam 10/10"

encoding = tokenizer(prompt, truncation=True, padding=True, return_tensors="pt")
outputs = model(**encoding)
print(outputs)