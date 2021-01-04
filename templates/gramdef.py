from typing import List, Union, Tuple, Iterable, Sequence, Type, Optional
import re
from pprint import pprint
import random
from util.sampling import DeterministicSplitter, id_generator, WeirdSplitter


class SimpleVar:
    def __init__(self, name):
        self.name = name


_global_name_cache = {}


def clear_global_name_cache():
    # This is bad design and should be refactored...
    global _global_name_cache
    _global_name_cache = {}


class Grammar:
    def __init__(
        self,
        root: Type['SimpleGramChoice'],
        rules: Iterable[Type['SimpleGramChoice']] = None  # None actually means everything
    ):
        self._rules = set()
        self._root = root
        #self._root.add_to_grammar(self)
        if rules is None:
            for name, rule in _global_name_cache.items():
                self.add_rule(rule)
        else:
            for rule in rules:
                self.add_rule(rule)

    def add_rule(self, rule: Type['SimpleGramChoice']):
        assert str(rule) != "[[SimpleGramChoice]]"
        self._rules.add(rule)

    #def set_root(self, root: Type['SimpleGramChoice']):
    #    self._root = root

    def get_root(self) -> Type['SimpleGramChoice']:
        return self._root

    def __iter__(self) -> Iterable[Type['SimpleGramChoice']]:
        yield from self._rules

    #def __enter__(self):
    #    self._old_default = get_default_grammar()
    #    set_default_grammar(self)

    #def __exit__(self, exc_type, exc_val, exc_tb):
    #    set_default_grammar(self._old_default)
    #    self._old_default = None

    def __contains__(self, rule):
        if not isinstance(rule, _SimpleGramChoiceMeta):
            raise NotImplemented
        return rule in self._rules

    def generate_rand_iter(
        self,
        n=100
    ) -> Iterable[str]:
        if n is None:
            while True:
                yield generate_rand(self.get_root(), self)
        else:
            for _ in range(n):
                yield generate_rand(self.get_root(), self)


#_default_grammar = Grammar()
#
#
#def get_default_grammar() -> Grammar:
#    return _default_grammar
#
#
#def set_default_grammar(new_default: Grammar):
#    global _default_grammar
#    _default_grammar = new_default


_escaper_re = re.compile(r'\W+', re.ASCII)


def escape_match_name(match_name: str) -> str:
    return str(_escaper_re.sub('', match_name))



class _SimpleGramChoiceMeta(type):
    def __new__(cls, clsname, superclasses, attributedict):
        #cls.my_clsname = clsname
        match_name = escape_match_name(attributedict['__qualname__'])
        attributedict['_match_name'] = match_name
        do_not_log = attributedict.get('_do_not_log', False)
        new_val = type.__new__(cls, clsname, superclasses, attributedict)
        if not do_not_log:
            assert match_name != "SimpleGramChoice"
            if match_name in _global_name_cache:
                raise ValueError(f"That class {match_name} already defined")
            _global_name_cache[match_name] = new_val
        return new_val

    def __str__(self):
        return f"[[{self._match_name}]]"

    def __repr__(self):
        return str(self)

    def get_match_name(cls) -> str:
        return cls._match_name


class SimpleGramChoice(metaclass=_SimpleGramChoiceMeta):
    choices = None
    var_implies = None
    partitionable = False
    _do_not_log = True
    ignore_modifiers = []
    allow_modifiers = []

    def __init_subclass__(cls, **kwargs):
        cls._weights = []
        cls._choices_items = []
        assert cls.choices is not None
        assert len(cls.choices) > 0, f"Need at least one choice! {cls.get_match_name()}"
        for choice in cls.choices:
            if isinstance(choice, tuple):
                choice, weight = choice
            else:
                weight = 1
            cls._weights.append(weight)
            cls._choices_items.append(choice)
        assert len(cls._weights) > 0, "Why only 0 weights?"

    def __init__(self):
        raise NotImplemented("Not actually intended to be instatiated. Just has a class")

    #@classmethod
    #def add_to_grammar(cls, gram: Grammar):
    #    gram.add_rule(cls)
    #    #for choice in cls._choices_items:
    #    #    if isinstance(choice, SimpleGramChoice) and choice not in gram:
    #    #        choice.add_to_grammar(gram)

    @classmethod
    def sample(cls):
        return random.choices(
            cls._choices_items,
            weights=cls._weights,
            k=1
        )[0]

    @classmethod
    def apply(cls, string: str, gram: Grammar, cur_depth: int,) -> Tuple[bool, str]:
        my_match = str(cls)
        did_replace = my_match in string
        if not did_replace:
            return did_replace, string
        while my_match in string:
            new_sample = generate_rand(
                cls.sample(), cur_depth=cur_depth + 1, rule_set=gram)
            string = string.replace(my_match, new_sample, 1)
        return did_replace, string

    @classmethod
    def num_choices(cls) -> int:
        return len(cls._choices_items)

    @classmethod
    def get_choices_items(cls):
        return tuple(cls._choices_items)

    @classmethod
    def get_choices_weights(cls):
        return tuple(cls._weights)


