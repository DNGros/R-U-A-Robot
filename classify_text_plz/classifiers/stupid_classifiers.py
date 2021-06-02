from collections import Counter
from typing import Dict

from classify_text_plz.modeling import TextModelTrained, TextModelMaker, Prediction
from classify_text_plz.dataing import MyTextData, DataSplit
import statistics

from classify_text_plz.typehelpers import CLASS_LABEL_TYPE
from classify_text_plz.util import normalize_dict_vals
import random


class MostCommonClassModelMaker(TextModelMaker):
    def fit(self, data: MyTextData) -> TextModelTrained:
        train_labels = data.get_split_data(DataSplit.TRAIN).get_labels()
        class_probs = normalize_dict_vals(Counter(train_labels))
        return AlwaysMostCommonModelTrained(class_probs)


class AlwaysMostCommonModelTrained(TextModelTrained):
    def __init__(self, return_probs):
        self._return_val = Prediction(return_probs)

    def predict_text(self, text: str):
        return self._return_val

    def __str__(self):
        return f"<Model Always Return '{self._return_val.most_probable_label()}'>"


class RandomGuessModelMaker(TextModelMaker):
    def fit(self, data: MyTextData) -> TextModelTrained:
        train_labels = data.get_split_data(DataSplit.TRAIN).get_labels()
        class_probs = normalize_dict_vals(Counter(train_labels))
        return RandomGuessTrained(class_probs)


class RandomGuessTrained(TextModelTrained):
    def __init__(self, return_probs: Dict[CLASS_LABEL_TYPE, float]):
        self._class_probs = return_probs

    def predict_text(self, text: str):
        #guess = WeightedR
        guess = random.choices(
            tuple(self._class_probs.keys()), weights=tuple(self._class_probs.values()), k=1)[0]
        probs = {
            label: 0.0 if label != guess else 1.0
            for label in self._class_probs.keys()
        }
        return Prediction(probs)

    def __str__(self):
        return f"<RandomGuess>"

