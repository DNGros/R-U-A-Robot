from dataclasses import dataclass
from typing import List, Iterable

from nltk import word_tokenize

from datatoy.explore_personas import load_persona_chat, get_all_persona_statements_from_examples, \
    get_all_turns_from_examples
import convokit
from itertools import islice
from convokit import Corpus, download


def preproc(s: str):
    return " ".join(word_tokenize(s.lower().strip()))


@dataclass(frozen=True)
class Utterance:
    dataset: str
    section: str
    subsection: str
    text: str
    proc_text: str


def _get_from_convo_corpus(
    corpus_name: str,
    get_section = lambda utt: "",
    allow_duplicates: bool = False
) -> Iterable[Utterance]:
    corpus = Corpus(filename=download(corpus_name))
    corpus.print_summary_stats()
    returned_text = set()
    for utt in corpus.iter_utterances():
        text = utt.text[max(-len(utt.text), -2000):]
        proc_text = preproc(text)
        if not allow_duplicates:
            if proc_text in returned_text:
                continue
            returned_text.add(proc_text)
        yield Utterance(corpus_name, get_section(utt), "", text, proc_text)


def get_all_reddit_small_utterances(duplicates: bool = False) -> Iterable[str]:
    yield from _get_from_convo_corpus(
        "reddit-corpus-small", lambda utt: utt.meta['subreddit'], allow_duplicates=duplicates)


def get_from_persuasion_for_good(duplicates: bool = False) -> Iterable[str]:
    yield from _get_from_convo_corpus("persuasionforgood-corpus", allow_duplicates=duplicates)


def get_all_utterances_list() -> List[Utterance]:
    out = []
    for kind in ("original", "revised"):
        examples = list(load_persona_chat(kind))
        out.extend([
            *(
                Utterance("PersonaChat", "persona", kind, ex, preproc(ex))
                for ex in get_all_persona_statements_from_examples(examples)
            ),
            *(
                Utterance("PersonaChat", "turn", kind, ex, preproc(ex))
                for ex in get_all_turns_from_examples(examples)
            ),
        ])
    out.extend(get_all_reddit_small_utterances())
    out.extend(get_from_persuasion_for_good())
    return out
