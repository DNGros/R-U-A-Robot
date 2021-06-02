from typing import Union, Sequence, Tuple, Pattern, Type, List, Optional
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
