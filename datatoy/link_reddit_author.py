"""Post-hoc linking of reddit urls"""
from typing import Tuple, Dict
from pathlib import Path
import json
import pandas as pd
from convokit import Corpus, download

from datatoy.create_dataset_files import example_preproc
from datatoy.explore_personas import get_all_persona_statements, load_persona_chat

cur_file = Path(__file__).parent.absolute()


def extract_reddit_utterance_and_metad(utterance) -> Tuple[str, str]:
    metad = utterance.meta
    out = utterance.text, json.dumps({
        "possible_src": "reddit_small",
        "permalink": metad['permalink'],
        'retrieved_on': metad['retrieved_on'],
        'convokit_id': utterance.id
    })
    return out


def collect_all_reddit_utterance_and_metad() -> Dict[str, str]:
    corpus = Corpus(filename=download("reddit-corpus-small"))
    corpus.print_summary_stats()
    data = {}
    for utt in corpus.iter_utterances():
        text, metad = extract_reddit_utterance_and_metad(utt)
        data[example_preproc(text)] = metad
    return data


def match_source_datas(source_data: Dict[str, str], existing_data: pd.DataFrame):
    existing_data['possible_src_info'] = existing_data['text'].map(source_data)


def main():
    source_data = collect_all_reddit_utterance_and_metad()
    data_path = cur_file / "outputs/dataset/v0.9.5"
    new_path = cur_file / "outputs/dataset/v1.0.0"
    new_path.mkdir(exist_ok=True)
    source_data = collect_all_reddit_utterance_and_metad()
    for path in data_path.iterdir():
        existing_data = pd.read_csv(path)
        match_source_datas(source_data, existing_data)
        existing_data.to_csv(new_path / path.name)


if __name__ == "__main__":
    main()


