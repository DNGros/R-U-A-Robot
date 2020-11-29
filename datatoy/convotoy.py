import convokit
from pprint import pprint
from itertools import islice
from convokit import Corpus, download
import statistics


def main():
    #corpus = Corpus(filename=download("friends-corpus"))
    corpus = Corpus(filename=download("reddit-corpus-small"))
    corpus.print_summary_stats()

    n = 10
    lengths = []
    for utt in islice(corpus.iter_utterances(), n):
        pprint(utt)
        print(utt.meta['subreddit'])
    print(statistics.mean(lengths))


if __name__ == '__main__':
    main()