from csv import writer
from regex import search
from os import makedirs
from os.path import sep
from datetime import datetime
from json import load, dumps
from code.wikipedia_dump_reader import WikipediaDumpReader
from code.wikitext_reader import WikitextReader


def write_meta(directory, entry_count,
               article_count, history_count, history_exact_count, history_top_level_count, history_exact_top_level_count,
               science_and_technology_count, science_and_technology_history_count, science_and_technology_history_exact_count,
               science_and_technology_history_top_level_count, science_and_technology_history_exact_top_level_count,
               start):
    with open(directory + sep + "meta.csv", "w") as meta_file:
        meta_file.write(",".join(["entry_count",
                                  "article_count",
                                  "history_count",
                                  "history_exact_count",
                                  "history_top_level_count",
                                  "history_exact_top_level_count"]))
        meta_file.write("\n")
        meta_file.write(",".join([str(value) for value in
                                  [entry_count,
                                   article_count,
                                   history_count,
                                   history_exact_count,
                                   history_top_level_count,
                                   history_exact_top_level_count]]))
        meta_file.write("\n")
        meta_file.write(",".join(["",
                                  "science_and_technology_count",
                                  "science_and_technology_history_count",
                                  "science_and_technology_history_exact_count",
                                  "science_and_technology_history_top_level_count",
                                  "science_and_technology_history_exact_top_level_count"]))
        meta_file.write("\n")
        meta_file.write(",".join([str(value) for value in
                                  ["",
                                   science_and_technology_count,
                                   science_and_technology_history_count,
                                   science_and_technology_history_exact_count,
                                   science_and_technology_history_top_level_count,
                                   science_and_technology_history_exact_top_level_count]]))
        meta_file.write("\n")
        meta_file.write(str(datetime.now() - start))

# path to Wikipedia dump file
DUMP_PATH = None
try:
    assert(DUMP_PATH is not None)
except AssertionError:
    print("Please set DUMP_PATH.")
    exit()

# path to output directory for corpus
CORPUS_DIRECTORY = None
try:
    assert(CORPUS_DIRECTORY is not None)
except AssertionError:
    print("Please set CORPUS_DIRECTORY.")
    exit()

# list of stopwords in titles to exclude articles
with open("resources/stoptitles.json") as file:
    stoptitles = load(file)

# list of stopwords in caetegories to exclude articles
stopcats = []
with open("resources/stopcats.json") as file:
    for valuelist in load(file).values():
        for value in valuelist:
            stopcats.append(value)

start = datetime.now()
output_directory = CORPUS_DIRECTORY + sep + \
    str(start).replace(" ", "_").replace(
        "-", "_").replace(":", "_").split(".")[0]
makedirs(output_directory)

wdr = WikipediaDumpReader(DUMP_PATH)

science_and_technology_corpus = []
FIRST_CORPUS_ENTRY = True

