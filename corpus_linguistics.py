import random
from csv import writer
from json import load
from os.path import sep
import matplotlib.pyplot as plt
from regex import search
from code.preprocessor.preprocessor import Preprocessor
from code.wikitext_reader import WikitextReader

# path to corpus directory
CORPUS_DIRECTORY = None
try:
    assert(CORPUS_DIRECTORY is not None)
except AssertionError:
    print("Please set CORPUS_DIRECTORY.")
    exit()

# path to linguistic analysis directory
LINGUISTIC_ANALYSIS_DIRECTORY = None
try:
    assert(LINGUISTIC_ANALYSIS_DIRECTORY is not None)
except AssertionError:
    print("Please set LINGUISTIC_ANALYSIS_DIRECTORY.")
    exit()

DOI_REGEX = "10\.\d{4,9}/[-\._;\(\)/:a-zA-Z0-9]+"

preprocessor = Preprocessor("en", [])

# ENTRY KEYS
# 'article_title', 'pageid', 'revid', 'timestamp',
# 'history_section', 'history_exact_section', 'history_section_top_level', 'history_exact_section_top_level',
# 'history_paths', 'categories', 'heading_tree', 'wikitext'

with open(CORPUS_DIRECTORY + sep + "science_and_technology_corpus.json") as file:
    articles = load(file)

headings_map = {}
category_map = {}
TOKENS = {}
regex_count = 0
with open(LINGUISTIC_ANALYSIS_DIRECTORY + sep + "history_section_exact_top_level_tokens.csv", "w") as token_file:
    csv_writer = writer(token_file, delimiter=",")
    for entry_count, entry in enumerate(articles, 1):
        # REPORT ARTICLE COUNT
        if entry_count % 1000 == 0:
            print(entry_count)
        # COUNT DOIS
        if search(DOI_REGEX, entry["wikitext"]):
            regex_count += 1
        # COLLECT CATEGORIES
        for category in entry["categories"]:
            if category not in category_map:
                category_map[category] = 0
            category_map[category] += 1
        # ANALYSE TOP LEVEL HISTORY SECTION
        if entry.get("history_exact_section_top_level", None):
            wtr = WikitextReader(entry["article_title"],
                                 entry["pageid"],
                                 entry["revid"],
                                 entry["timestamp"],
                                 entry["wikitext"])
            sections, categories = wtr.process()
            for heading in [item[0] for item in sections]:
                if heading not in headings_map:
                    headings_map[heading] = 0
                headings_map[heading] += 1
            assert(categories == entry["categories"])
            section_tree = wtr.section_tree(sections, True)
            history_section = wtr.find_section("History", section_tree)
            if history_section["path"] != entry["article_title"] + "|" + "History":
                print(history_section["path"])
            history_section_text = wtr.get_text_of_section(history_section)
            tokens = preprocessor.preprocess(
                history_section_text, True, True, False, True)[0]
            tokens = {token: tokens.count(token)
                      for token in tokens if len(token) > 1}
            tokens = {token: tokens[token] for token in sorted(tokens.keys(),
                                                               key=lambda token: tokens[token],
                                                               reverse=True)[:25]}
            token_row = []
            for token, count in tokens.items():
                token_row.append(token)
                token_row.append(count)
                if token not in TOKENS:
                    TOKENS[token] = 0
                TOKENS[token] += 1
            csv_writer.writerow([entry["article_title"], entry.get(
                "history_paths", entry.get("history_path"))] + token_row)
            token_file.flush()
print("regex_count", regex_count)
print("articles", len(articles))
print("categories", len(category_map))

# OVERALL TOKEN COUNT
TOKENS = {token: TOKENS[token] for token in sorted(TOKENS.keys(),
                                                   key=lambda token: TOKENS[token],
                                                   reverse=True)}
with open(LINGUISTIC_ANALYSIS_DIRECTORY + sep + "history_section_exact_top_level_tokens_overall.csv", "w") as overall_token_file:
    csv_writer = writer(overall_token_file, delimiter=",")
    for token, count in TOKENS.items():
        csv_writer.writerow([token, count])

# SORT CATEGORIES BY COUNT
category_map = {category: category_map[category] for category in sorted(category_map.keys(),
                                                                        key=lambda category: category_map[category],
                                                                        reverse=True)}


# GET AND WRITE ARTICLE TITLES
article_titles = sorted([article["article_title"] for article in articles])
with open(LINGUISTIC_ANALYSIS_DIRECTORY + sep + "article_titles.txt", "w") as file:
    file.write("\n".join(article_titles))

# ARTICLE SAMPLE (LaTeX)
sample = random.sample(article_titles, 90)
with open(LINGUISTIC_ANALYSIS_DIRECTORY + sep + "presentation-article-sample.txt", "w") as file:
    for i in range(30):
        file.write(sample[i] + " & " + sample[i+30] +
                   " & " + sample[i+60] + "\\\\" + "\n")
        file.write("\\hline" + "\n")

# TOP50 CATEGORIES (LaTeX)
top50 = [k + " & " + str(category_map[k])
         for k in list(category_map.keys())[:50]]
with open(LINGUISTIC_ANALYSIS_DIRECTORY + sep + "presentation-top50-categories.txt", "w") as file:
    for i in range(50):
        file.write("\\textbf{" + str(i + 1) + "} & " +
                   top50[i] + "\\\\" + "\n")
        file.write("\\hline" + "\n")

# STOPCATS (LaTeX)
with open(LINGUISTIC_ANALYSIS_DIRECTORY + sep + "stopcats.json") as file:
    stopcats = load(file)
stopwords = []
for valuelist in stopcats.values():
    for value in valuelist:
        stopwords.append(value)
with open(LINGUISTIC_ANALYSIS_DIRECTORY + sep + "presentation-stopcats.txt", "w") as file:
    for key, value in stopcats.items():
        file.write("\\coloritem[darkgray]" + "\n")
        file.write("{\\color{\\emcolor} " + key + "}: '" +
                   "', '".join(value) + "'" + "\n")

# PLOT CATEGORY DISTRIBUTION
plt.figure(dpi=300)
x = [i for i in range(len(category_map.keys()))]
y = list(category_map.values())
plt.plot(x, y, label="science_or_technology_and_not_stopcat_no_year".replace(
    "_", " "), color="black")
plt.xlabel("category")
plt.ylabel("frequency")
plt.semilogy(base=10)
plt.legend()
plt.savefig(LINGUISTIC_ANALYSIS_DIRECTORY + sep +
            "figure-" +
            "science_or_technology_and_not_stopcat_no_year_no_list".replace("_", "-") + ".png")

headings_map = {heading:headings_map[heading] for heading in sorted(headings_map.keys(), key=lambda heading: headings_map[heading], reverse=True)}

i = 0
for heading in headings_map:
    i += 1
    print(heading, headings_map[heading])
    if i == 20:
        break
