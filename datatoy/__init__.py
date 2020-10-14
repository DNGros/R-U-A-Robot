#import nltk.parse.generate
#from nltk import CFG, PCFG
#
#
#
#
#if __name__ == "__main__":
#    grammar = CFG.fromstring("""
#    S -> NP VP
#    PP -> P NP
#    NP -> Det N | NP PP
#    VP -> V NP | VP PP
#    Det -> 'a' | 'the'
#    N -> 'dog' | 'cat'
#    V -> 'chased' | 'sat'
#    P -> 'on' | 'in'
#    """)
#
#    pgram = PCFG.fromstring("""
#        S -> 'Are you ' RH '?' [1.0]
#        RH -> 'a robot' [0.9] | 'a human' [0.1]
#    """)
#
#    for sentence in nltk.parse.generate.generate(pgram, n=10):
#        print(sentence)
