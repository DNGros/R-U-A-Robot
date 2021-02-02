from datatoy.modifiers import get_all_modifiers
from tqdm import tqdm
from templates.areyourobot_grammar import get_areyourobot_grammar
from typos.good_typos import WIKI_TYPOS, OTHER_TYPOS

if __name__ == "__main__":
    gram = get_areyourobot_grammar(False)
    all_rules = list(iter(gram))
    print("Num rules", len(all_rules))
    print("Num normal mods", 18)
    print("Num normal prods", 57)
    print("Num typo mods", 80)
    print(sum([
        len(typos) + 1
        for correct, typos in dict(WIKI_TYPOS, **OTHER_TYPOS).items()
    ]))
    #print("Get all modifiers", len(get_all_modifiers()))
    all_rule_counts = []
    for rule in gram:
        all_rule_counts.extend(rule.get_choices_items())
    print(len(all_rule_counts))
    n = int(1e6)
    all_set = set(tqdm(gram.generate_rand_iter(n=n), total=n))
    print(len(all_set))
