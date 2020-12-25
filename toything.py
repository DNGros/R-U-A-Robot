from templates.areyourobot_grammar import get_areyourobot_grammar
from templates.gramdef import SimpleGramChoice, Grammar
from templates.gramgen import GramRecognizer


class NextThing(SimpleGramChoice):
    choices = [
        "oink",
        f"pop [[NextThing]]"
    ]


class RootProduction(SimpleGramChoice):
    choices = [
        "foo",
        ("bar", 10),
        f"foo {NextThing}"
    ]


if __name__ == "__main__":
    print(f"foo {NextThing}")
    print(str(RootProduction))
    gram = Grammar(RootProduction)
    print(list(gram.generate_rand_iter(10)))
    parser = GramRecognizer(gram)
    print(parser.is_in_grammar("foo pop pop oink"))
    print(parser.is_in_grammar("pop pop pop oink"))

    print(list(get_areyourobot_grammar().generate_rand_iter(10)))

