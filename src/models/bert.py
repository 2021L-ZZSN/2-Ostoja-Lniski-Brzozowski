from transformers import AutoTokenizer, Trainer, BertForSequenceClassification, BertConfig, TrainingArguments

from src.common.consts import RANDOM_STATE
from src.common.data_preparation import KlejType, read_klej
import torch
from sklearn.model_selection import train_test_split
from src.models import MODEL_USED
VALIDATION_SIZE = 0.1
tokenizer = AutoTokenizer.from_pretrained(MODEL_USED)
klej_in = read_klej(KlejType.IN, ("positive", "negative", "neutral"))
train_data, test_data = klej_in["train"], klej_in["dev"]

train_data, val_data = train_test_split(
    train_data,
    test_size=VALIDATION_SIZE,
    random_state=RANDOM_STATE,
    stratify=[d["label"] for d in train_data])

train_texts = [d["text"] for d in train_data]
train_labels = [d["label"] for d in train_data]

val_texts = [d["text"] for d in train_data]
val_labels = [d["label"] for d in train_data]


test_texts = [d["text"] for d in test_data]
test_labels = [d["label"] for d in test_data]

label_mapper = {label: i for i, label in enumerate(set(test_labels))}

train_labels = [label_mapper[label] for label in train_labels]
val_labels = [label_mapper[label] for label in val_labels]
test_labels = [label_mapper[label] for label in test_labels]

train_encodings = tokenizer(train_texts, truncation=True, padding=True)
val_encodings = tokenizer(val_texts, truncation=True, padding=True)
test_encodings = tokenizer(test_texts, truncation=True, padding=True)


class KlejDataset(torch.utils.data.Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.labels)


train_dataset = KlejDataset(train_encodings, train_labels)
val_dataset = KlejDataset(val_encodings, val_labels)
test_dataset = KlejDataset(test_encodings, test_labels)

training_args = TrainingArguments(
    output_dir='./results',          # output directory
    num_train_epochs=3,              # total number of training epochs
    per_device_train_batch_size=16,  # batch size per device during training
    per_device_eval_batch_size=64,   # batch size for evaluation
    warmup_steps=500,                # number of warmup steps for learning rate scheduler
    weight_decay=0.01,               # strength of weight decay
    logging_dir='./logs',            # directory for storing logs
    logging_steps=10,
)

model = BertForSequenceClassification.from_pretrained(MODEL_USED, num_labels=3)


trainer = Trainer(
    model=model,                         # the instantiated 🤗 Transformers model to be trained
    args=training_args,                  # training arguments, defined above
    train_dataset=train_dataset,         # training dataset
    eval_dataset=val_dataset             # evaluation dataset
)

trainer.train()
