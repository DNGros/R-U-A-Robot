import statistics

from templates.gramdef import Grammar


def explore_gram_capcity(gram: Grammar):
    seen = set()
    num_per_step = 250
    for i in range(20):
        counts = []
        for v in gram.generate_rand_iter(n=num_per_step):
            v = v.strip().lower()
            counts.append(int(v in seen))
            seen.add(v)
        print(f"Range {i*num_per_step}-{(i+1)*num_per_step}: {statistics.mean(counts)}")
    pass