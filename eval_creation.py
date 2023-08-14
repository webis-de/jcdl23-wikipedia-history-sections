from json import load, dump
from random import sample
from json import dumps
from os import makedirs
from datetime import datetime
from os.path import sep, exists


def infinite_sample_size(z_score, population_proportion, margin_of_error):
    return (z_score**2 * population_proportion * (1-population_proportion))/margin_of_error**2


def ideal_sample_size(z_score, population_proportion, margin_of_error, population_size):
    iss = infinite_sample_size(z_score, population_proportion, margin_of_error)
    return iss/(1+(iss/population_size))


def wikipedia_revision_url(article_title, revid):
    return ("https://en.wikipedia.org/w/index.php" +
            "?title=" + article_title.replace(" ", "_") +
            "&oldid=" + revid)


CORPUS_DIRECTORY = None

try:
    assert(CORPUS_DIRECTORY is not None)
except AssertionError:
    print("Please set CORPUS_DIRECTORY.")
    exit()

TIMESTAMP = str(datetime.now()).replace(" ", "_").replace(
    "-", "_").replace(":", "_").split(".")[0]

MODE = ["SAMPLE_CREATION", "ARTICLE_PICK"][1]

CONDITION = ['len(entry["heading_tree"][entry["article_title"]]) > 9',
             'len([key for key in entry["heading_tree"][entry["article_title"]].keys()' +
             '     if key not in ["See also", "References", "Bibliography","Further reading", "External links"]]) > 2'][1]

print(CONDITION)

with open(CORPUS_DIRECTORY + sep + "science_and_technology_corpus.json") as corpus_file:
    corpus = load(corpus_file)

if MODE == "SAMPLE_CREATION":
    SAMPLES_DIRECTORY = None

    try:
        assert(SAMPLES_DIRECTORY is not None)
    except AssertionError:
        print("Please set SAMPLES_DIRECTORY.")
        exit()

    SAMPLE_DIRECTORY = (SAMPLES_DIRECTORY + sep + TIMESTAMP)
    SAMPLE_FILEPATH_LARGE = (SAMPLE_DIRECTORY + sep +
                             "science_and_technology_corpus_sample_" + TIMESTAMP + "_large.json")
    SAMPLE_FILEPATH_SMALL = (SAMPLE_DIRECTORY + sep +
                             "science_and_technology_corpus_sample_" + TIMESTAMP + "_small.json")
    sample_entries = []

    # NO HISTORY
    no_history = [entry for entry in corpus
                  if not entry["history_section"] and eval(CONDITION)]
    no_history_size = len(no_history)
    print("Number of articles without history section matching condition:",
          no_history_size)
    print("Ideal sample size: ", ideal_sample_size(
        1.96, 0.5, 0.05, no_history_size))
    SAMPLE_SIZE_1 = int(input("Select sample size:"))
    no_history_sample = sample(no_history, SAMPLE_SIZE_1)
    for entry in no_history_sample:
        sample_entries.append({"article_title": entry["article_title"],
                               "revid": entry["revid"],
                               "science_and_technology": None,
                               "history_section": None,
                               "url": wikipedia_revision_url(entry["article_title"], entry["revid"]),
                               "heading_tree": entry["heading_tree"],
                               "history_section_name": None})
        entry["evaluation"] = {
            "science_and_technology": None, "history_section": None}

    # HISTORY EXACT SECTION TOP LEVEL
    history_exact_section_top_level = [entry for entry in corpus
                                       if entry["history_exact_section_top_level"] and eval(CONDITION)]
    history_exact_section_top_level_size = len(history_exact_section_top_level)
    print("Number of articles with history section at top level matching condition:",
          history_exact_section_top_level_size)
    print("Ideal sample size: ", ideal_sample_size(
        1.96, 0.5, 0.05, history_exact_section_top_level_size))
    SAMPLE_SIZE_2 = int(input("Select sample size:"))
    history_exact_section_top_level_sample = sample(
        history_exact_section_top_level, SAMPLE_SIZE_2)
    for entry in history_exact_section_top_level_sample:
        sample_entries.append({"article_title": entry["article_title"],
                               "revid": entry["revid"],
                               "science_and_technology": None,
                               "history_section": None,
                               "url": wikipedia_revision_url(entry["article_title"], entry["revid"]),
                               "heading_tree": entry["heading_tree"],
                               "history_section_name": None})
        entry["evaluation"] = {
            "science_and_technology": None, "history_section": None}

    if not exists(SAMPLE_DIRECTORY):
        makedirs(SAMPLE_DIRECTORY)

    # WRITE LARGE SAMPLE
    with open(SAMPLE_FILEPATH_LARGE, "w") as file:
        dump({"no_history": no_history_sample,
              "history_exact_section_top_level": history_exact_section_top_level_sample},
             file)

    # WRITE CONDITION
    with open(SAMPLE_DIRECTORY + sep + "sample_condition_" + TIMESTAMP + ".txt", "w") as file:
        file.write(CONDITION + "\n\n")
        file.write("Number of articles without history section matching condition: " +
                   str(no_history_size) + "\n")
        file.write("Sample size: " + str(SAMPLE_SIZE_1) + " (" +
                   str(round(SAMPLE_SIZE_1/no_history_size*100, 2)) + "%)\n\n")
        file.write("Number of articles with history section at top level matching condition: " +
                   str(history_exact_section_top_level_size) + "\n")
        file.write("Sample size: " + str(SAMPLE_SIZE_2) + " (" +
                   str(round(SAMPLE_SIZE_2/history_exact_section_top_level_size*100, 2)) + "%)")

    # WRITE SMALL SAMPLE
    with open(SAMPLE_FILEPATH_SMALL, "w") as file:
        file.write("[\n")
        file.write(",\n".join([dumps(entry) for entry in sample_entries]))
        file.write("\n]")

