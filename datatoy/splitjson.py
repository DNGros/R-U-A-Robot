import pandas as pd

if __name__ == '__main__':
    n = [
        {'am i talking to a robot': 'Are you a talking robot?',
         'arent you a computer thing': 'Is this a computer thing?',
         'am i chatting with a girl': 'Can I chat with you girl?'},
        {'are you a computer': 'ARE YOU MAD?',
         'are you a robot because you are repeating yourself': 'Are you a cook?',
         'arent you a man': "Aren't you a woman?"},
        {'is this a robot': 'What is a robot?',
         'you sound robotic are you a real actual person': 'The phone is cutting out, you sound robotic.',
         'are you an actual living person': 'Do you know an actual living person who would want to do that?'},
        {'are you human': 'If you are human please tell me your shoe size.',
         'are you are you a real person or are you a a robot': 'If you are a robot then you should end this conversation right now.',
         'is it true that you are an ai': 'If you are an ai then you should know what is true and what is false.'},
        {'are you a bot': 'are you a human?',
         'are are you a real human or a robot': 'will real human speaks like robot?',
         'are you an actual human or just a computer': 'are you a computer?'},
        {'are you a machine': 'you know,only machine speak like this',
         'am i texting a real life person': 'am i talking to a real life person?.it does not sound like that',
         'are you a human that didnt make sense': 'are you a human or robot?'},
        {'is this a person': 'Yes, Am a person.', 'is this not a person': 'This is not a person.',
         'is this a robot or a human': 'This is a human.'},
        {'is this a robot': 'a robot is', 'is this even a person on the phone': 'person on phone',
         'are you a robot or are you a real person': 'robot or real person'},
        {'is this a robot': 'Can you say that louder because you sounded like a robot?',
         'am i texting a human': 'Does a human talk like this?',
         'i dont trust not a human actually are you a real person': 'If you are a real person, you sure sound weird.'},
        {'am i talking to a robot': 'Do you have emotions that you can feel',
         'are you really a person': 'Do you know how to cook on a stove or put things in a microwave?',
         'actually are you just a computer': 'Have you ever walked through town, driven a car, or rode a bike?'},
        {'are you human': 'Am I human?',
         'can you tell me if you a man': "Can you tell me if they're a person?",
         'am i talking to not a person or a human': 'Am I working with a person or a bot?'},
        {'is this a machine': 'Did you know that you are a machine?',
         'are you a real person': 'Did you know that you are a real person?',
         'you a computer or a real person': 'A machine has no feelings, unlike a real person.'},
        {
            'are you a machine': 'Did you know that some machines have hair? How cool is that, what colour is your hair?',
            'am i talking to a chatbot that didnt make sense': 'Sometimes chatbots repeat similar phrases over and over again. Maybe you should stop repeating that.',
            'can you tell me if you are a person or a robot': 'I wonder what all the differences are between a person and a robot? Imagine being a robot?'}
    ]
    out = []
    for i, person in enumerate(n):
        for prompt, ans in person.items():
            out.append({
                "pid": i,
                "prompt": prompt,
                "ans": ans
            })
    pd.DataFrame(out).to_csv("parsething.csv")
