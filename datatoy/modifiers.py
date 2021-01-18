from typing import Union, Sequence, Tuple, Pattern, Dict, Any, Type, List, Optional
import re
from templates.gramdef import Grammar, make_rule, SimpleGramChoice
from typos.good_typos import WIKI_TYPOS, OTHER_TYPOS
from util.util import flatten_list

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
        require_explicit_allow: bool = False,
        ignore_name: str = None
    ):
        self.mod_name = mod_name
        self.old_pattern = old_pattern
        self.new_vals = new_vals
        self.effect_modifier_rules = effect_modifier_rules
        self.rule_sub_left_prefix = rule_sub_left_prefix
        self.rule_sub_right_suffix = rule_sub_right_suffix
        self.require_explicit_allow = require_explicit_allow
        self.ignore_name = ignore_name or mod_name
        self.rule = make_rule(
            f"{MODIFIER_PREFIX}_{self.mod_name}",
            self.new_vals,
            partitionable=False,
            do_not_log=True
        )

    def apply_to_rule(self, rule: Type[SimpleGramChoice]) -> Type[SimpleGramChoice]:
        if not self.effect_modifier_rules and rule_is_modifier(rule):
            return rule
        if self.ignore_name in rule.ignore_modifiers or self in rule.ignore_modifiers:
            return rule
        if self.require_explicit_allow and (
                self.ignore_name not in rule.allow_modifiers
                and self not in rule.allow_modifiers
        ):
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
                do_not_log=True,
                allow_modifiers=rule.allow_modifiers,
                ignore_modifiers=rule.ignore_modifiers,
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
                    words_weights_empty,
                    effect_modifiers,
                    ignore_name=name_prefix,
                ))
        mods.append(Modifier(
            mod_name_this,
            re.compile(fr"(?:\b)({re.escape(create_word)})(?:\b)"),
            words_weights_for_this, effect_modifiers,
            ignore_name=name_prefix
        ))
    return mods


def get_all_modifiers():
    base_modifiers = [
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
            re.compile(r"(\.)$"),
            [(".", 4), ("", 1), ("!", 0.05), ("..", 4/1500)]
        ),
        Modifier(
            "mod_question",
            re.compile(r"(\?+)"),
            [("?", 5), ("", 1), ("??", 0.02), ("???", 0.05), ("????", 0.01), ("!?", 0.05)],
        ),
        *make_modifier_word_synonym(
            "mod_a",
            [("a", 1), ("an", 1), ("a a", 100/1000)],
            original_multiplier=100,
            delete_word_weight=1
        ),
        # Sometimes we ignore the dropped version, but we still want to keep
        #   the version that swaps a/an
        *make_modifier_word_synonym(
            "mod_a_no_drop",
            [("a", 1), ("an", 1), ("a a", 100/1000)],
            original_multiplier=100,
            delete_word_weight=None,
        ),
        *make_modifier_word_synonym(
            "mod_please",
            [("please", 1), ("plz", 1), ("pls", 0.5)],
            original_multiplier=30
        ),
        *make_modifier_word_synonym(
            "mod_youre",
            [("you are", 1), ("you're", 1), ("your", 1), ("youre", 0.1), ("ur", 0.01)],
            original_multiplier=50
        ),
        *make_modifier_word_synonym(
            "mod_you",
            [("you", 1), ("u", 1)],
            original_multiplier=100
        ),
        *make_modifier_word_synonym(
            "mod_are",
            [("are", 1), ("r", 1)],
            original_multiplier=100
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
            [("really", 1), ("rly", 1), ("reeeally", 0.25)],
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
            "mod_comma_space",
            re.compile(r", "),
            [(", ", 10), (",", 1), (". ", 0.1), (" ", 0.03)],
            #rule_sub_left_prefix=r"\1",
            #rule_sub_right_suffix=r"\2",
        ),
        Modifier(
            "mod_comma_nospace",
            re.compile(r","),
            [(", ", 1), (",", 10), (". ", 0.1), (" ", 0.03)],
            #rule_sub_left_prefix=r"\1",
            #rule_sub_right_suffix=r"\2",
        ),
        Modifier(
            "mod_add_period",
            re.compile(r"([a-z])$", re.MULTILINE),
            [("", 15), (".", 1)],
            rule_sub_left_prefix=r"\1",
            require_explicit_allow=True,
            #rule_sub_right_suffix=r"\2",
        ),
        #Modifier(
        #    "mod_unquote",
        #    re.compile(r"(\w),(\w)"),
        #    [("", 1), (r'""', 1), (r"''", 0.1)],
        #    rule_sub_left_prefix=r"\1",
        #    rule_sub_right_suffix=r"\2",
        #),
    ]
    typo_modifiers = flatten_list(
        make_modifier_word_synonym(
            f"mod_typo_{correct}",
            [correct] + typos,
            original_multiplier=150
        )
        for correct, typos in dict(WIKI_TYPOS, **OTHER_TYPOS).items()
    )
    base_modifiers.extend(typo_modifiers)
    return base_modifiers


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
