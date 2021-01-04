from util.sampling import duplicate_upto_set_prob_mass, partition_list, WeirdSplitter


def test_duplicate_upto_set_prob_mass():
    result = duplicate_upto_set_prob_mass(
        2,
        [1,  2,  3,  4,  5],
        [.14, .3, .19, .21, .16],
        0.6
    )
    print(result)
    assert result == (
        [[(2, .3), (4, .21), (3, .19)]]*2,
        [(5, .16), (1, .14)]
    )


def test_duplicate_upto_set_prob_mass2():
    result = duplicate_upto_set_prob_mass(
        3,
        [1,  2,  3,  4,  5],
        [.14, .3, .19, .21, .16],
        0.7
    )
    print(result)
    assert result == (
        [[(2, .3), (4, .21), (3, .19)]]*3,
        [(5, .16), (1, .14)]
    )


def test_partion_list():
    result = partition_list(
        elements=list(range(10)),
        split_weights=[0.6, 0.4],
    )
    assert result == [
        [0, 1, 2, 3, 4, 5],
        [6, 7, 8, 9]
    ]


def test_partion_list2():
    result = partition_list(
        elements=list(range(10)),
        split_weights=[0.6, 0.37, 0.03],
    )
    assert result == [
        [0, 1, 2, 3, 4, 5],
        [6, 7, 8],
        [9]
    ]


def test_partion_list3():
    result = partition_list(
        elements=list(range(5)),
        split_weights=[0.5, 0.38, 0.12],
    )
    assert result == [
        [0, 1],
        [2, 3],
        [4]
    ]


def test_partion_list4():
    result = partition_list(
        elements=list(range(5)),
        split_weights=[0.3, 0.38, 0.32],
    )
    assert result == [
        [0],
        [1, 2],
        [3, 4]
    ]


def test_weird_splitter():
    splitter = WeirdSplitter([0.7, 0.1, 0.2], seed=42, duplicate_prob_mass=.35)
    result = splitter.split_items(
        vals=list(range(10)),
        base_weights=[0, .21, 0, 0, .05, .3, .1, .19, 0.15, 0]
    )
    print(result)
    a, b, c = map(set, result)
    assert (a & b & c) == {(5, 0.3), (1, .21)}
    assert (2, 0) in (a | b | c)
    assert len(a) == 7
    assert len(b) == 3
    assert len(c) == 4
