from pathlib import Path
import torch
from typing import List, Iterable, Mapping, Union

from torch.utils.data import Dataset
from transformers import BertForSequenceClassification, BertTokenizerFast, AutoTokenizer, \
    AutoModelForSequenceClassification, DistilBertForSequenceClassification, DistilBertTokenizer, \
    DistilBertTokenizerFast, EvaluationStrategy, BertTokenizer

from classify_text_plz.dataing import MyTextData, DataSplit
from transformers import BertForSequenceClassification, BertTokenizerFast, Trainer, TrainingArguments
import numpy as np
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

from classify_text_plz.modeling import TextModelMaker, TextModelTrained, Prediction
from classify_text_plz.typehelpers import CLASS_LABEL_TYPE

cur_file = Path(__file__).parent.absolute()


def make_pt_dataset(
    text: Iterable[str],
    labels: List[int],
    tokenizer: Union[BertTokenizerFast, BertTokenizer],
    max_length: int,
):
    text = list(text)
    assert len(text) == len(labels)
    is_fast = isinstance(tokenizer, BertTokenizerFast)
    tokenized = tokenizer(text, padding=True, truncation=True, max_length=max_length)

    class _InnerDataset(Dataset):
        def __len__(self):
            return len(text)

        def __getitem__(self, idx: int):
            if is_fast:
                v = tokenized[idx]
                return {
                    "input_ids": v.ids,
                    "attention_mask": v.attention_mask,
                    "label": labels[idx]
                }
            return {
                "input_ids": tokenized.input_ids[idx],
                "attention_mask": tokenized.attention_mask[idx],
                "label": labels[idx]
            }

    return _InnerDataset()


class BertlikeModelMaker(TextModelMaker):
    def __init__(
        self,
        model_name: str = "bert-base-uncased",
        epoch: int = 3,
        model_override = None,
        tokenizer_override = None,
    ):
        self.model_name = model_name
        self.epoch = epoch
        self.model_override = model_override
        self.tokenizer_override = tokenizer_override

    def fit(self, data: MyTextData) -> TextModelTrained:
        # Hastily adapted from https://colab.research.google.com/drive/1-JIJlao4dI-
        #   Ilww_NnTc0rxtp-ymgDgM?usp=sharing#scrollTo=N8J-TLhBuaOf
        index_to_label = list(set(data.get_split_data(DataSplit.TRAIN).get_labels()))
        label_to_index = {
            label: i
            for i, label in enumerate(index_to_label)
        }
        #model = DistilBertForSequenceClassification.from_pretrained(
        #    self.model_name, num_labels=len(index_to_label))
        #tokenizer = DistilBertTokenizerFast.from_pretrained(self.model_name)
        model = self.model_override or BertForSequenceClassification.from_pretrained(
            self.model_name, num_labels=len(index_to_label))
        tokenizer = self.tokenizer_override or BertTokenizerFast.from_pretrained(self.model_name)

        def proc_labels(lables):
            return [label_to_index[l] for l in lables]

        def compute_metrics(pred):
            labels = pred.label_ids
            preds = pred.predictions.argmax(-1)
            precision, recall, f1, _ = precision_recall_fscore_support(labels, preds, average='weighted')
            acc = accuracy_score(labels, preds)
            r = {
                'accuracy': acc,
                'f1': f1,
                'precision': precision,
                'recall': recall
            }
            print(r)
            return r

        training_args = TrainingArguments(
            #output_dir=str(cur_file / "../outputs/newbert"),
            # TODO make good eval file
            output_dir=str(Path("~/plzouts/newbert").expanduser()),
            num_train_epochs=self.epoch,

            #per_device_train_batch_size=4,
            #per_device_eval_batch_size=8,
            per_device_train_batch_size=8,
            per_device_eval_batch_size=8,

            warmup_steps=500,
            weight_decay=0.01,
            #evaluate_during_training=True,
            #evaluate_during_training=False,
            evaluation_strategy=EvaluationStrategy.EPOCH,
            fp16=False,
            logging_dir=str(Path("~/plzouts/berlogs").expanduser()),
            #logging_dir=str(cur_file / "../outputs/newbertlogs"),
        )

        trainer = Trainer(
            model=model,
            args=training_args,
            compute_metrics=compute_metrics,
            train_dataset=make_pt_dataset(
                data.get_split_data(DataSplit.TRAIN).get_text(),
                proc_labels(data.get_split_data(DataSplit.TRAIN).get_labels()),
                tokenizer,
                max_length=model.config.max_position_embeddings
            ),
            eval_dataset=make_pt_dataset(
                data.get_split_data(DataSplit.VAL).get_text(),
                proc_labels(data.get_split_data(DataSplit.VAL).get_labels()),
                tokenizer,
                max_length=model.config.max_position_embeddings
            ),
        )

        if self.epoch > 0:
            trainer.train()

        return BertlikeTrainedModel(model, tokenizer, index_to_label, self.model_name)


class BertlikeTrainedModel(TextModelTrained):
    def __init__(
        self,
        model: BertForSequenceClassification,
        tokenizer: BertTokenizerFast,
        label_map: List[CLASS_LABEL_TYPE],
        name: str,
    ):
        self._model, self._tokenizer, self._label_map = model, tokenizer, label_map
        self._model.eval()
        self._name = name

    def predict_text(self, text: str) -> Prediction:
        tokenized = self._tokenizer(
            [text], padding=True, truncation=True,
            return_tensors="pt",
            max_length=self._model.config.max_position_embeddings,
        )
        #print(tokenized)
        with torch.no_grad():
            p = self._model(
                input_ids=tokenized['input_ids'].to(self._model.device),
                attention_mask=tokenized['attention_mask'].to(self._model.device)
            )
        return Prediction({
            self._label_map[i]: float(prob)
            for i, prob in enumerate(torch.softmax(p[0][0], dim=0))
        })

    def get_model_name(self) -> str:
        return f"{self.__class__.__name__}={self._name}"
