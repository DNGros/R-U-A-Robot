from typing import Union, Sequence, Tuple, Pattern, Dict, Any, Type
import re
from templates.gramdef import Grammar, make_rule, SimpleGramChoice


class Modifier:
    def __init__(
        self,
        mod_name: str,
        old_pattern: Pattern,
        new_vals: Union[str, Sequence[Union[str, Tuple[str, float]]]],
    ):
        self.mod_name = mod_name
        self.old_pattern = old_pattern
        self.new_vals = new_vals
        self.rule = make_rule(f"_modifier_{self.mod_name}", self.new_vals, do_not_log=True)

    def apply_to_rule(self, rule: Type[SimpleGramChoice]) -> Type[SimpleGramChoice]:
        # Search every choice, replacing occurances of the pattern if needed
        new_choices = []
        has_change = False
        for choice, weight in zip(rule.get_choices_items(), rule.get_choices_weights()):
            new_choice, new_weight = self.apply_to_choice(choice, weight)
            has_change = has_change or new_choice != choice or new_weight != new_weight
            new_choices.append((new_choice, new_weight))

        if has_change:
            return make_rule(
                f"{rule.get_match_name()}_mod{self.mod_name}",
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
            return (self.old_pattern.sub(str(self.rule), choice), weight)
        else:
            return (choice, weight)



mod_dont = Modifier(
    "mod_dont",
    re.compile(r"\b(don't|do not)\b"),
    [("don't", 8), ("do not", 1)]
)


def modify_grammar(gram: Grammar, mod: Modifier) -> Grammar:
    #mod_rule_versions: Dict[str, SimpleGramChoice] = {}
    new_rules = []
    new_root = None
    for rule in gram:
        new_rules.append(mod.apply_to_rule(rule))
        if gram.get_root() == rule:
            new_root = new_rules[-1]

    return Grammar(new_root, new_rules + list([mod.rule]))
