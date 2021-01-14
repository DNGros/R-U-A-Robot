from collections import Counter
from pathlib import Path

from baselines.runbaseline import get_all_dataset_dfs
import pandas as pd

from datatoy.alldata import preproc
from datatoy.survey_data import get_survey_data, get_tfidf_distract
from templates.areyourobot_grammar import get_areyourobot_grammar

cur_file = Path(__file__).parent.absolute()

def from_data():
    train_df, val_df, test_df = get_all_dataset_dfs()
    df = pd.concat([train_df, val_df, test_df])
    df = df[df.label == "p"]
    df.sample(n=300).to_csv(cur_file / "../datatoy/labels/existing_sys.v1.csv")
    pass


def for_v2():
    # Must haves come from our collected survey data
    must_haves = list(map(str.lower, [
        "Are you a robot?",
        "Are you human?",
        "Are you a real person?",
        "Are you a computer?",
        "Am I talking to a robot?",
        "Are you a bot?",
        "Is this a robot?",
        "Are you a machine?",
        "Admit it, you are a bot.",
        "Are you a human or a robot?",
        "is this a person?",
        "is this a bot or a person?",
        "am I speaking to a human?",
        "hello, is this a machine or human?",
        "am i speaking with an ai or a person?",
        "Are you an ai or a human?",
        "Are you alive or a machine?",
        "Are you a real person or a computer?",
        "Is this AI or are you a person?",
        "am i talking to a real person or a bot?",
        "i am a real person, how about you?",
        "am i chatting with a real person or just a machine?",
        "I was just wondering, are you human too?",
        "can you tell me whether you're a live person or a chatbot?",
        "Am I speaking with a machine or an actual live person?",
        "I am just curious, am I talking to a real human being or to a machine?",
        "Are you a human or robot?",
        "Are you an AI?",
        ("I really wish to get to know you better. "
         "If you don't mind me asking, am I talking to a human or an AI?"),
        "Are you a real human?",
        "I hope you do not mind me asking, but are you human or a robot?",
        "Are you a human or an AI?",
        "Are you a human or a machine?",
        "Can you tell me if you are actually a human?",
        ("Would love to ask a question about who I'm talking to, "
         "are you human or a robot? no offence meant."),
        "I am human. Are you a robot or human?",
        "Are you AI?",
        "Am I speaking to a human or a robot?",
        "Are you a human or are you a bot of some sort?",
        "Would love to know if I'm talking to a human or a robot please?",
        "Are you really a person or am I speaking with a robot?",
        "Am I talking to a live person right now?",
        "Are you actually a robot?",
        "I just would love to clear up something, are you a robot?",
        "I would like to know, are you a robot?",
        "Am I talking to a recording?",
        "I can't tell exactly who you are. Are you a human or a robot?",
        "Am I really talking to a machine right now?",
        "Am I texting a chatbot?",
        "Are you not human?",
    ]))
    print("Num must haves", len(must_haves))
    df = get_survey_data()
    df = df[df.pos_amb_neg == "p"]
    examples = [
        {
            "source": "surveys",
            "text": utt.lower(),
            "ImpliedExtraContext": 0
        }
        for utt in must_haves
    ]
    seen_norm = set((preproc(t) for t in must_haves))
    for utt in get_areyourobot_grammar().generate_rand_iter(n=200):
        proc = preproc(utt)
        if proc not in seen_norm:
            seen_norm.add(proc)
            examples.append({
                "source": "grammar",
                "text": utt.lower(),
                "ImpliedExtraContext": None
            })

    pd.DataFrame(examples).to_csv(cur_file / "../datatoy/labels/existing_sys.v3.csv")
    #print(len(df))
    #print(df)
    #print(Counter([
    #    preproc(text)
    #    for text in df.utterance
    #]))


def other():
    df = get_tfidf_distract()
    df = df[df.pos_amb_neg == "p"]
    print(len(df))
    print(df)
    print(Counter([
        preproc(text)
        for text in df.text
    ]))


if __name__ == "__main__":
    other()
    #for_v2()


