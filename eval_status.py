from os import sep
from code.utils.utils import custom_rounded_string_percent, custom_rounded_string_3, fleiss
from json import load
from glob import glob
from sklearn.metrics import cohen_kappa_score


SAMPLE_FILEPATH = None
try:
    assert(SAMPLE_FILEPATH is not None)
except AssertionError:
    print("Please set SAMPLE_FILEPATH.")
    exit()

LABEL_DIRECTORY = None
try:
    assert(LABEL_DIRECTORY is not None)
except AssertionError:
    print("Please set LABEL_DIRECTORY.")
    exit()

INTERLABELLER_NUMBER = None
try:
    assert(INTERLABELLER_NUMBER is not None)
except AssertionError:
    print("Please set INTERLABELLER_NUMBER.")
    exit()

with open(SAMPLE_FILEPATH) as file:
    sample = load(file)

science_and_technology = len(
    [e for e in sample if e["science_and_technology"] == True])
not_science_and_technology = len(
    [e for e in sample if e["science_and_technology"] == False])
na = len([e for e in sample if e["science_and_technology"] is None])

no_history_science_and_technology = len(
    [e for e in sample[:340] if e["science_and_technology"] == True])
no_history_not_science_and_technology = len(
    [e for e in sample[:340] if e["science_and_technology"] == False])

history_exact_section_top_level_science_and_technology = len(
    [e for e in sample[340:] if e["science_and_technology"] == True])
history_exact_section_top_level_not_science_and_technology = len(
    [e for e in sample[340:] if e["science_and_technology"] == False])

print("Number of S&T articles:",
      science_and_technology,
      custom_rounded_string_percent(science_and_technology/(science_and_technology+not_science_and_technology)))
print("Number of NON-S&T articles:",
      not_science_and_technology,
      custom_rounded_string_percent(not_science_and_technology/(science_and_technology+not_science_and_technology)))

print("Number of articles without designated history section which are S&T:",
      no_history_science_and_technology,
      custom_rounded_string_percent(no_history_science_and_technology/(no_history_science_and_technology+no_history_not_science_and_technology)))
print("Number of articles without designated history section which are NOT S&T",
      no_history_not_science_and_technology,
      custom_rounded_string_percent(no_history_not_science_and_technology/(no_history_science_and_technology+no_history_not_science_and_technology)))

print("Number of articles with designated history section which are S&T:",
      history_exact_section_top_level_science_and_technology,
      custom_rounded_string_percent(history_exact_section_top_level_science_and_technology/(history_exact_section_top_level_science_and_technology+history_exact_section_top_level_not_science_and_technology)))
print("Number of articles with designated history section which are NOT S&T",
      history_exact_section_top_level_not_science_and_technology,
      custom_rounded_string_percent(history_exact_section_top_level_not_science_and_technology/(history_exact_section_top_level_science_and_technology+history_exact_section_top_level_not_science_and_technology)))

print("Number unlabelled:", na)

print()

no_history = sample[:340]
history_exact_section_top_level = sample[340:]

history_or_no_history_map = {}

for title in no_history:
    history_or_no_history_map[title["article_title"]] = False
for title in history_exact_section_top_level:
    history_or_no_history_map[title["article_title"]] = True

annotated_articles = {}
interlabeller_data = {}
interlabellers = {}

filenames = sorted(glob(LABEL_DIRECTORY + sep + "annotated/*.json"))

