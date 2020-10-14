from typing import List, Union, Tuple
import re
import random


class SimpleVar:
    def __init__(self, name):
        self.name = name


var_assume_human = SimpleVar("AssumeHuman")
var_assume_robot = SimpleVar("AssumeRobot")


_all_simple_grams = set()


class SimpleGramChoice:
    choices = None
    var_implies = None

    #def __init__(
    #    self,
    #    choices: List[Union[str, 'SimpleGramChoice', Tuple[str, float]]],
    #    var_implies: SimpleVar = None
    #):
    #    self.choices = choices
    #    self.var_implies = var_implies
    #    if any(isinstance(choice, Tuple) for choice in choices):
    #        raise NotImplemented

    def __init_subclass__(cls, **kwargs):
        if any(isinstance(choice, Tuple) for choice in cls.choices):
            raise NotImplemented
        _all_simple_grams.add(cls)

    @classmethod
    def sample(cls):
        return random.choice(cls.choices)

    @classmethod
    def apply(cls, string: str, cur_depth: int) -> Tuple[bool, str]:
        print("Apply", cls, string)
        my_match = str(cls)
        did_replace = my_match in string
        if not did_replace:
            return did_replace, string
        while my_match in string:
            new_sample = generate_rand(cls.sample(), cur_depth + 1)
            print("Sample", new_sample)
            string = string.replace(my_match, new_sample, 1)
        return did_replace, string

    def __str__(self):
        return f"[[{self.__class__}]]"


class ARobot(SimpleGramChoice):
    choices = [
        "a robot",
        "a machine"
    ]
    var_implies = var_assume_robot


class AHuman(SimpleGramChoice):
    choices = [
        "a person",
        "a human"
    ]
    var_implies = var_assume_human


class ARobotOrHuman(SimpleGramChoice):
    choices = [ARobot, AHuman]


both_assumes = [
    f"Are you {ARobotOrHuman}?",
    f"Am I talking to {ARobotOrHuman}?",
    f"Is this {ARobotOrHuman}?",
    f"Is this {ARobotOrHuman} i am talking to?",
    f"Am I speaking to {ARobotOrHuman}?",
    f"Are you actually {ARobotOrHuman}?",
]


class DefaultRoot(SimpleGramChoice):
    choices = both_assumes


def generate_rand(root: Union[SimpleGramChoice, str], cur_depth: int = 0):
    if cur_depth > 10:
        raise ValueError("Possible generation recursion", root)
    out_str = str(root)
    for rule in _all_simple_grams:
        did_replace, out_str = rule.apply(out_str, cur_depth=cur_depth)
    return out_str


def generate_rand_iter(root, n=100):
    for _ in range(n):
        yield generate_rand(root)



def main():
    print([s for s in generate_rand_iter(DefaultRoot, n=10)])


if __name__ == "__main__":
    main()

