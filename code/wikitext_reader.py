from regex import findall, match, sub
from os import popen
from html import unescape


class WikitextReader:

    def __init__(self, article_title, pageid, revid, timestamp, wikitext, fix_introduction_heading = False):
        self.article_title = article_title
        self.pageid = pageid
        self.revid = revid
        self.timestamp = timestamp
        self.wikitext = wikitext
        self.fix_introduction_heading = fix_introduction_heading

    def process(self):
        """
        Process the wikitext and extract headings, associated wikitext and categories.

        Headings are identified by two or more leading '=' in line
        and the same number of '=' towards the end of the line.

        '=' characters are cleaned, line is stipped, comments matching
        '&lt;.*&gt;' are removed.

        Categories are identified by lines starting in '[[category:'.
        Markup is removed, categories with '|' are cleaned from the
        character itself and any preceeding characters.

        Returns:
            Tuple of list of heading-level-wikitext lists and list of category strings.
        """
        sections = [[(self.article_title + (" --- Introduction ---" if self.fix_introduction_heading else "")), 1, ""]]
        categories = []
        previous_level = 1
        for line in self.wikitext.split("\n"):
            if line.lower().startswith("[[category:"):
                category = line.lower().replace("[[category:", "")
                category = category.split("]")[0]
                category = category.split("|")[0]
                categories.append(category.strip())
                continue
            matches = findall("==+", line)
            if len(matches) > 1 and matches[0] == matches[-1] and match(matches[0], line):
                level = len(matches[0])
                if level > previous_level + 1:
                    level = previous_level + 1
                else:
                    previous_level = level
                section_heading = line.replace("=", "")
                section_heading = sub("&lt;.*&gt;", "", section_heading)
                sections.append([unescape(section_heading.strip()), level, ""])
            else:
                sections[-1][-1] += line + "\n"
        return sections, categories

    def heading_tree(self, sections):
        """
        Build tree of section headings.

        Args:
            sections: Lists of heading-level-tuples.

        Returns:
            Section heading tree as nested dictionary.
        """
        def recursive_heading_tree(sections, current_level):
            """
            Args:
                sections: Lists of heading-level-tuples.
                current_level: Recursive call parameter for level.
            """
            heading_tree = {}
            if sections:
                super_section_heading = None
                for section_heading, level, text in sections:
                    if level == current_level:
                        heading_tree[section_heading] = []
                        super_section_heading = section_heading
                    else:
                        if super_section_heading == None:
                            heading_tree[section_heading] = []
                        else:
                            heading_tree[super_section_heading].append(
                                [section_heading, level, text])
                for section_heading in heading_tree:
                    heading_tree[section_heading] = recursive_heading_tree(
                        heading_tree[section_heading], current_level + 1)
            return ({(self.article_title + (" --- Introduction ---" if self.fix_introduction_heading else "")):
                     heading_tree[self.article_title + (" --- Introduction ---" if self.fix_introduction_heading else "")]}
                    if current_level == 1 else heading_tree)
        return recursive_heading_tree(sections, 1)

    def section_tree(self, sections, clean_text):
        """
        Build tree of section, nested with the below keys per section:

        'name': name of section
        'level': level of the section, with root at 1
        'parent': name of the parent section
        'path': |-separated path to the section
        'text': wikitext of the section
        'subsections': list of subsection which in turn are section trees themselves

        Args:
            sections: Lists of heading-level-wikitext lists.
            clean_text: Flag to clean wikitext.

        Returns:
            Section tree as nested dictionary.
        """
        def clean(wikitext):
            # HELPER FUNCTION TO CLEAN WIKITEXT
            string = wikitext.replace("\n", " ")
            string = sub("&lt.*?&gt;", "", string)
            string = sub("{{.*?}}", "", string)
            string = sub(" +", " ", string)
            string = sub("http.*? ", " ", string)
            string = sub("\[\[File:.*?\]\]", " ", string)
            return unescape(string).strip()

        def recursive_section_tree(sections, current_level, parent, path, clean_text):
            """
            Args:
                sections: Lists of heading-level-wikitext lists.
                current_level: Recursive call parameter for level.
                parent: Recursive call parameter for parent.
                path: Recursive call parameter for path.
                clean_text: Flag to clean wikitext.
            """
            section_tree = {}
            if sections:
                for section_heading, level, text in sections:
                    cleaned_text = clean(text) if clean_text else text
                    if level == current_level:
                        section_tree["name"] = section_heading
                        section_tree["level"] = level
                        section_tree["parent"] = parent
                        section_tree["path"] = path + section_heading
                        section_tree["text"] = cleaned_text
                        section_tree["subsections"] = []
                    else:
                        if level == current_level + 1:
                            if "subsections" not in section_tree:
                                section_tree["subsections"] = []
                            section_tree["subsections"].append([])
                        section_tree["subsections"][-1].append(
                            [section_heading, level, cleaned_text])
                if "subsections" not in section_tree:
                    section_tree["subsections"] = []
                if "subsections" in section_tree:
                    for i in range(len(section_tree["subsections"])):
                        section_tree["subsections"][i] = recursive_section_tree(section_tree["subsections"][i],
                                                                                current_level + 1,
                                                                                section_tree["name"],
                                                                                section_tree["path"] + "|",
                                                                                clean_text)

            return section_tree
        return recursive_section_tree(sections, 1, None, "", clean_text)

    def find_heading(self, string, node):
        """
        Checks heading tree for string (breadth-first).

        Args:
            string: The string to identify.
            node: The section tree as dictionary to check.

        Returns:
            List of str[] path.
        """
        def recursive_find_heading(string, node, path, results=[]):
            """
            Args:
                string: The string to identify.
                node: The section tree as dictionary to check.
                path: Recursive call parameter for path.
                results: Container for recursive result collection.
            """
            for key in node:
                if string.lower() in key.lower():
                    results.append(path + [key])
            for key in node:
                result = recursive_find_heading(
                    string, node[key], path + [key], results)
            return results
        return recursive_find_heading(string, node, [], [])

    def find_section(self, string, node):
        """
        Checks section tree for string in heading (breadth-first).

        Args:
            string: The string to identify.
            node: The section tree as dictionary to check.

        Returns:
            The node with the string in its name.
        """
        if string.lower() == node["name"].lower():
            return node
        for subsection in node["subsections"]:
            if string.lower() == subsection["name"].lower():
                return subsection
        for subsection in node["subsections"]:
            return self.find_section(string, subsection)
        return None

    def get_text_of_section(self, node, level=float("inf")):
        """
        Get the text of a particular (sub)section.

        Args:
            node: The section tree as dictionary to check.
            level: Depth up to which text will be retrieved.

        Returns:
            The concatenated text of that section.
        """
        class TEXT:
            def __init__(self):
                self.string = ""

        def recursive_get_text_of_section(node, level, text):
            """
            Args:
                node: The section tree as dictionary to check.
                level: Depth up to which text will be retrieved.
            """
            text.string += node["text"] + " "
            if node["level"] < level:
                for subsection in node["subsections"]:
                    recursive_get_text_of_section(subsection, level, text)
            return text
        return recursive_get_text_of_section(node, level, TEXT()).string

    def has_category(self, string, categories):
        return any([string.lower() in category for category in categories])

    def references(self):
        """
        Extract cited references from Wikitext and
        return as list of dictionaries.
        """
        return [{item.split("=" if "=" in item else " ")[0].strip():
                 ("=" if "=" in item else " ").join(item.split("=" if "=" in item else " ")[1:]).strip()
                 for item in [item.strip() for item in citation[2:-2].strip().split("|")]}
                for citation in findall("{{[cC]ite.*?}}", self.wikitext)]

    def debug(self):
        print(self.article_title)
        print(self.revid)
        print(self.timestamp)
        for heading in self.headings:
            print(heading)
        popen("firefox " + "https://en.wikipedia.org/w/index.php?title=" +
              self.article_title + "&oldid=" + self.revid)
