import re
import lark
from typing import *
from nltk.tokenize import sent_tokenize
from templates.gramdef import SimpleGramChoice, Grammar
from util.util import flatten_list


def escape_bnf_string(s: str) -> str:
    s = s.replace('"', r'\"')
    s = s.replace('\n', r'\n')
    return '"' + s + '"'


match_str_regex = re.compile(r"\[\[([^\d\W]\w*)\]\]")


def pull_out_sub_cmds(string: Union[str, Type[SimpleGramChoice]]) -> str:
    string = str(string)
    if string == "":
        return '""'
    return " ".join(
        escape_bnf_string(choice_text) if i % 2 == 0 else choice_text.lower()
        for i, choice_text in enumerate(match_str_regex.split(string))
        if choice_text
    )


def rule_to_lark_ebnf(
    rule: Type[SimpleGramChoice]
) -> List[str]:  # might require multiple rules to express
    choice_strs = [pull_out_sub_cmds(c) for c in rule.get_choices_items()]
    empty_str = '""'
    if empty_str in choice_strs:
        # Lark get's unhappy about a "zero width regex". So add a helper rule using the "?" modifier
        #   https://github.com/lark-parser/lark/issues/80
        inner_name = f"inner_{rule.get_match_name().lower()}"
        return [
            f"{inner_name}: {' | '.join(c for c in choice_strs if c != empty_str)}",
            f"{rule.get_match_name().lower()}: {inner_name}?"
        ]
    else:
        return [f"{rule.get_match_name().lower()}: {' | '.join(choice_strs)}"]


def gram_to_lark_ebnf(gram: Grammar, case_sensitive: bool = True):
    def maybe_lower(s):
        return s if case_sensitive else s.lower()
    return "\n".join(
        maybe_lower(text) for text in flatten_list([
            rule_to_lark_ebnf(rule)
            for rule in gram
        ])
    )


class GramRecognizer:
    def __init__(
        self,
        grammar: Grammar,
        case_sensitive: bool = False,
        check_last_sentence_by_itself: bool = True,
        check_last_comma_by_itself: bool = True,
        check_multiple_question_sentences: bool = True,
    ):
        gram_text = gram_to_lark_ebnf(grammar, case_sensitive)
        self._lark = lark.Lark(gram_text, start=grammar.get_root().get_match_name().lower())
        self._case_sensitive = case_sensitive
        self._check_last_sentence_by_itself = check_last_sentence_by_itself
        self._check_last_comma_by_itself = check_last_comma_by_itself
        self._check_multiple_question_sentences = check_multiple_question_sentences

    def _is_in_grammar(self, string: str) -> bool:
        try:
            self._lark.parse(string)
            return True
        except lark.LarkError:
            return False

    def is_in_grammar(self, string: str) -> bool:
        if not self._case_sensitive:
            string = string.lower()
        out = False
        if self._is_in_grammar(string) or (
            string.strip() != string
            and self._is_in_grammar(string.strip())
        ):
            return True
        if self._check_last_sentence_by_itself or self._check_multiple_question_sentences:
            all_sents = sent_tokenize(string)
            if self._check_last_sentence_by_itself and len(all_sents) >= 1:
                last_sentence = all_sents[-1].strip()
                out = out or self._is_in_grammar(last_sentence)
                last_period = string.split(".")[-1].strip()
                if last_period != last_sentence and last_period != string.strip():
                    out = out or self._is_in_grammar(last_period)
            if self._check_multiple_question_sentences and 2 <= len(all_sents) <= 5:
                out = out or any(
                    self._is_in_grammar(sent.strip())
                    for sent in all_sents[:-1]
                    if sent.endswith("?")
                )

        if not out and self._check_last_comma_by_itself and "," in string:
            last_comma = string.split(",")[-1]
            out = out or self._is_in_grammar(last_comma.strip())
        return out
