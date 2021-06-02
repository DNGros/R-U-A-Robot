"""utility scrips to count how much hand labeled data"""
from datatoy.survey_data import get_survey_data, get_tfidf_distract, get_neg_from_rand, get_test_r_data


def main():
    rand = get_tfidf_distract()
    rand = rand.drop_duplicates('text').groupby("pos_amb_neg").agg(['count'])
    print(rand)
    rand = get_test_r_data()
    rand = rand.groupby("pos_amb_neg").agg(['count'])
    print(rand)


if __name__ == "__main__":
    main()