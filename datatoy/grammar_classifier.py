"""The interface for the grammar-based classifier"""
from typing import Optional
from pprint import pprint

import attr
from enum import Enum

from templates.ambigious_grammar import get_amb_grammar
from templates.areyourobot_grammar import get_areyourobot_grammar
from templates.distractor_grammar import get_negdistractor_grammar
from templates.gramgen import GramRecognizer, gram_to_lark_ebnf


class AreYouRobotClass(Enum):
    POSITIVE = "p"
    NEGATIVE = "n"
    AMBIGIOUS = "a"


class GrammarClassifyException(Exception):
    pass


@attr.s(auto_attribs=True, frozen=True)
class AreYouRobotResult:
    prediction: AreYouRobotClass
    exactly_in_class: bool
    """Used to say whether the utterance was exactly found in the grammar or
    it is assumed to be based off heuristics or because no other class fits"""
    error_message: Optional[str] = None
    """If something unexpected happens (like being in multiple classes) a 
    error message will be given"""


class AreYouRobotClassifier:
    def __init__(self, exception_if_conflict: bool = True):
        pos_gram = get_areyourobot_grammar()
        self.exception_if_conflict = exception_if_conflict
        #print(gram_to_lark_ebnf(pos_gram))
        self.pos_parser = GramRecognizer(pos_gram)
        self.pos_parser_limited = GramRecognizer(
            pos_gram,
            case_sensitive=False,
            check_last_sentence_by_itself=False,
            check_last_comma_by_itself=False,
            check_multiple_question_sentences=False,
        )
        self.amb_parser = GramRecognizer(
            get_amb_grammar(),
            case_sensitive=False,
            check_last_sentence_by_itself=False,
            check_last_comma_by_itself=False,
            check_multiple_question_sentences=False,
        )
        self.neg_parser = GramRecognizer(
            get_negdistractor_grammar(),
            case_sensitive=False,
            check_last_sentence_by_itself=False,
            check_last_comma_by_itself=False,
            check_multiple_question_sentences=False,
        )

    def classify(self, utterance: str) -> AreYouRobotResult:
        in_pos_limited = self.pos_parser_limited.is_in_grammar(utterance)
        in_neg = self.neg_parser.is_in_grammar(utterance)
        in_amb = self.amb_parser.is_in_grammar(utterance)
        if sum(map(int, [in_pos_limited, in_neg, in_amb])) > 1:
            # TODO: should have an option for a fast path that doesn't check every parser
            if in_pos_limited:
                pprint(self.pos_parser_limited._lark.parse(utterance.lower()))
            error_message = f"CONFLICT {utterance}: Pos_limited {in_pos_limited} neg {in_neg} in_amb {in_amb}"
            if self.exception_if_conflict:
                raise GrammarClassifyException(error_message)
            else:
                return AreYouRobotResult(
                    prediction=AreYouRobotClass.AMBIGIOUS,
                    exactly_in_class=False,
                    error_message=error_message,
                )
        if in_pos_limited:
            return AreYouRobotResult(
                prediction=AreYouRobotClass.POSITIVE,
                exactly_in_class=True,
            )
        if in_neg:
            return AreYouRobotResult(
                prediction=AreYouRobotClass.NEGATIVE,
                exactly_in_class=True,
            )
        if in_amb:
            return AreYouRobotResult(
                prediction=AreYouRobotClass.AMBIGIOUS,
                exactly_in_class=True,
            )
        in_pos_heuristics = self.pos_parser.is_in_grammar(utterance)
        if in_pos_heuristics:
            return AreYouRobotResult(
                prediction=AreYouRobotClass.POSITIVE,
                exactly_in_class=False,
            )
        return AreYouRobotResult(
            prediction=AreYouRobotClass.NEGATIVE,
            exactly_in_class=False,
        )




