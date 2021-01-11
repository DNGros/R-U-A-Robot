from convokit import Corpus, download

if __name__ == "__main__":
    corpus = Corpus(filename=download("reddit-corpus-small"))
    corpus.print_summary_stats()
    for utt in corpus.iter_utterances():
        print(utt)

