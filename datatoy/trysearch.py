import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
import dataclasses
from typing import List, Tuple, Iterable
from pathlib import Path
from tqdm import tqdm
import random
import numpy as np
import scipy.special
from whoosh.qparser import QueryParser
from whoosh import qparser
from whoosh.index import create_in
import whoosh.index
from whoosh.fields import STORED, TEXT, ID, Schema

from datatoy.alldata import get_all_utterances_list, preproc, Utterance

cur_file = Path(__file__).parent.absolute()
indexdir = "indexdir"
REINDEX: bool = True


class QuickWhooshSearcher:
    def __init__(self, index):
        self._index = index

    def search(self, queries: List[str], max_results=20) -> List[List[Tuple[str, float]]]:
        out = []
        parser = QueryParser("proc_text", self._index.schema, group=qparser.OrGroup)
        with self._index.searcher() as searcher:
            for query in tqdm(queries):
                query = parser.parse(preproc(query))
                results = searcher.search(query, limit=max_results)
                v = []
                out.append(v)
                for result in results[:min(len(results), max_results)]:
                    v.append((Utterance(**dict(result)), result.score))
        return out


class ScikitSearcher:
    def __init__(self, text, y, max_results: int = 20):
        self.y = y
        self.count_vect = CountVectorizer()
        X_train_counts = self.count_vect.fit_transform(text)
        self.tfidf_transformer = TfidfTransformer(norm='l2')
        self.X_train_tfidf = self.tfidf_transformer.fit_transform(X_train_counts)
        self.neigh = NearestNeighbors(n_neighbors=max_results, n_jobs=-1, metric='cosine')
        self.neigh.fit(self.X_train_tfidf)

        pass

    def search(self, queries: List[str]) -> List[List[Tuple[Utterance, float]]]:
        X_test_counts = self.count_vect.transform(queries)
        X_test_tfidf = self.tfidf_transformer.transform(X_test_counts)
        all_dists, all_inds = self.neigh.kneighbors(X_test_tfidf, return_distance=True)
        out = []
        for dists, indexes in zip(all_dists, all_inds):
            scores = 1 - dists
            out.append([
                (self.y[index], score)
                for score, index in zip(scores, indexes)
                if score > 0
            ])
        return out


def make_searcher(examples: Iterable[Utterance]) -> QuickWhooshSearcher:
    schema = Schema(
        dataset=ID(stored=True),
        section=ID(stored=True),
        subsection=ID(stored=True),
        text=STORED(),
        proc_text=TEXT(stored=True)
    )
    #st = RamStorage()
    ix = create_in(indexdir, schema)
    #ix = st.create_index(schema)
    writer = ix.writer(limitmb=256, procs=8, multisegment=False)
    print("adding docs")
    for ex in examples:
        writer.add_document(**dataclasses.asdict(ex))
    print("commiting")
    writer.commit()
    return QuickWhooshSearcher(ix)


def make_searcher_skit(examples: Iterable[Utterance]) -> ScikitSearcher:
    samples = [ex.proc_text for ex in examples]
    return ScikitSearcher(samples, examples, 20)


def sample_search_result(results: List[Tuple[Utterance, float]]):
    strings, scores = zip(*results)
    #print("scores", scores)
    prob = scipy.special.softmax(np.array(scores).astype(np.float))
    #print("prob", prob)
    return random.choices(strings, weights=prob, k=1)[0]


def load_searcher() -> ScikitSearcher:
    #ix = whoosh.index.open_dir(indexdir)
    #return QuickWhooshSearcher(ix)
    #return make_searcher_skit()
    raise NotImplemented
    pass


def search_some_distractir_examples(n=10):
    print("Load searcher")
    if REINDEX:
        searcher = make_searcher_skit(examples=get_all_utterances_list())
    else:
        searcher = load_searcher()
    print("gen examples")
    queries = get_some_samples(n=n)
    print("search")
    results = searcher.search(queries)
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
    results = list(set(search_some_distractir_examples(n=10000)))
    random.shuffle(results)
    csv_dict = []
    for result in results:
        csv_dict.append({
            "found": "weighted",
            **dataclasses.asdict(result),
        })
    pd.DataFrame(csv_dict).to_csv(cur_file / "outputs/distract_2.csv")


def rand_sample():
    results = random.sample(get_all_utterances_list(), 1000)
    csv_dict = []
    for result in results:
        csv_dict.append({
            "found": "random",
            **dataclasses.asdict(result),
        })
    pd.DataFrame(csv_dict).to_csv(cur_file / "outputs/distract_rand_0.csv")


if __name__ == "__main__":
    main()
    #rand_sample()
