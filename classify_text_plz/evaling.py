import statistics
import abc
from typing import Iterable, Sequence, Dict, List, Tuple, Union
from classify_text_plz.dataing import MyTextData, DataSplit, MyTextDataSplit
from classify_text_plz.modeling import TextModelTrained, Prediction
from classify_text_plz.typehelpers import CLASS_LABEL_TYPE


class PlzTextMetric(abc.ABC):
    @abc.abstractmethod
    def score(
        self,
        expected: Iterable[CLASS_LABEL_TYPE],
        predicted: Iterable[Prediction]
    ) -> float:
        pass

    def __str__(self):
        return self.__class__.__name__

    def metric_name(self):
        return self.__class__.__name__


class Accuracy(PlzTextMetric):
    def score(
        self,
        expected: Iterable[CLASS_LABEL_TYPE],
        predicted: Iterable[Prediction]
    ) -> float:
        return statistics.mean(int(gt == p.most_probable_label()) for gt, p in zip(expected, predicted))


class Recall(PlzTextMetric):
    def __init__(
        self,
        pos_class: CLASS_LABEL_TYPE,
    ):
        self._pos_class = pos_class

    def score(
        self,
        expected: Iterable[CLASS_LABEL_TYPE],
        predicted: Iterable[Prediction]
    ) -> float:
        return statistics.mean(
            int(gt == p.most_probable_label())
            for gt, p in zip(expected, predicted)
            if gt == self._pos_class
        )


class EvalResult:
    def __init__(
        self,
        model: TextModelTrained,
        metrics: Dict[DataSplit, Dict[PlzTextMetric, float]],
        predictions: Dict[DataSplit, List[Tuple[Tuple[str, CLASS_LABEL_TYPE], Prediction]]],
    ):
        self.model = model
        self.metrics = metrics
        self.predictions = predictions


class PlzEvaluator:
    def __init__(
        self,
        metrics: Sequence[PlzTextMetric] = (Accuracy(), ),
        default_dump_split_highest_loss: Dict[Union[DataSplit, str], int] = None,
    ):
        self.metrics = metrics
        self.default_dump_split_highest_loss = default_dump_split_highest_loss or {
            DataSplit.VAL: 10,
            DataSplit.TEST: 10,
        }

    def print_eval(
        self,
        data: MyTextData,
        model: TextModelTrained,
        #splits: Sequence[DataSplit] = (DataSplit.TRAIN, DataSplit.VAL),
        dump_split_highest_loss: Dict[DataSplit, int] = None,
        dump_split_lowest_loss: Dict[DataSplit, int] = None,
    ) -> EvalResult:
        all_predictions = {split_key: [] for split_key, _ in data.get_all_splits()}
        all_metrics = {split_key: {} for split_key, _ in data.get_all_splits()}
        for split_key, split_data in data.get_all_splits():
            print(f"="*40)
            print("~"*5 + f" Split {split_key}")
            #if split_key in (DataSplit.TRAIN, DataSplit.VAL, DataSplit.TEST):
            #    print("SKIP")
            #    continue
            predictions = [model.predict_text(text) for text in split_data.get_text()]
            for metric in self.metrics:
                score = metric.score(split_data.get_labels(), predictions)
                print(f"{metric}: {score}")
                all_metrics[split_key][metric.metric_name()] = score
            all_predictions[split_key] = list(zip(split_data.get_text_and_labels(), predictions))
            correct_prob = [
                pred.get_prob_of(gt) for gt, pred in zip(split_data.get_labels(), predictions)
            ]
            correct_prob_and_example = sorted(zip(
                correct_prob,
                split_data.get_text_and_labels(),
                predictions
            ), key=lambda v: v[0])
            if dump_split_highest_loss is None:
                dump_split_highest_loss = self.default_dump_split_highest_loss
            if dump_split_lowest_loss is None:
                dump_split_lowest_loss = {
                    DataSplit.VAL: 3,
                    DataSplit.TEST: 0,
                }
            num_high = dump_split_highest_loss.get(split_key, 0)
            if num_high:
                print(f"-" * 3)
                print(f"Highest {num_high} loss predictions:")
                for prob, (text, gt), pred in correct_prob_and_example[:num_high]:
                    print(f"Correct {prob}: {(text, gt)} pred {pred.most_probable_label()}")
            num_low = dump_split_lowest_loss.get(split_key, 0)
            if num_low:
                print(f"-" * 40)
                print(f"Lowest {num_low} loss predictions:")
                for prob, (text, gt), pred in reversed(correct_prob_and_example[-num_low:]):
                    print(f"Correct {prob}: {(text, gt)} pred {pred.most_probable_label()}")
        return EvalResult(model, all_metrics, all_predictions)

