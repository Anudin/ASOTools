import sys
import argparse
import re
from play_scraper import search as store_search
from unidecode import unidecode
from gensim.parsing.preprocessing import remove_stopwords
from fuzzywuzzy.process import fuzz, extract

# Bash example for counting: python3 main.py ... | sort | uniq -c | sort -hr


def preprocess_descriptions(descriptions):
    def preprocess(description):
        description = re.sub(r"[^\w']+", " ", description).strip()
        description = description.lower()
        return remove_stopwords(description)

    return list(map(preprocess, descriptions))


def string_list_to_word_list(descriptions):
    wordlist_nested = [description.split() for description in descriptions]
    wordlist = [word for sublist in wordlist_nested for word in sublist]
    return wordlist


# ATTENTION Defunced, threshold too low and deduplication missing
def fuzzy_count(wordlist, threshold=70, scorer=fuzz.token_set_ratio):
    """Adapted from fuzzywuzzy.process.dedupe"""
    extractor = {}

    for item in wordlist:
        # return all duplicate matches found
        matches = extract(item, wordlist, limit=None, scorer=scorer)
        filtered = [x for x in matches if x[1] > threshold]
        matches = len(filtered)
        if matches == 1:
            extractor[filtered[0][0]] = 1
        else:
            # alpha sort
            filtered = sorted(filtered, key=lambda x: x[0])
            # length sort
            filter_sort = sorted(filtered, key=lambda x: len(x[0]), reverse=True)
            # take first item as our 'canonical example'
            extractor[filter_sort[0][0]] = matches

    # check that extractor differs from contain_dupes (e.g. duplicates were found)
    # if not, then return the original list
    if len(extractor) == len(wordlist):
        return wordlist
    else:
        return extractor


# TODO Fix fuzzy counting
# TODO More involved logik considering e.g. synonyms
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("search_term")
    parser.add_argument("--only-top", type=int)
    args = parser.parse_args()

    entries = store_search(args.search_term)
    descriptions = [unidecode(entry["description"]) for entry in entries]
    if args.only_top:
        descriptions = descriptions[0 : args.only_top]
    descriptions = preprocess_descriptions(descriptions)
    wordlist = string_list_to_word_list(descriptions)
    print("\n".join(wordlist))
    #  counted = fuzzy_count(wordlist)
    #  print("\n".join([f"{count} {entry}" for entry, count in counted.items()]))
