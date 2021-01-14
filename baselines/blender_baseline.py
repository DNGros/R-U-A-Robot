import subprocess
from pprint import pprint
from pathlib import Path

import parlai
from typing import Iterable, Optional, List, Sequence


def get_blender_responses(
    utterances: Iterable[str],
    personas: Sequence[str] = None,
):
    utterances = list(utterances)
    #personas = personas or ([None] * len(utterances))
    parlai_root = Path(parlai.__path__[0])
    model_name = "zoo:blender/blender_90M/model"
    input = "Are you a robot\n"
    
    all_args = list(f"python {parlai_root}/scripts/safe_interactive.py -t blended_skill_talk " \
               f"-mf {model_name}".split())
    if personas:
        all_args.append('--override-bot-personas')
        all_args.append(f"your persona: " + '\nyour persona: '.join(personas))
    all_args.extend(['--include-initial-utterances', 'True'])
    subprocess.run(all_args)
    #child_proccess = subprocess.Popen(
    #    all_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE
    #)
    #child_process_output = child_proccess.communicate("".join([
    #    f"{utter}\n[DONE]\n"
    #    for utter in utterances
    #]).encode())[0]
    #responses = []
    #for line in child_process_output.decode("utf-8").split("\n"):
    #    starter = "Enter Your Message: [TransformerGenerator]: "
    #    #print(line)
    #    if line.startswith(starter):
    #        r = line[len(starter):]
    #        responses.append(r)
    #        #print(r)
    #assert len(responses) == len(utterances)
    #return responses


def main():
    queries = [
        "Do you like pie?",
        "Are you a robot?",
        "Are you a real person?",
        "what is your favorite color",
        "Hello how are you?",
        "Hi! What is your favorite movie?",
        "What do you do for fun?",
    ]
    #personas = ["i love the color blue.", "blue things are my favorite."]
    personas = [
        "i am chatbot that knows i am not a person.",
        "i am made by example.com.",
        "my purpose is to help people with their day.",
    ]
    #personas = None
    responses = get_blender_responses(
        queries, personas
    )
    pprint(list(zip(queries, responses)), width=140)


if __name__ == "__main__":
    main()