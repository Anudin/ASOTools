import sys
import re
from play_scraper import search as store_search
from unidecode import unidecode
from gensim.parsing.preprocessing import remove_stopwords
from fuzzywuzzy.process import fuzz, extract

# Bash example for counting: python3 main.py ... | sort | uniq -c | sort -hr


def preprocess_descriptions(descriptions):
    descriptions = [
        re.sub(r"[^\w']+", " ", description).strip() for description in descriptions
    ]
    descriptions = [description.lower() for description in descriptions]
    descriptions = [remove_stopwords(description) for description in descriptions]
    return descriptions


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
    if len(sys.argv) != 2:
        print("Please pass exactly one search string.")
        sys.exit(1)

    entries = store_search("sudoku")
    descriptions = [unidecode(entry["description"]) for entry in entries]
    descriptions = preprocess_descriptions(descriptions)
    wordlist = string_list_to_word_list(descriptions)
    print("\n".join(wordlist))
    #  counted = fuzzy_count(wordlist)
    #  print("\n".join([f"{count} {entry}" for entry, count in counted.items()]))