with open(output_directory + sep + "results.csv", "w") as result_file, \
        open(output_directory + sep + "science_and_technology_corpus.json", "w") as corpus_file:

    corpus_file.write("[")

    result_csv_writer = writer(result_file, delimiter=",")
    result_csv_writer.writerow(["article_title",
                                "pageid",
                                "history_section",
                                "history_exact_section",
                                "history_section_top_level",
                                "history_exact_section_top_level",
                                "history_path",
                                "categories",
                                "heading_tree"])

    entry_count = 0
    article_count = 0
    history_count = 0
    history_exact_count = 0
    history_top_level_count = 0
    history_exact_top_level_count = 0
    science_and_technology_count = 0
    science_and_technology_history_count = 0
    science_and_technology_history_exact_count = 0
    science_and_technology_history_top_level_count = 0
    science_and_technology_history_exact_top_level_count = 0

    for article_title, pageid, revid, timestamp, wikitext in wdr.line_iter():

        wtr = WikitextReader(article_title, pageid, revid, timestamp, wikitext)
        sections, categories = wtr.process()
        heading_tree = wtr.heading_tree(sections)
        entry_count += 1

        if heading_tree[article_title]:
            article_count += 1
            if article_count % 10000 == 0:
                write_meta(output_directory, entry_count,
                           article_count, history_count, history_exact_count, history_top_level_count, history_exact_top_level_count,
                           science_and_technology_count, science_and_technology_history_count, science_and_technology_history_exact_count,
                           science_and_technology_history_top_level_count, science_and_technology_history_exact_top_level_count,
                           start)

            history_paths = wtr.find_heading(
                "history", heading_tree) + wtr.find_heading("histori", heading_tree)
            history_paths_lowered = [[segment.lower() for segment in history_path[1:]]
                                     for history_path in history_paths if history_path[1:]]
            history_section = False
            history_exact_section = False
            history_section_top_level = False
            history_exact_section_top_level = False

            if history_paths_lowered:
                history_section = True
                for history_path_lowered in history_paths_lowered:
                    if "history" in history_path_lowered:
                        history_exact_section = True
                    if "history" in history_path_lowered[0] or "histori" in history_path_lowered[0]:
                        history_section_top_level = True
                    if history_path_lowered[0] == "history":
                        history_exact_section_top_level = True

            if history_section:
                history_count += 1
            if history_exact_section:
                history_exact_count += 1
            if history_section_top_level:
                history_top_level_count += 1
            if history_exact_section_top_level:
                history_exact_top_level_count += 1

            result_csv_writer.writerow([article_title,
                                        pageid,
                                        history_section,
                                        history_exact_section,
                                        history_section_top_level,
                                        history_exact_section_top_level,
                                        history_paths,
                                        categories,
                                        heading_tree])
            result_file.flush()

            no_stoptitle = True
            for stoptitle in stoptitles:
                if stoptitle in article_title.lower():
                    no_stoptitle = False
                    break

            if no_stoptitle and not search("\d\d\d\d", article_title):
                if any(["technolog" in category for category in categories]):
                    if not any([any([stopcat in category for stopcat in stopcats]) for category in categories]):
                        corpus_entry = {"article_title": article_title,
                                        "pageid": pageid,
                                        "revid": revid,
                                        "timestamp": timestamp,
                                        "history_section": history_section,
                                        "history_exact_section": history_exact_section,
                                        "history_section_top_level": history_section_top_level,
                                        "history_exact_section_top_level": history_exact_section_top_level,
                                        "history_paths": history_paths,
                                        "categories": categories,
                                        "heading_tree": heading_tree,
                                        "wikitext": wikitext}

                        if FIRST_CORPUS_ENTRY:
                            corpus_file.write("\n" + dumps(corpus_entry))
                            FIRST_CORPUS_ENTRY = False
                        else:
                            corpus_file.write(",\n" + dumps(corpus_entry))
                        corpus_file.flush()

                        science_and_technology_count += 1

                        if history_section:
                            science_and_technology_history_count += 1
                        if history_exact_section:
                            science_and_technology_history_exact_count += 1
                        if history_section_top_level:
                            science_and_technology_history_top_level_count += 1
                        if history_exact_section_top_level:
                            science_and_technology_history_exact_top_level_count += 1

            if article_count % 100000 == 0:
                print("entries:", entry_count)
                print("articles:", article_count)
                print("with history:", history_count)
                print("with exact history:", history_exact_count)
                print("with history at top level:", history_top_level_count)
                print("with exact history at top level:",
                      history_exact_top_level_count)
                print("science_and_technology_count",
                      science_and_technology_count)
                print("science_and_technology_history_count",
                      science_and_technology_history_count)
                print("science_and_technology_history_exact_count",
                      science_and_technology_history_exact_count)
                print("science_and_technology_history_top_level_count",
                      science_and_technology_history_top_level_count)
                print("science_and_technology_history_exact_top_level_count",
                      science_and_technology_history_exact_top_level_count)
                print("time:", datetime.now() - start)
                print()

    write_meta(output_directory, entry_count,
               article_count, history_count, history_exact_count, history_top_level_count, history_exact_top_level_count,
               science_and_technology_count, science_and_technology_history_count, science_and_technology_history_exact_count,
               science_and_technology_history_top_level_count, science_and_technology_history_exact_top_level_count,
               start)

    corpus_file.write("\n]")
