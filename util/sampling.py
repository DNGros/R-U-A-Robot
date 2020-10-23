from typing import Sequence
import math
import hashlib
import random
import string


def id_generator(size=6, chars=string.ascii_uppercase + string.digits, seed=None):
    # ref https://stackoverflow.com/questions/2257441/
    if seed:
        rng = random.Random(seed)
        return ''.join(rng.choice(chars) for _ in range(size))
    else:
        return ''.join(random.choice(chars) for _ in range(size))


class DeterministicSplitter:
    """Used to perform a pseudorandom selection of a split for example as a
    function of the input
    """
    def __init__(
        self,
        split_weights: Sequence[float],
        seed: int = None
    ):
        weight_sum = sum(split_weights)
        self._splits_weights = [w / weight_sum for w in split_weights]
        if seed is None:
            self._seed_str = ""
        else:
            self._seed_str = id_generator(seed=seed)

    def get_split_from_example(
        self,
        x: str
    ) -> int:
        """
        Args:
            x: the value to partition
        :returns
            The partition index. It will between 0 to `(len(self.split_weights) - 1)`
        """
        DIGEST_BYTES = 8
        MAX_VAL = 2**(8*DIGEST_BYTES)
        hash = hashlib.blake2b(
            str.encode(x + "::" + self._seed_str),
            digest_size=DIGEST_BYTES
        )
        hash_int = int(hash.hexdigest(), 16)
        current_ceiling = 0
        for i, probability in enumerate(self._splits_weights):
            current_ceiling += probability * MAX_VAL
            if hash_int <= math.ceil(current_ceiling):
                return i
        raise RuntimeError(f"Unreachable code reached. Splits {self._splits_weights}")