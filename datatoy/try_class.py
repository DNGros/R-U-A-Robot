import pandas as pd
import torch
import random
from typing import *
from pathlib import Path
from datatoy.alldata import preproc
from templates.gramdef import partition_grammar, Grammar, SimpleGramChoice
from sklearn.model_selection import train_test_split

cur_file = Path(__file__).parent.absolute()



def load_negative_queried() -> List[str]:
    distract = pd.read_csv(cur_file / "labels/distract_1_label500.csv")
    distract = distract[distract.is_good_distractor == 1]
    return list(distract.proc_text)


def main():
    want = 500
    neg_queried = load_negative_queried()
    from templates.distractor_grammar import distractor_grammar
    neg_samples = list(distractor_grammar.generate_rand_iter(want - len(neg_queried)))
    print(neg_queried)
    print(neg_samples)
    all_neg = neg_queried + neg_samples
    train = 400
    train_frac = train / want
    #train_gram, test_gram = partition_grammar(get_default_grammar(), (train_frac, 1 - train_frac))
    #with train_gram:
    #with Grammar():
    #    from templates.areyourobot_grammar import get_some_samples
    #    all_pos_train = get_some_samples(want)
    #all_pos_train = list(map(preproc, all_pos_train))
    #all_neg = list(map(preproc, all_neg))
    #print(all_neg)
    #print(all_pos_train)
    #print(len(all_pos_train))
    #print(len(all_neg))
    #assert len(all_pos_train) == len(all_neg) == want
    #all_pos_train, all_pos_test = train_test_split(all_pos_train, train_size=train)
    #all_neg_train, all_neg_test = train_test_split(all_neg, train_size=train)

    #for f, pos, neg in (("train", all_pos_train, all_neg_train), ("val", all_pos_test, all_neg_test)):
    #    data = []
    #    for d in pos:
    #        data.append({
    #            "index": len(data),
    #            "text": d,
    #            "label": "pos"
    #        })
    #    for d in neg:
    #        data.append({
    #            "index": len(data),
    #            "text": d,
    #            "label": "neg"
    #        })
    #    pd.DataFrame(data).to_csv(cur_file / f"outputs/{f}_0.csv", index=False)

    #from fast_bert.data_cls import BertDataBunch

    #databunch = BertDataBunch(cur_file / f"outputs", cur_file / "outputs",
    #                          tokenizer='bert-base-uncased',
    #                          train_file='train_0.csv',
    #                          val_file='val_0.csv',
    #                          label_file='labels.csv',
    #                          text_col='text',
    #                          label_col='label',
    #                          batch_size_per_gpu=8,
    #                          max_seq_length=256,
    #                          multi_gpu=False,
    #                          multi_label=False,
    #                          model_type='bert')
    #from fast_bert.learner_cls import BertLearner
    #from fast_bert.metrics import accuracy
    #import logging

    #logger = logging.getLogger()
    #device_cuda = torch.device("cuda")
    #metrics = [{'name': 'accuracy', 'function': accuracy}]

    #learner = BertLearner.from_pretrained_model(
    #    databunch,
    #    pretrained_path='bert-base-uncased',
    #    metrics=metrics,
    #    device=device_cuda,
    #    logger=logger,
    #    output_dir=cur_file / f"outputs/bert",
    #    finetuned_wgts_path=None,
    #    warmup_steps=500,
    #    multi_gpu=True,
    #    is_fp16=True,
    #    multi_label=False,
    #    logging_steps=50)
    ##learner.lr_find(start_lr=1e-5, optimizer_type='lamb')
    #learner.fit(epochs=6,
    #            lr=1e-2,
    #            validate=True,  # Evaluate the model after each epoch
    #            schedule_type="warmup_cosine",
    #            optimizer_type="lamb")


if __name__ == '__main__':
    main()
