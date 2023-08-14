from json import load, dumps
from random import shuffle
from os.path import exists, sep
from os import makedirs


def write_sample(directory, entries, username):
    path = directory + sep + username + ".json"
    if not exists(directory):
        makedirs(directory)
    with open(path, "w") as file:
        file.write("[\n")
        file.write(",\n".join([dumps(entry) for entry in entries]))
        file.write("\n]")

SAMPLE_FILEPATH = None

try:
    assert(SAMPLE_FILEPATH is not None)
except AssertionError:
    print("Please set SAMPLE_FILEPATH.")
    exit()

OUTPUT_DIRECTORY = None

try:
    assert(OUTPUT_DIRECTORY is not None)
except AssertionError:
    print("Please set OUTPUT_DIRECTORY.")
    exit()

if not exists(OUTPUT_DIRECTORY):
        makedirs(OUTPUT_DIRECTORY)

LABELLER_EVALUATION = 2

if LABELLER_EVALUATION == 1:

    # S&T labelled data is sample basis for first labeller evaluation
    with open(SAMPLE_FILEPATH) as file:
        sample = load(file)

    end = False
    while not end:
        # split sample data in shards with designated and without designated history section
        no_history = sample[:340]
        shuffle(no_history)
        history_exact_section_top_level = sample[340:]
        shuffle(history_exact_section_top_level)

        titles = set()
        title_sets = []
        for i in range(10):
            username = str(i+1).rjust(3, "0")
            entries = no_history[34*i:34*(i+1)] + \
                history_exact_section_top_level[31*i:31*(i+1)]
            shuffle(entries)
            title_sets.append(set())
            for entry in entries:
                if entry["article_title"] == "HTTP+HTML form-based authentication":
                    # ensure that article no longer on Wikipedia is put in 10th batch
                    if i == 9:
                        end = True
                    note = "HTTP+HTML form-based authentication in " + username + "."
                    with open(OUTPUT_DIRECTORY + sep + "notes.txt", "w") as file:
                        file.write(note)
                titles.add(entry["article_title"])
                title_sets[-1].add(entry["article_title"])
            write_sample(OUTPUT_DIRECTORY, entries, username)
            print("S&T count in", username, "is:", len(
                [entry for entry in entries if entry["science_and_technology"]]))
        print(note)

    assert(len(titles) == 650)
    intersection = set()
    for title_set in title_sets:
        intersection = intersection.intersection(title_set)
    assert(len(intersection) == 0)

if LABELLER_EVALUATION == 2:

    with open(SAMPLE_FILEPATH) as file:
        sample = load(file)

    NO_HISTORY_WITH_HISTORY_SECTION_FILEPATH = None

    try:
        assert(NO_HISTORY_WITH_HISTORY_SECTION_FILEPATH is not None)
    except AssertionError:
        print("Please set NO_HISTORY_WITH_HISTORY_SECTION_FILEPATH.")
        exit()

    with open(NO_HISTORY_WITH_HISTORY_SECTION_FILEPATH) as file:
        articles_no_history_with_history_section = [
            line.strip() for line in file.readlines()]

    # set all articles to be S&T
    for entry in sample:
        entry["science_and_technology"] = True

    # articles known to contain history section but history section name not labelled as not implemented in evaluator during first evaluation
    sample_known_to_contain_history_section_from_eval_002 = [entry for entry in sample
                                                             if entry["article_title"] in articles_no_history_with_history_section]

    # set articles known to contain history
    for entry in sample_known_to_contain_history_section_from_eval_002:
        entry["history_section"] = True

    sample_not_known_to_contain_history_section_from_eval_002 = [entry for entry in sample
                                                                 if entry["article_title"] not in articles_no_history_with_history_section]

    print(len(sample_not_known_to_contain_history_section_from_eval_002))

    shuffle(sample_not_known_to_contain_history_section_from_eval_002)

    title_sets = []
    for index, i in enumerate([1, 2, 3, 4, 5, 6, 8, 9, 10]):
        username = str(i).rjust(3, "0")
        entries = sample_not_known_to_contain_history_section_from_eval_002[100*index:100*(
            index+1)]
        if i == 10:
            entries = sample_known_to_contain_history_section_from_eval_002 + entries
            with open(OUTPUT_DIRECTORY + sep + "notes.txt", "a") as file:
                file.write(
                    ("in " + username + ", already known to contain history section from evaluation:").upper() + "\n\n")
            for entry in sample_known_to_contain_history_section_from_eval_002:
                with open(OUTPUT_DIRECTORY + sep + "notes.txt", "a") as file:
                    file.write(entry["article_title"] + "\n")
        title_sets.append(set([entry["article_title"] for entry in entries]))
        write_sample(OUTPUT_DIRECTORY, entries, username)
        print("S&T count in", username, "is:", len(
            [entry for entry in entries if entry["science_and_technology"]]))
        print("H count in", username, "is:", len(
            [entry for entry in entries if entry["history_section"]]))

    assert(len(sample) == 928)
    intersection = set()
    for title_set in title_sets:
        intersection = intersection.intersection(title_set)
    assert(len(intersection) == 0)
