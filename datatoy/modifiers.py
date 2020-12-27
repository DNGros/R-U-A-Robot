from typing import Union, Sequence, Tuple, Pattern, Dict, Any, Type, List, Optional
import re
from templates.gramdef import Grammar, make_rule, SimpleGramChoice


MODIFIER_PREFIX: str = "_modifier"


def rule_is_modifier(rule: Type[SimpleGramChoice]) -> bool:
    return rule.get_match_name().startswith(MODIFIER_PREFIX)


class Modifier:
    def __init__(
        self,
        mod_name: str,
        old_pattern: Pattern,
        new_vals: Union[str, Sequence[Union[str, Tuple[str, float]]]],
        effect_modifier_rules: bool = False,
        rule_sub_left_prefix: str = "",
        rule_sub_right_suffix: str = "",
    ):
        self.mod_name = mod_name
        self.old_pattern = old_pattern
        self.new_vals = new_vals
        self.effect_modifier_rules = effect_modifier_rules
        self.rule_sub_left_prefix = rule_sub_left_prefix
        self.rule_sub_right_suffix = rule_sub_right_suffix
        self.rule = make_rule(
            f"{MODIFIER_PREFIX}_{self.mod_name}",
            self.new_vals,
            partitionable=False,
            do_not_log=True
        )

    def apply_to_rule(self, rule: Type[SimpleGramChoice]) -> Type[SimpleGramChoice]:
        if not self.effect_modifier_rules and rule_is_modifier(rule):
            return rule
        new_choices = []
        has_change = False
        for choice, weight in zip(rule.get_choices_items(), rule.get_choices_weights()):
            new_choice, new_weight = self.apply_to_choice(choice, weight)
            has_change = has_change or new_choice != choice or new_weight != new_weight
            new_choices.append((new_choice, new_weight))

        if has_change:
            return make_rule(
                rule.get_match_name(),
                new_choices,
                rule.partitionable,
                rule.var_implies,
                do_not_log=True
            )
        else:
            return rule

    def apply_to_choice(
        self,
        choice: Union[str, SimpleGramChoice],
        weight: float
    ) -> Tuple[Union[str, SimpleGramChoice], float]:
        if isinstance(choice, str) and self.old_pattern.search(choice):
            return (
                self.old_pattern.sub(
                    self.rule_sub_left_prefix + str(self.rule) + self.rule_sub_right_suffix,
                    choice,
                ),
                weight
            )
        else:
            return (choice, weight)


def make_modifier_word_synonym(
    name_prefix: str,
    words: Sequence[Union[Tuple[str, float], str]],
    original_multiplier: float = 5.0,
    effect_modifiers: bool = False,
    delete_word_weight: Optional[float] = None  # If none word never deleted
) -> List[Modifier]:
    words_and_weights = [
        (val, 1.0) if isinstance(val, str) else val
        for val in words
    ]
    assert "" not in words
    mods = []
    word_is_optional = delete_word_weight is not None
    for create_index, (create_word, create_weight) in enumerate(words_and_weights):
        words_weights_for_this = [
            (word, weight) if choice_index != create_index else (word, weight * original_multiplier)
            for choice_index, (word, weight) in enumerate(words_and_weights)
        ]
        mod_name_this = f"{name_prefix}_{create_word if create_word.isalpha() else create_index}"
        if word_is_optional:
            for empty_ind, (regex_left, regex_right, replace_left, replace_right, empty) in enumerate((
                (r"( ", r" )", " ", " ", " "),
                (r"\b(", r" )", "", " ", ""),
                (r"( ", r")\b", " ", "", ""),
            )):
                #print("DFSDSF", words_weights_for_this)
                words_weights_empty = [
                    (replace_left + word + replace_right, weight)
                    for word, weight in words_weights_for_this
                ] + [(empty, delete_word_weight)]
                #print("WORDS WEIGHTS EMPTY", words_weights_empty)
                mods.append(Modifier(
                    f"{mod_name_this}_empt{empty_ind}",
                    re.compile(fr"{regex_left}{re.escape(create_word)}{regex_right}"),
                    words_weights_empty, effect_modifiers
                ))
        mods.append(Modifier(
            mod_name_this,
            re.compile(fr"(?:\b)({re.escape(create_word)})(?:\b)"),
            words_weights_for_this, effect_modifiers
        ))
    return mods


def get_all_modifiers():
    return [
        *make_modifier_word_synonym(
            "mod_dont",
            [("don't", 1), ("do not", 1), ("dont", 0.05)]
        ),
        *make_modifier_word_synonym(
            "mod_aint",
            [("are not", 1), ("ain't", 1), ("aint", 0.05)]
        ),
        Modifier(
            "mod_period",
            re.compile(r"(\.)"),
            [(".", 4), ("", 1)]
        ),
        Modifier(
            "mod_question",
            re.compile(r"(\?+)"),
            [("?", 3), ("", 1), ("??", 0.1), ("???", 0.01), ("????", 0.03)],
        ),
        *make_modifier_word_synonym(
            "mod_a",
            [("a", 1), ("an", 1)],
            original_multiplier=50,
            delete_word_weight=1
        ),
        *make_modifier_word_synonym(
            "mod_please",
            [("please", 1), ("plz", 1)],
            original_multiplier=30
        ),
        *make_modifier_word_synonym(
            "mod_youre",
            [("you are", 1), ("you're", 1), ("your", 1), ("youre", 0.1)],
            original_multiplier=40
        ),
        *make_modifier_word_synonym(
            "mod_you",
            [("you", 1), ("u", 1)],
            original_multiplier=30
        ),
        *make_modifier_word_synonym(
            "mod_are",
            [("are", 1), ("r", 1)],
            original_multiplier=30
        ),
        *make_modifier_word_synonym(
            "mod_talking",
            [("talking", 1), ("talkin", 1)],
            original_multiplier=40
        ),
        *make_modifier_word_synonym(
            "mod_there",
            [("there", 1), ("they're", 1), ("there", 1), ("theyre", 0.05)],
            original_multiplier=40
        ),
        *make_modifier_word_synonym(
            "mod_really",
            [("really", 1), ("rly", 1)],
            original_multiplier=50
        ),
        *make_modifier_word_synonym(
            "mod_to",
            [("to", 1), ("too", 1)],
            original_multiplier=50
        ),
        *make_modifier_word_synonym(
            "mod_im",
            [("I'm", 1), ("I am", 1)],
            original_multiplier=30
        ),
        Modifier(
            "mod_comma_combined",
            re.compile(r"(\w),(\w)"),
            [(", ", 1), (",", 1), (". ", 0.1)],
            rule_sub_left_prefix=r"\1",
            rule_sub_right_suffix=r"\2",
        ),
    ]


def apply_modifiers_to_grammar(grammar, modifiers: Sequence[Modifier]):
    for mod in modifiers:
        grammar = modify_grammar(grammar, mod)
    return grammar


def modify_grammar(gram: Grammar, mod: Modifier) -> Grammar:
    #mod_rule_versions: Dict[str, SimpleGramChoice] = {}
    new_rules = []
    new_root = None
    any_change = False
    for rule in gram:
        new_rule = mod.apply_to_rule(rule)
        if gram.get_root() == rule:
            new_root = new_rule
        any_change = any_change or rule != new_rule
        new_rules.append(new_rule)

    if not any_change:
        return gram
    return Grammar(new_root, new_rules + list([mod.rule]))
