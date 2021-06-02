from typing import Dict, List

from tokenizers.normalizers import Sequence

from classify_text_plz.classifiers.bow_logreg import BowModelLogRegressModel
from classify_text_plz.classifiers.deeplearn.bertbaseline import BertlikeModelMaker
from classify_text_plz.classifiers.fasttext_baseline import FastTextModelMaker
from classify_text_plz.classifiers.stupid_classifiers import MostCommonClassModelMaker, RandomGuessModelMaker
from classify_text_plz.classifiers.tfidf_nn import TfidfKnnModelMaker
from classify_text_plz.dataing import MyTextData, DataSplit, MyTextDataSplit
from classify_text_plz.evaling import PlzEvaluator, PlzTextMetric, EvalResult
from classify_text_plz.modeling import TextModelMaker


def classify_this_plz(
    data: MyTextData,
    evaluator: PlzEvaluator = None,
    include_test_split: bool = False,
    extra_model_maker: List[TextModelMaker] = None,
) -> Dict[str, EvalResult]:
    evaluator = PlzEvaluator() if evaluator is None else evaluator
    all_results = {}
    for model_maker, dump_vals in [
        #(MostCommonClassModelMaker(), False),

        #(RandomGuessModelMaker(), False),
        #(BowModelLogRegressModel(), True),
        #(TfidfKnnModelMaker(k=2), True),
        #(FastTextModelMaker(epoch=10, wordNgrams=3), True),

        #(BertlikeModelMaker('bert-base-uncased', epoch=3), True),
    ] + list((zip(extra_model_maker, [True]*len(extra_model_maker)) if extra_model_maker else [])):
        model = model_maker.fit(data)
        print(f"#"*80)
        print(f"Evaluate model {model.get_model_name()}")
        eval_result = evaluator.print_eval(
            data,
            model,
            #splits=[DataSplit.TRAIN, DataSplit.VAL] + ([DataSplit.TEST] if include_test_split else []),
            dump_split_highest_loss=None if dump_vals else {},
            dump_split_lowest_loss=None if dump_vals else {},
        )
        all_results[model.get_model_name()] = eval_result
    return all_results