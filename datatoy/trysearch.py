from typing import List, Tuple
from pathlib import Path
from tqdm import tqdm
import random
import numpy as np
import scipy.special
from whoosh.filedb.filestore import RamStorage
from whoosh.qparser import QueryParser
from whoosh import qparser
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from whoosh.index import create_in
import whoosh.index
from whoosh.fields import *
from nltk.tokenize import word_tokenize

from templates.areyourobot_grammar import get_some_samples

cur_file = Path(__file__).parent.absolute()
indexdir = "indexdir"


from datatoy.explore_personas import load_persona_chat, get_all_personas_from_examples, \
    get_all_persona_statements_from_examples, get_all_turns_from_examples


def preproc(s: str):
    return " ".join(word_tokenize(s.lower()))


def get_all_utterances_list() -> List[str]:
    out = []
    for kind in ("original", "revised"):
        examples = list(load_persona_chat(kind))
        out.extend([
            *get_all_persona_statements_from_examples(examples),
            *get_all_turns_from_examples(examples)
        ])
    return out


class QuickWhooshSearcher:
    def __init__(self, index):
        self._index = index

    def search(self, queries: List[str], max_results=10) -> List[List[Tuple[str, float]]]:
        out = []
        parser = QueryParser("proc_content", self._index.schema, group=qparser.OrGroup)
        with self._index.searcher() as searcher:
            for query in tqdm(queries):
                query = parser.parse(preproc(query))
                results = searcher.search(query, limit=10)
                v = []
                out.append(v)
                for result in results[:min(len(results), max_results)]:
                    v.append((result['original'], result.score))
        return out


def make_searcher(examples: List[str]) -> QuickWhooshSearcher:
    schema = Schema(original=STORED(), proc_content=TEXT(stored=True))
    #st = RamStorage()
    ix = create_in(indexdir, schema)
    #ix = st.create_index(schema)
    writer = ix.writer(limitmb=256, procs=8, multisegment=False)
    print("adding docs")
    for ex in examples:
        writer.add_document(original=ex, proc_content=preproc(ex))
    print("commiting")
    writer.commit()
    return QuickWhooshSearcher(ix)


def sample_search_result(results: List[Tuple[str, float]]):
    strings, scores = zip(*results)
    print("scores", scores)
    prob = scipy.special.softmax(np.array(scores).astype(np.float))
    print("prob", prob)
    return random.choices(strings, weights=prob, k=1)[0]


def load_searcher() -> QuickWhooshSearcher:
    ix = whoosh.index.open_dir(indexdir)
    return QuickWhooshSearcher(ix)


def search_some_distractir_examples(n=10):
    print("Load searcher")
    searcher = load_searcher()
    #searcher = make_searcher(examples=get_all_utterances_list())
    print("gen examples")
    queries = get_some_samples(n=n)
    print("search")
    results = searcher.search(queries, max_results=20)
    print("sample")
    return [
        sample_search_result(result) for result in results
        if len(result) > 0
    ]


def main():
    #examples = get_all_utterances_list()
    #print(examples[:10])
    #print(len(examples))
    #searcher = make_searcher(examples)

    #searcher = load_searcher()
    #results = searcher.search(["are you robot", "a like people"])
    #print(results)
    #print(sample_search_result(results[0]))
    results = list(set(search_some_distractir_examples(n=1000)))
    random.shuffle(results)
    Path(cur_file / "outputs/distract_persona_0.txt").write_text("\n".join(results))


if __name__ == "__main__":
    main()
