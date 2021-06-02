import nltk
from sklearn.pipeline import Pipeline

from classify_text_plz.dataing import MyTextData, DataSplit
from classify_text_plz.modeling import TextModelTrained, Prediction, TextModelMaker


def preproc_for_bow(text: str):
    text = " ".join(nltk.tokenize.word_tokenize(text))
    text = text.strip()
    return text


class PlzScikitModelMaker(TextModelMaker):
    def __init__(self):
        self._pipeline = None
        self._name = self.__class__.__name__

    def fit(self, data: MyTextData) -> TextModelTrained:
        index_to_label = list(set(data.get_split_data(DataSplit.TRAIN).get_labels()))
        label_to_index = {
            label: i
            for i, label in enumerate(index_to_label)
        }
        self._pipeline.fit(
            [
                #preproc_for_bow(txt)
                txt
                for txt in data.get_split_data(DataSplit.TRAIN).get_text()
            ],
            [
                label_to_index[label]
                for label in data.get_split_data(DataSplit.TRAIN).get_labels()
            ]
        )
        return PlzTrainedScikitModel(self._name, self._pipeline, index_to_label)


class PlzTrainedScikitModel(TextModelTrained):
    def __init__(self, name: str, model: Pipeline, index_to_label):
        self._name, self._model, self._label_map = name, model, index_to_label

    def predict_text(self, text: str):
        #pred = self._model.predict_proba([preproc_for_bow(text)])[0]
        pred = self._model.predict_proba([text])[0]
        #print(pred)
        return Prediction(
            label_to_prob={
                label: score
                for label, score in zip(self._label_map, pred)
            },
            presorted=False,
            guarantee_all_classes=True
        )

    def get_model_name(self) -> str:
        return self._name