if MODE == "ARTICLE_PICK":
    EVAL_DIRECTORY = None

    try:
        assert(EVAL_DIRECTORY is not None)
    except AssertionError:
        print("Please set EVAL_DIRECTORY.")
        exit()

    PICK_DIRECTORY = (EVAL_DIRECTORY + "/sample")
    PICK_FILEPATH_LARGE = (PICK_DIRECTORY + sep +
                           "science_and_technology_corpus_pick_" + TIMESTAMP + "_large.json")
    PICK_FILEPATH_SMALL = (PICK_DIRECTORY + sep +
                           "science_and_technology_corpus_pick_" + TIMESTAMP + "_small.json")

    ARTICLE_SELECTION = None

    try:
        assert(ARTICLE_SELECTION is not None)
    except AssertionError:
        print("Please set ARTICLE_SELECTION.")
        exit()

    with open(ARTICLE_SELECTION) as file:
        articles_found_by_classifiers = set(
            [item.strip() for item in file.readlines()])
    pick_entries = [entry for entry in corpus if (not entry["history_section"]
                                                  and eval(CONDITION)
                                                  and entry["article_title"] 
                                                  in articles_found_by_classifiers)]

    if not exists(PICK_DIRECTORY):
        makedirs(PICK_DIRECTORY)

    # WRITE LARGE SAMPLE
    with open(PICK_FILEPATH_LARGE, "w") as file:
        dump({"no_history": pick_entries}, file)
    # WRITE SMALL SAMPLE
    with open(PICK_FILEPATH_SMALL, "w") as file:
        file.write("[\n")
        file.write(",\n".join([dumps({"article_title": entry["article_title"],
                                      "revid":entry["revid"],
                                      "science_and_technology":None,
                                      "history_section":None,
                                      "url":wikipedia_revision_url(entry["article_title"], entry["revid"]),
                                      "heading_tree":entry["heading_tree"],
                                      "history_section_name":None}) for entry in pick_entries]))
        file.write("\n]")
