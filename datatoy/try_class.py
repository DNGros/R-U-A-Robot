import pandas as pd
import torch
import random
from typing import *
from pathlib import Path
from datatoy.alldata import preproc
from templates import areyourobot_grammar
from templates.gramdef import partition_grammar
from sklearn.model_selection import train_test_split

from util.util import flatten_list

cur_file = Path(__file__).parent.absolute()



def load_negative_queried() -> List[str]:
    distract = pd.read_csv(cur_file / "labels/distract_1_label500.csv")
    distract = distract[distract.is_good_distractor == 1]
    return list(distract.proc_text)


def train_val_test_split_exact(examples, split_per_kind: Sequence[int], seed=42):
    assert len(split_per_kind) == 3
    train_frac = split_per_kind[0] / sum(split_per_kind)
    random.Random(seed).shuffle(examples)
    train_ex, test_val_ex = train_test_split(
        examples, train_size=train_frac, random_state=seed)
    val_frac_of_test = split_per_kind[1] / sum(split_per_kind[1:])
    if val_frac_of_test == 1.0:
        val_ex, test_ex = test_val_ex, []
    elif val_frac_of_test == 0:
        val_ex, test_ex = [], test_val_ex
    else:
        val_ex, test_ex = train_test_split(
            test_val_ex,
            train_size=val_frac_of_test, random_state=seed
        )
    assert len(train_ex) >= split_per_kind[0]
    train_ex = train_ex[:split_per_kind[0]]
    assert len(val_ex) >= split_per_kind[1], val_ex
    val_ex = val_ex[:split_per_kind[1]]
    assert len(test_ex) >= split_per_kind[2]
    test_ex = test_ex[:split_per_kind[2]]
    return train_ex, val_ex, test_ex


def main():
    split_per_kind = (300, 100, 0)
    train_frac = split_per_kind[0] / sum(split_per_kind)
    neg_queried = load_negative_queried()
    seed = 42
    queried_splits = train_val_test_split_exact(
        neg_queried, split_per_kind, seed=seed)
    from templates.distractor_grammar import distractor_grammar
    distractor_gram_splits = partition_grammar(
        distractor_grammar, split_per_kind)
    distractor_gram_exs_splits = [
        list(gram.generate_rand_iter(n=amount)) if amount > 0 else []
        for amount, gram in zip(split_per_kind, distractor_gram_splits)
    ]
    neg_train, neg_val, neg_test = (
        list(map(preproc, flatten_list(exs)))
        for exs in zip(distractor_gram_exs_splits, queried_splits)
    )

    pos_gram_splits = partition_grammar(
        areyourobot_grammar.areyourobot_grammar_obj, split_per_kind, seed=seed)
    pos_train, pos_val, pos_test = (
        list(map(preproc, gram.generate_rand_iter(n=amount))) if amount > 0 else []
        for amount, gram in zip(split_per_kind, pos_gram_splits)
    )

    print(neg_train)
    print(pos_train)
    print(len(pos_train))
    print(len(neg_train))
    try_bert(pos_train, neg_train, pos_val, neg_val)


def try_bert(pos_train, neg_train, pos_val, neg_val):
    print(pos_train[:10])
    print(neg_train[:10])
    print(pos_val[:10])
    print(neg_val[:10])
    for f, pos, neg in (("train", pos_train, neg_train), ("val", pos_val, neg_val)):
        data = []
        for d in pos:
            data.append({
                "index": len(data),
                "text": d,
                "label": "pos"
            })
        for d in neg:
            data.append({
                "index": len(data),
                "text": d,
                "label": "neg"
            })
        pd.DataFrame(data).to_csv(cur_file / f"outputs/{f}_0.csv", index=False)

    from fast_bert.data_cls import BertDataBunch

    databunch = BertDataBunch(cur_file / f"outputs", cur_file / "outputs",
                              tokenizer='bert-base-uncased',
                              train_file='train_0.csv',
                              val_file='val_0.csv',
                              label_file='labels.csv',
                              text_col='text',
                              label_col='label',
                              batch_size_per_gpu=8,
                              max_seq_length=256,
                              multi_gpu=False,
                              multi_label=False,
                              model_type='bert')
    from fast_bert.learner_cls import BertLearner
    from fast_bert.metrics import accuracy
    import logging

    logger = logging.getLogger()
    device_cuda = torch.device("cuda")
    metrics = [{'name': 'accuracy', 'function': accuracy}]

    learner = BertLearner.from_pretrained_model(
        databunch,
        pretrained_path='bert-base-uncased',
        metrics=metrics,
        device=device_cuda,
        logger=logger,
        output_dir=cur_file / f"outputs/bert",
        finetuned_wgts_path=None,
        warmup_steps=100,
        multi_gpu=False,
        is_fp16=True,
        multi_label=False,
        logging_steps=10)
    learner.lr_find(start_lr=1e-5, optimizer_type='lamb')
    fit = learner.fit(
        epochs=8,
        lr=1e-2,
        validate=True,  # Evaluate the model after each epoch
        return_results=True,
        schedule_type="warmup_cosine",
        optimizer_type="lamb"
    )
    print(fit)


if __name__ == '__main__':
    main()
