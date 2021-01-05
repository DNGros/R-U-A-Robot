from typing import Sequence, TypeVar


def flatten_list(t):
    return [item for sublist in t for item in sublist]


T = TypeVar("T")


def get_only_element(l: Sequence[T]) -> T:
    if len(l) != 1:
        raise ValueError()
    return l[0]