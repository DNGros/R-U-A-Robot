import re
import lark
from typing import *
from nltk.tokenize import sent_tokenize
from templates.gramdef import SimpleGramChoice, Grammar
from util.util import flatten_list


def escape_bnf_string(s: str) -> str:
    return '"' + s.replace('"', r'\"') + '"'


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
        check_last_sentence_by_itself: bool = True
    ):
        gram_text = gram_to_lark_ebnf(grammar, case_sensitive)
        self._lark = lark.Lark(gram_text, start=grammar.get_root().get_match_name().lower())
        self._case_sensitive = case_sensitive
        self._check_last_sentence_by_itself = check_last_sentence_by_itself

    def _is_in_grammar(self, string: str) -> bool:
        try:
            self._lark.parse(string)
            return True
        except lark.LarkError:
            return False

    def is_in_grammar(self, string: str) -> bool:
        if not self._case_sensitive:
            string = string.lower()
        if self._is_in_grammar(string) or self._is_in_grammar(string.strip()):
            return True
        if self._check_last_sentence_by_itself:
            last_sentence = sent_tokenize(string)[-1]
            return self._is_in_grammar(last_sentence.strip())
        return False
