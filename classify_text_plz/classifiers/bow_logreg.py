import nltk
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.linear_model import LogisticRegression

from classify_text_plz.classifiers.scikithelpers import preproc_for_bow, PlzTrainedScikitModel, \
    PlzScikitModelMaker
from classify_text_plz.dataing import MyTextData, DataSplit
from classify_text_plz.modeling import TextModelMaker, TextModelTrained
from sklearn.pipeline import Pipeline


class BowModelLogRegressModel(PlzScikitModelMaker):
    def __init__(self):
        super().__init__()
        self._name = "BOWLogisticRegression"
        self._pipeline = Pipeline([
            ('vect', CountVectorizer(
                analyzer='word',
                tokenizer=nltk.tokenize.word_tokenize,
                lowercase=True
            )),
            ('tfidf', TfidfTransformer()),
            ('clf', LogisticRegression()),
        ])
