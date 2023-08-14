from code.wikipedia_dump_reader import WikipediaDumpReader
import unittest


class TestWikipediaDumpReader(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.input_filepath = "tests/data/wikipedia_dump.bz2"

    def test_iterator(self):

        titles = []
        pageids = []
        revids = []
        texts = []

        with WikipediaDumpReader(self.input_filepath) as wdr:
            for title, pageid, revid, timestamp, text in wdr.line_iter():
                if title not in titles:
                    titles.append(title)
                if pageid not in pageids:
                    pageids.append(pageid)
                if revid not in revids:
                    revids.append(revid)
                texts.append(text)

        self.maxDiff = None
        self.assertEqual(len(titles), 2)
        self.assertEqual(titles[0], "1.6 Band")
        self.assertEqual(titles[1], "Derek Panza")
        self.assertEqual(len(pageids), 2)
        self.assertEqual(pageids[0], "27121496")
        self.assertEqual(pageids[1], "27121502")
        self.assertEqual(len(revids), 193 - 11)
        self.assertEqual(revids[0], "358506549")
        self.assertEqual(revids[-1], "918238989")
        self.assertEqual(len(texts), 193 - 11)

        with open("tests/data/first_text.txt") as file:
            self.assertEqual(texts[0], "".join(file.readlines()))
        with open("tests/data/final_text.txt") as file:
            self.assertEqual(texts[-1], "".join(file.readlines()))


if __name__ == "__main__":
    unittest.main()
