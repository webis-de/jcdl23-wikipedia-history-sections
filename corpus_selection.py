from json import load, dumps 
from glob import glob
from os import sep
from code.wikitext_reader import WikitextReader
from pprint import pprint

# ARTICLE CONDITION
CONDITION = ['len(entry["heading_tree"][entry["article_title"]]) > 9',
             'len([key for key in entry["heading_tree"][entry["article_title"]].keys()' +
             ' if key not in ["See also", "References", "Bibliography","Further reading", "External links"]]) > 2'][1]

CORPUS_DIRECTORY = None
try:
    assert(CORPUS_DIRECTORY is not None)
except AssertionError:
    print("Please set CORPUS_DIRECTORY.")
    exit()

EVAL_DIRECTORY = None
try:
    assert(EVAL_DIRECTORY is not None)
except AssertionError:
    print("Please set EVAL_DIRECTORY.")
    exit()

eval_filepaths = glob(EVAL_DIRECTORY + sep + "*.json")

with open(CORPUS_DIRECTORY + sep + "science_and_technology_corpus.json") as file:
    corpus = load(file)

eval_results = {}

for eval_filepath in eval_filepaths:
    with open(eval_filepath) as file:
        eval_result = load(file)
        for result in eval_result:
            eval_results[result["article_title"]] = result

corpus_compiled = []

articles_with_history_section_designated_exact = set()
articles_with_history_section_designated_fuzzy = set()
articles_with_history_section_non_designated = set()

for entry in corpus:
    
    article_title = entry["article_title"]
    pageid = entry["pageid"]
    revid = entry["revid"]
    timestamp = entry["timestamp"]
    wikitext = entry["wikitext"]

    wtr = WikitextReader(article_title, pageid, revid, timestamp, wikitext, fix_introduction_heading=True)
    sections, categories = wtr.process()
    
    heading_tree = wtr.heading_tree(sections)
    section_tree = wtr.section_tree(sections, clean_text=False)

    # CHECK AND MARK ARTICLES FOR NUMBER OF SECTIONS
    entry["more_than_two_sections_excluding_boilerplate"] = eval(CONDITION)

    # CHECK FOR EXACT OR FUZZY DESIGNATED HISTORY SECTION AT TOP LEVEL
    has_designated_history_section = entry['history_exact_section_top_level'] or entry['history_section_top_level']

    #CHECK NON-DESIGNATED HISTORY SECTION AT TOP LEVEL
    has_non_designated_history_section = article_title in eval_results and eval_results[article_title]["history_section"] == True

    entry["history_section_designated_exact"] = False
    entry["history_section_designated_fuzzy"] = False
    entry["history_section_non_designated"] = False

    if has_designated_history_section or has_non_designated_history_section:

        history_section_texts = {}

        # ADD HISTORY PATHS FROM EVAL RESULTS
        if not entry["history_paths"]:
            for history_section_name in eval_results[article_title]["history_section_name"]:
                entry["history_paths"] += wtr.find_heading(history_section_name, heading_tree)
        else:
            entry["history_paths"] = [[history_path[0] + (" --- Introduction ---" if wtr.fix_introduction_heading else "")] +
                                      history_path[1:] for history_path in entry["history_paths"]]
            
        for history_path in entry["history_paths"]:

            # IN CASE ARTICLE CONTAINS BOTH TOP LEVEL AND LOWER LEVEL HISTORY SECTIONS, ONLY CONSIDER TOP LEVEL SECTIONS
            if len(history_path) > 2:
                entry["history_paths"].remove(history_path)
                continue

            history_section = wtr.find_section(history_path[-1], section_tree)
            history_section_text = wtr.get_text_of_section(history_section)
            history_section_texts["|".join(history_path)] = history_section_text.strip()

            if history_path[-1].lower() == "history":
                entry["history_section_designated_exact"] = True
                articles_with_history_section_designated_exact.add(article_title)
            elif "history" in history_path[-1].lower() or "histori" in history_path[-1].lower():
                entry["history_section_designated_fuzzy"] = True
                articles_with_history_section_designated_fuzzy.add(article_title)
            else:
                entry["history_section_non_designated"] = True
                articles_with_history_section_non_designated.add(article_title)

        del entry["wikitext"]
        entry["history_section_texts"] = history_section_texts
        entry["heading_tree"] = heading_tree

        del entry["history_section"]
        del entry["history_exact_section"]
        del entry["history_section_top_level"]
        del entry["history_exact_section_top_level"]

        corpus_compiled.append(entry)

with open(CORPUS_DIRECTORY + sep + "webis-WikiSciTech-23.json", "w") as file:
    file.write("[\n")
    file.write(",\n".join([dumps(item) for item in corpus_compiled]))
    file.write("\n]")    

print(len(corpus_compiled))
print("articles_with_history_section_designated_exact:", len(articles_with_history_section_designated_exact))
print("articles_with_history_section_designated_fuzzy:", len(articles_with_history_section_designated_fuzzy))
print("articles_with_history_section_non_designated:", len(articles_with_history_section_non_designated))
