from code.wikitext_reader import WikitextReader
from json import load as json_load
from os.path import sep

CONDITION = ['len(entry["heading_tree"][entry["article_title"]]) > 9',
             'len([key for key in entry["heading_tree"][entry["article_title"]].keys()' +
             ' if key not in ["See also", "References", "Bibliography","Further reading", "External links"]]) > 2'][1]

CORPUS_DIRECTORY = None

try:
    assert(CORPUS_DIRECTORY is not None)
except AssertionError:
    print("Please set CORPUS_DIRECTORY.")
    exit()
    
LEVEL = "section"

with open(CORPUS_DIRECTORY + sep + "science_and_technology_corpus.json") as file:
    ARTICLES = [entry for entry in json_load(file)
                if (entry["history_exact_section_top_level"] if LEVEL == "section" else True) and
                eval(CONDITION)]

heading_map = {}
sizes = {"0": 0,
         "1": 0,
         "2-10": 0,
         "11-100": 0,
         "101-1000": 0,
         "1000+": 0}

for count, entry in enumerate(ARTICLES, 1):
    print(count)
    wtr = WikitextReader(entry["article_title"],
                         entry["pageid"],
                         entry["revid"],
                         entry["timestamp"],
                         entry["wikitext"])
    sections, categories = wtr.process()
    section_tree = wtr.section_tree(sections, True)
    top_level_headings = list(
        entry["heading_tree"][entry["article_title"]].keys())
    for heading in top_level_headings:
        section = wtr.find_section(heading, section_tree)
        section_text = wtr.get_text_of_section(section)
        size = len(section_text)

        if heading not in ["See also", "Sources", "References", "Bibliography", "Further reading", "External links"]:
            if size == 0:
                sizes["0"] += 1
            elif size == 1:
                sizes["1"] += 1
            elif size <= 11:
                sizes["2-10"] += 1
            elif size <= 101:
                sizes["11-100"] += 1
            elif size <= 1001:
                sizes["101-1000"] += 1
            else:
                sizes["1000+"] += 1
        #heading = heading.lower()
        if heading not in heading_map:
            heading_map[heading] = 0
        heading_map[heading] += 1

print("Section length distribution:")
print("\t", sizes)

heading_map = {k: heading_map[k] for k in sorted(heading_map.keys(),
                                                 key=lambda k: heading_map[k],
                                                 reverse=True)}
print("Frequency of boilerplate sections:")
for heading in ["References",
                "External links",
                "See also",
                "Notes",
                "Further reading",
                "Bibliography",
                "Sources",
                "Footnotes",
                "Notes and references",
                "References and notes",
                "External sources",
                "Links",
                "References and sources"]:
    print("\t", heading, heading_map.get(heading, "N/A"))
