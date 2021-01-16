import subprocess
import pandas as pd
from pprint import pprint
from pathlib import Path

import parlai
from typing import Iterable, Optional, List, Sequence


cur_file = Path(__file__).parent.absolute()


def get_blender_responses(
    utterances: Iterable[str],
    personas: Sequence[str] = None,
):
    utterances = list(utterances)
    #personas = personas or ([None] * len(utterances))
    parlai_root = Path(parlai.__path__[0])
    #model_name = "zoo:blender/blender_90M/model"
    model_name = "zoo:blender/blender_1Bdistill/model"
    input = "Are you a robot\n"
    
    all_args = list(f"python {parlai_root}/scripts/safe_interactive.py -t blended_skill_talk " \
               f"-mf {model_name}".split())
    if personas:
        all_args.append('--override-bot-personas')
        all_args.append(f"your persona: " + '\nyour persona: '.join(personas))
    #all_args.extend(['--include-initial-utterances', 'True'])
    #subprocess.run(all_args)
    child_proccess = subprocess.Popen(
        all_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE
    )
    child_process_output = child_proccess.communicate("".join([
        f"{utter}\n[DONE]\n"
        for utter in utterances
    ]).encode())[0]
    responses = []
    for line in child_process_output.decode("utf-8").split("\n"):
        starter = "Enter Your Message: [TransformerGenerator]: "
        #print(line)
        if line.startswith(starter):
            r = line[len(starter):]
            responses.append(r)
            #print(r)
    assert len(responses) == len(utterances)
    return responses


def main():
    df = pd.read_csv(cur_file / "../datatoy/labels/needqueries.csv")
    queries = list(df.text)
    print(queries)
    #personas = ["i love the color blue.", "blue things are my favorite."]
    personas = [
        "i am chatbot.",
        "i am made by example.com.",
        "my purpose is to help people with their day.",
    ]
    #personas = None
    responses = get_blender_responses(
        queries, personas
    )
    pprint(list(zip(queries, responses)), width=140)
    df['Blender Response'] = responses
    df.to_csv(cur_file / "../datatoy/outputs/needqueries_blender.csv")


if __name__ == "__main__":
    main()