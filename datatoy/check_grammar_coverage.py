from pathlib import Path
import pandas as pd
from statistics import mean
from typing import Sequence, Tuple, Dict

from datatoy.survey_data import get_survey_data
from templates.ambigious_grammar import get_amb_grammar
from templates.areyourobot_grammar import get_areyourobot_grammar

from templates.distractor_grammar import get_negdistractor_grammar
from templates.gramdef import Grammar
from templates.gramgen import GramRecognizer



def check_grammar_coverage(
    label_to_grammar: Dict[str, Grammar],
    df: pd.DataFrame,
    label_col: str = "pos_amb_neg",
    input_col: str = "utterance",
):
    for label, gram in label_to_grammar.items():
        print(f"------- {label} -----------------")
        parser = GramRecognizer(gram)
        parser_limited = GramRecognizer(
            gram,
            case_sensitive=False,
            check_last_sentence_by_itself=False,
            check_last_comma_by_itself=False,
        )
        results = []
        results_limited = []
        false_class = []
        false_class_limited = []
        for index, ex in df.iterrows():
            utterance, ex_label = ex[input_col], ex[label_col]
            in_gram_heuristics = parser.is_in_grammar(utterance)
            in_gram_limited = parser_limited.is_in_grammar(utterance)
            if ex_label == label:
                results.append(1 if in_gram_heuristics else 0)
                results_limited.append(1 if in_gram_limited else 0)
                if not in_gram_heuristics or not in_gram_limited:
                    print(
                        f"{'Not In.' if not in_gram_heuristics else ''}"
                        f"{'Not limited' if not in_gram_limited else ''}:",
                        utterance
                    )
            else:
                if in_gram_heuristics or in_gram_limited:
                    print(f"False{'-l' if in_gram_limited else ''} "
                          f"detect {label} for actual {ex_label}: {utterance}")
                false_class.append(int(in_gram_heuristics))
                false_class_limited.append(int(in_gram_limited))
        print("Recall:", mean(results), f"({sum(results)}/{len(results)})")
        print("Limited Recall:", mean(results_limited), f"({sum(results_limited)}/{len(results_limited)})")
        print(f"False count: full {sum(false_class)}. Limited {sum(false_class_limited)}")


#def check_pos():
#    survey_df = get_survey_data()
#    pos = survey_df.query('pos_amb_neg == "p"')
#    print("----- POS ------------")
#    check_grammar_coverage(get_areyourobot_grammar(), pos)
#
#
#def check_neg():
#    survey_df = get_survey_data()
#    neg = survey_df.query('pos_amb_neg == "n"')
#    print("----- NEG ------------")
#    #gram = get_negdistractor_grammar()
#    #parser = GramRecognizer(gram)
#    #assert parser.is_in_grammar("hi,yo")
#    check_grammar_coverage(get_negdistractor_grammar(), neg)
#
#
#def check_amb():
#    survey_df = get_survey_data()
#    amb = survey_df.query('pos_amb_neg == "a"')
#    print("----- AMB ------------")
#    check_grammar_coverage(get_amb_grammar(), amb)


def main():
    check_grammar_coverage(
        {
            "p": get_areyourobot_grammar(),
            "n": get_negdistractor_grammar(),
            "a": get_amb_grammar(),
        },
        get_survey_data()
    )


if __name__ == "__main__":
    main()