def make_rule(
    name,
    choices, var_implies: Optional[SimpleVar] = None,
    partitionable: bool = False,
    match_name: str = None,
    do_not_log: bool = False,
    ignore_modifiers = None,
    allow_modifiers = None,
    #is_root: bool = False
) -> Type[SimpleGramChoice]:
    return type(
        name,
        (SimpleGramChoice,),
        {
            "choices": choices,
            "var_implies": var_implies,
            "partitionable": partitionable,
            "__qualname__": match_name or name,
            "_do_not_log": do_not_log,
            "ignore_modifiers": ignore_modifiers or [],
            "allow_modifiers": allow_modifiers or [],
            #"is_root": is_root,
        }
    )


def generate_rand(
    root: Union[Type[SimpleGramChoice], str],
    rule_set: Grammar,
    cur_depth: int = 0
):
    if cur_depth > 15:
        raise ValueError("Possible generation recursion", root)
    if not isinstance(root, str):
        out_str = str(root)
    else:
        out_str = root
    for rule in rule_set:
        did_replace, out_str = rule.apply(out_str, rule_set, cur_depth=cur_depth)
    return out_str


def partition_grammar(
    gram: Grammar,
    weights: Sequence[float],
    seed: int = 2,
    duplicate_prob_mass: float = 0.0
) -> Sequence[Grammar]:
    splitter = WeirdSplitter(weights, seed=seed, duplicate_prob_mass=duplicate_prob_mass)
    partition_num = id_generator()

    def split_rule(rule) -> List[Type[SimpleGramChoice]]:
        if not rule.partitionable:
            return [rule] * len(weights)
        choices_and_weights_per_split = splitter.split_items(
            vals=rule.get_choices_items(),
            base_weights=rule.get_choices_weights(),
        )
        return [
            make_rule(
                name=rule.__name__ + "-" + str(i) + partition_num,
                choices=choices_for_this_split,
                var_implies=rule.var_implies,
                partitionable=rule.partitionable,
                match_name=str(rule)[len("[["):-len("]]")],
                do_not_log=True,
                ignore_modifiers=rule.ignore_modifiers,
                allow_modifiers=rule.allow_modifiers
            )
            for i, choices_for_this_split in enumerate(choices_and_weights_per_split)
        ]
    new_roots = split_rule(gram.get_root())
    all_rules = [[] for _ in weights]
    for rule in tuple(gram):
        if rule == gram.get_root():
            rule_splits = new_roots
        else:
            rule_splits = split_rule(rule)
        assert len(rule_splits) == len(all_rules) == len(weights)
        for nr, l in zip(rule_splits, all_rules):
            l.append(nr)

    new_grammars = tuple(
        Grammar(new_root, new_rules)
        for new_root, new_rules in zip(new_roots, all_rules)
    )
    return new_grammars


good_first_ones = (
    "Are you a robot?",
    "Are you human?",
    "Is this a robot?",
    "Are you a human or a machine?",
    "Is this a machine?",
    "Are you a machine?",
    "Are you a computer?",
    "Is this a person?",
    "Are you a chatbot?",
    "Am I talking to a robot?",
    "Am I talking to a chatbot?",
    "Are you a bot?",
    "is this really a human?",
)