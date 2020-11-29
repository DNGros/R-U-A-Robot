from typing import List, Union, Tuple, Iterable, Sequence, Type, Optional
from pprint import pprint
import random
from util.sampling import DeterministicSplitter


class SimpleVar:
    def __init__(self, name):
        self.name = name


_global_name_cache = {}


class Grammar:
    def __init__(
        self,
        root: Type['SimpleGramChoice']
    ):
        self._rules = set()
        self._root = root
        #self._root.add_to_grammar(self)
        for name, rule in _global_name_cache.items():
            self.add_rule(rule)

    def add_rule(self, rule: Type['SimpleGramChoice']):
        self._rules.add(rule)

    #def set_root(self, root: Type['SimpleGramChoice']):
    #    self._root = root

    def get_root(self) -> Type['SimpleGramChoice']:
        return self._root

    def __iter__(self):
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




class _SimpleGramChoiceMeta(type):
    def __new__(cls, clsname, superclasses, attributedict):
        #cls.my_clsname = clsname
        match_name = attributedict['__qualname__']
        attributedict['_match_name'] = match_name
        new_val = type.__new__(cls, clsname, superclasses, attributedict)
        if match_name in _global_name_cache:
            raise ValueError(f"That class {match_name} already defined")
        print("ADDING", clsname)
        _global_name_cache[match_name] = new_val
        return new_val

    def __str__(self):
        return f"[[{self._match_name}]]"

    def __repr__(self):
        return str(self)


class SimpleGramChoice(metaclass=_SimpleGramChoiceMeta):
    choices = None
    var_implies = None
    partitionable = False

    def __init_subclass__(cls, **kwargs):
        cls._weights = []
        cls._choices_items = []
        assert cls.choices is not None
        for choice in cls.choices:
            if isinstance(choice, tuple):
                choice, weight = choice
            else:
                weight = 1
            cls._weights.append(weight)
            cls._choices_items.append(choice)

    #@classmethod
    #def add_to_grammar(cls, gram: Grammar):
    #    gram.add_rule(cls)
    #    #for choice in cls._choices_items:
    #    #    if isinstance(choice, SimpleGramChoice) and choice not in gram:
    #    #        choice.add_to_grammar(gram)

    @classmethod
    def sample(cls):
        #print(str(cls), cls._choices_items)
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

    def __str__(self):
        return f"[[{self.__class__}]]"

    def __repr__(self):
        return str(self)

    @classmethod
    def get_choices_items(cls):
        return tuple(cls._choices_items)

    @classmethod
    def get_choices_weights(cls):
        return tuple(cls._weights)


def make_rule(
    name,
    choices,
    var_implies: Optional[SimpleVar] = None,
    partitionable: bool = False,
    is_root: bool = False
) -> Type[SimpleGramChoice]:
    return type(
        name,
        (SimpleGramChoice,),
        {
            "choices": choices,
            "var_implies": var_implies,
            "partitionable": partitionable,
            "is_root": is_root,
        }
    )


def generate_rand(
    root: Union[Type[SimpleGramChoice], str],
    rule_set: Grammar,
    cur_depth: int = 0
):
    if cur_depth > 15:
        raise ValueError("Possible generation recursion", root)
    out_str = str(root)
    for rule in rule_set:
        did_replace, out_str = rule.apply(out_str, rule_set, cur_depth=cur_depth)
    return out_str


def partition_grammar(
    rules: Grammar,
    weights: Sequence[float],
    seed: int = 2
) -> Sequence[Grammar]:
    new_grammars = tuple(Grammar() for _ in weights)
    splitter = DeterministicSplitter(weights, seed=seed)
    for rule in tuple(rules):
        choices = tuple(zip(rule.get_choices_items(), rule.get_choices_weights()))
        if rule.partitionable:
            new_choices = tuple([] for _ in weights)
            for choice, weight in choices:
                index = splitter.get_split_from_example(str(choice))
                new_choices[index].append((choice, weight))
            assert len(new_grammars) == len(new_choices)
            pprint(new_choices)
        else:
            new_choices = tuple([choices] * len(weights))
        for i, choices_for_this_split in enumerate(new_choices):
            with new_grammars[i]:
                make_rule(
                    name=rule.__name__ + "-" + str(i),
                    choices=choices_for_this_split,
                    var_implies=rule.var_implies,
                    partitionable=rule.partitionable,
                    is_root=rule.is_root
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