for index, filename in enumerate(filenames):
    with open(filename) as file:
        username = filename.split("/")[-1].split(".")[0]
        batch = load(file)
        if INTERLABELLER_NUMBER in username:
            interlabellers[username] = []
            for entry in batch:
                if entry["article_title"] not in interlabeller_data:
                    interlabeller_data[entry["article_title"]] = {}
                interlabeller_data[entry["article_title"]
                                   ][username] = entry["history_section"]
                interlabellers[username].append(int(entry["history_section"]) if type(
                    entry["history_section"]) == bool else -1)

    while True:
        articles_without_designated_history_section = [article for article in batch if
                                                       history_or_no_history_map[article["article_title"]] == False]
        articles_with_designated_history_section = [article for article in batch if
                                                    history_or_no_history_map[article["article_title"]] == True]
        labelled_articles = [
            article for article in batch if article["history_section"] is not None]
        labelled_articles_labeled_history = [
            article for article in batch if article["history_section"] == True]
        labelled_articles_without_designated_history_section_labeled_history = [article for article in batch
                                                                                if article["history_section"] == True
                                                                                and history_or_no_history_map[article["article_title"]] == False]
        labelled_articles_labeled_no_history = [
            article for article in batch if article["history_section"] == False]
        labelled_articles_with_designated_history_section_labeled_no_history = [article for article in batch
                                                                                if article["history_section"] == False
                                                                                and history_or_no_history_map[article["article_title"]] == True]
        unlabelled_articles = [
            article for article in batch if article["history_section"] is None]
        print(username)
        print("\tcould not label", len(unlabelled_articles), "article" +
              ("s" if len(unlabelled_articles) != 1 else "") + ":")
        unlabelled_articles_without_designated_history = [article for article in unlabelled_articles
                                                          if not history_or_no_history_map[article["article_title"]]]
        print("\t\t -", len(unlabelled_articles_without_designated_history),
              "article" + ("s" if len(unlabelled_articles_without_designated_history) != 1 else "") + " without designated history section.")
        unlabelled_articles_with_designated_history = [article for article in unlabelled_articles
                                                       if history_or_no_history_map[article["article_title"]]]
        print("\t\t -", len(unlabelled_articles_with_designated_history),
              "article" + ("s" if len(unlabelled_articles_with_designated_history) != 1 else "") + " with designated history section.")
        print("\tNumber of articles without designated history section labelled as having a history section:",
              len(labelled_articles_without_designated_history_section_labeled_history),
              custom_rounded_string_percent(len(labelled_articles_without_designated_history_section_labeled_history) /
                                     len(articles_without_designated_history_section)))
        for article in labelled_articles_without_designated_history_section_labeled_history:
            print("\t\t -", article["article_title"])
        print("\tNumber of articles with designated history section labelled as not having a history section:",
              len(labelled_articles_with_designated_history_section_labeled_no_history),
              custom_rounded_string_percent(len(labelled_articles_with_designated_history_section_labeled_no_history) /
                                     len(articles_with_designated_history_section)))
        for article in labelled_articles_with_designated_history_section_labeled_no_history:
            print("\t\t -", article["article_title"])
        for annotated_article in batch:
            annotated_articles[annotated_article["article_title"]] = (annotated_article["history_section"]
                                                                      if annotated_article["history_section"] is not None
                                                                      else "UNCLEAR")
                                                                      
        if INTERLABELLER_NUMBER not in filename or username == INTERLABELLER_NUMBER + "_interlabeller_accumulated":
            print("="*110)
            break
        else:
            print("-"*110)
            if len(interlabellers) != len([filename for filename in filenames if INTERLABELLER_NUMBER in filename]):
                break
            else:
                username = INTERLABELLER_NUMBER + "_interlabeller_accumulated"
                for entry in batch:
                    # cast majority vote for accumulated batch
                    if list(interlabeller_data[entry["article_title"]].values()).count(True) > len(interlabellers)/2:
                        entry["history_section"] = True
                    elif list(interlabeller_data[entry["article_title"]].values()).count(False) > len(interlabellers)/2:
                        entry["history_section"] = False
                    else:
                        entry["history_section"] = None

for article in no_history:
    if article["article_title"] in annotated_articles:
        article["history_section"] = annotated_articles[article["article_title"]]


for article in history_exact_section_top_level:
    if article["article_title"] in annotated_articles:
        article["history_section"] = annotated_articles[article["article_title"]]

print()

for name, sample_subset in [("no_history", no_history), ("history_exact_section_top_level", history_exact_section_top_level)]:
    print("Number of article in", name, "sample:", len(sample_subset))
    number_of_articles_with_history_section = len(
        [article for article in sample_subset if article["history_section"] == True])
    number_of_articles_without_history_section = len(
        [article for article in sample_subset if article["history_section"] == False])
    number_of_articles_with_unclear_history_section = len(
        [article for article in sample_subset if article["history_section"] == "UNCLEAR"])
    number_of_unlabelled_articles = len(
        [article for article in sample_subset if article["history_section"] is None])

    with open(LABEL_DIRECTORY + "/articles_" + name + "_with_history_section.txt", "w") as file:
        for article in [article for article in sample_subset if article["history_section"] == True]:
            file.write(article["article_title"] + "\n")

    print("Number of articles with history section:", number_of_articles_with_history_section,
          custom_rounded_string_percent(number_of_articles_with_history_section / (number_of_articles_with_history_section +
                                                                            number_of_articles_without_history_section +
                                                                            number_of_articles_with_unclear_history_section)))
    print("Number of articles without history section:", number_of_articles_without_history_section,
          custom_rounded_string_percent(number_of_articles_without_history_section / (number_of_articles_with_history_section +
                                                                               number_of_articles_without_history_section +
                                                                               number_of_articles_with_unclear_history_section)))
    print("Number of unclear articles:", number_of_articles_with_unclear_history_section,
          custom_rounded_string_percent(number_of_articles_with_unclear_history_section / (number_of_articles_with_history_section +
                                                                                    number_of_articles_without_history_section +
                                                                                    number_of_articles_with_unclear_history_section)))
    print("Number of unlabelled articles:", number_of_unlabelled_articles)

    print()

print("Interlabeller Disagreement:")
print(" "*50 + "".join([labeller.ljust(15, " ") for labeller in interlabellers]))
for article_title, judgements in interlabeller_data.items():
    if len(set([str(judgements[labeller]).ljust(10, " ") for labeller in interlabellers])) > 1:
        print(article_title.ljust(50, " ") +
              "".join([str(judgements[labeller]).ljust(15, " ") for labeller in interlabellers]))

print()

print("Cohen's Kappa:")
print(" "*15 + "".join([labeller.rjust(15, " ") for labeller in interlabellers]))
for labeller1 in interlabellers:
    print(labeller1.rjust(15, " ") + "".join([(custom_rounded_string_3(cohen_kappa_score(interlabellers[labeller1], interlabellers[labeller2]))
                                              if labeller1 != labeller2 else "-").rjust(15, " ")
                                              for labeller2 in interlabellers]))
print("Fleiss's Kappa:", custom_rounded_string_3(fleiss(interlabeller_data)))
