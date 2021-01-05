from pathlib import Path
import pandas as pd
import nltk.tokenize
import re


cur_file = Path(__file__).parent.absolute()


def untokenize(words):
    """
    Untokenizing a text undoes the tokenizing operation, restoring
    punctuation and spaces to the places that people expect them to be.
    Ideally, `untokenize(tokenize(text))` should be identical to `text`,
    except for line breaks.
    """
    # From https://stackoverflow.com/a/34682849
    text = ' '.join(words)
    step1 = text.replace("`` ", '"').replace(" ''", '"').replace('. . .',  '...')
    step2 = step1.replace(" ( ", " (").replace(" ) ", ") ")
    step3 = re.sub(r' ([.,:;?!%]+)([ \'"`])', r"\1\2", step2)
    step4 = re.sub(r' ([.,:;?!%]+)$', r"\1", step3)
    step5 = step4.replace(" '", "'").replace(" n't", "n't").replace(
         "can not", "cannot")
    step6 = step5.replace(" ` ", " '")
    return step6.strip()


def unmerge_data_with_merged_cells(df: pd.DataFrame):
    """When loading a csv with merged cells the merge value only appears at the top.
    This function with propogate the top value to the null values below"""
    rows = df.to_dict(orient='records')
    for i, row in enumerate(rows):
        for col, val in row.items():
            if pd.isnull(val):
                row[col] = rows[i - 1][col]
    return pd.DataFrame(rows)


def get_survey_data():
    return pd.read_csv(cur_file / "labels/part1_survey_data.csv")


def update_text(row):
    text = row.text.lower()
    if row['dataset'] == "PersonaChat":
        return untokenize(text.split())
    return text


def get_tfidf_distract():
    data = pd.read_csv(cur_file / "labels/tfidf_labeldata.csv")
    data['text_unproc'] = data.apply(update_text, axis=1)
    #print(data[['dataset', 'text_unproc']])
    return data


def get_codeguide_table():
    data = pd.read_csv(cur_file / "labels/codeingguide_table_examples.csv")
    data = unmerge_data_with_merged_cells(data)
    data.replace({"Label": {"Pos": "p", "AIC": "a", "Neg": "n"}}, inplace=True)
    return data


def get_neg_from_rand():
    data = pd.read_csv(cur_file / "labels/randsample_labeldata.csv")
    data['text_unproc'] = data.apply(update_text, axis=1)
    return data


if __name__ == "__main__":
    print(untokenize("yes . i live on a farm , actually . you ?".split()))
    #get_tfidf_distract()
    get_codeguide_table()
