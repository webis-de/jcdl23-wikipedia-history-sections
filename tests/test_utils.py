from code.utils.utils import fleiss
import unittest


class TestUtils(unittest.TestCase):

    def test_fleiss(self):

        # cf. https://en.wikipedia.org/wiki/Fleiss%27_kappa#Worked_example
        matrix = [[0, 0, 0, 0, 14],
                  [0, 2, 6, 4, 2],
                  [0, 0, 3, 5, 6],
                  [0, 3, 9, 2, 0],
                  [2, 2, 8, 1, 1],
                  [7, 7, 0, 0, 0],
                  [3, 2, 6, 3, 0],
                  [2, 5, 3, 2, 2],
                  [6, 5, 2, 1, 0],
                  [0, 2, 2, 3, 7],
                  ]
        # interlabeller data derived from above test matrix
        interlabeller_data = {"doc_01":{"a":4,"b":4,"c":4,"d":4,"e":4,"f":4,"g":4,"h":4,"i":4,"j":4,"k":4,"l":4,"m":4,"n":4},
                              "doc_02":{"a":1,"b":1,"c":2,"d":2,"e":2,"f":2,"g":2,"h":2,"i":3,"j":3,"k":3,"l":3,"m":4,"n":4},
                              "doc_03":{"a":2,"b":2,"c":2,"d":3,"e":3,"f":3,"g":3,"h":3,"i":4,"j":4,"k":4,"l":4,"m":4,"n":4},
                              "doc_04":{"a":1,"b":1,"c":1,"d":2,"e":2,"f":2,"g":2,"h":2,"i":2,"j":2,"k":2,"l":2,"m":3,"n":3},
                              "doc_05":{"a":0,"b":0,"c":1,"d":1,"e":2,"f":2,"g":2,"h":2,"i":2,"j":2,"k":2,"l":2,"m":3,"n":4},
                              "doc_06":{"a":0,"b":0,"c":0,"d":0,"e":0,"f":0,"g":0,"h":1,"i":1,"j":1,"k":1,"l":1,"m":1,"n":1},
                              "doc_07":{"a":0,"b":0,"c":0,"d":1,"e":1,"f":2,"g":2,"h":2,"i":2,"j":2,"k":2,"l":3,"m":3,"n":3},
                              "doc_08":{"a":0,"b":0,"c":1,"d":1,"e":1,"f":1,"g":1,"h":2,"i":2,"j":2,"k":3,"l":3,"m":4,"n":4},
                              "doc_09":{"a":0,"b":0,"c":0,"d":0,"e":0,"f":0,"g":1,"h":1,"i":1,"j":1,"k":1,"l":2,"m":2,"n":3},
                              "doc_10":{"a":1,"b":1,"c":2,"d":2,"e":3,"f":3,"g":3,"h":4,"i":4,"j":4,"k":4,"l":4,"m":4,"n":4}}

        self.assertEqual(round(fleiss(interlabeller_data), 3), 0.210)

if __name__ == "__main__":
    unittest.main()

