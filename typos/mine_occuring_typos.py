"""Finds the typos that actually occur in our data so less heavy"""
from pathlib import Path
from templates.areyourobot_grammar import get_areyourobot_grammar
from collections import Counter, defaultdict
import nltk
from util.util import flatten_list
from pprint import pprint


cur_file = Path(__file__).parent.absolute()

if __name__ == "__main__":
    used_words = Counter(flatten_list(
        nltk.tokenize.word_tokenize(utt.lower())
        for utt in get_areyourobot_grammar(use_mods=False).generate_rand_iter(10000)
    ))
    wiki_text = (cur_file / "wikipedia/typos_from_wikipedia.txt").read_text()
    print(used_words)
    print(used_words["bout"])

    word_to_typos = defaultdict(list)
    for line in wiki_text.split("\n"):
        misspelling, corrections = line.lower().split("->")
        corrections = corrections.split(", ")
        if sum(used_words[v] for v in [misspelling] + corrections) >= 1:
            for correct in corrections:
                if used_words[correct] >= 1:
                    word_to_typos[correct].append(misspelling)
    pprint(dict(word_to_typos))

