from tkinter import Listbox, Tk, Label, Button, CENTER, simpledialog, StringVar, Scrollbar, Frame
from requests import get
from json import load, dumps
from os.path import exists, sep
import webbrowser
from platform import system


class Evaluator:
    def __init__(self, directory, to_label):
        root = Tk()
        root.configure(background="ghost white")
        root.geometry("900x700")
        self.to_label = to_label
        root.title("WIKIPEDIA SCIENCE & TECHNOLOGY EVALUATOR")
        root.withdraw()
        username_query = "Enter username:"
        while True:
            self.username = simpledialog.askstring(
                title="USERNAME", prompt=username_query)
            if self.username is None:
                exit()
            self.sample_filepath = (
                (directory + sep) if directory != "" else "") + self.username + ".json"
            if not exists(self.sample_filepath):
                response = get(
                    "https://files.webis.de/thesis-kircheis-eval/" + self.sample_filepath)
                if response.status_code == 404:
                    username_query = "User not found. Enter username:"
                    continue
                else:
                    with open(self.sample_filepath, "wb") as file:
                        file.write(response.content)
                        break
            else:
                break
        # READ SAMPLE FILE, SET INDEX TO FIRST ARTICLE WITHOUT JUDGEMENT OR INCORRECT LABELLING E.G. HISTORY SECTION AND NONE SELECTED
        with open(self.sample_filepath) as file:
            self.articles = load(file)
        root.deiconify()
        self.index = 0
        for index, article in enumerate(self.articles):
            if (article[self.to_label] is None or
                (article[self.to_label] == True and not article["history_section_name"]) or
                    (article[self.to_label] == False and article["history_section_name"])):
                self.index = index
                break

        # GUI MEASURES
        M100 = 100
        M80 = int(M100 * 0.8)
        M60 = int(M100 * 0.6)
        M40 = int(M100 * 0.4)
        M20 = int(M100 * 0.2)

        # SET UP GRID
        root.rowconfigure(0, weight=1)
        root.rowconfigure(1, weight=1)
        root.rowconfigure(2, weight=1)
        root.rowconfigure(3, weight=1)
        root.rowconfigure(4, weight=1)
        root.rowconfigure(5, weight=1)
        root.rowconfigure(6, weight=1)
        root.rowconfigure(7, weight=1)
        root.rowconfigure(8, weight=1)
        root.rowconfigure(9, weight=1)
        root.columnconfigure(0, weight=1)
        root.columnconfigure(1, weight=1)
        root.columnconfigure(2, weight=1)
        root.columnconfigure(3, weight=1)
        root.columnconfigure(4, weight=1)

        self.r = 0xff
        self.g = 0x0
        self.b = 0x0
        os = system().lower()
        if os == "linux":
            self.colour_timer = 3
        else:
            self.colour_timer = 1
        '''
        # HELP TEXTS
        self.helptext1 = ("Does this article have a History Section, i.e. a subsection, preferably at top level,\n" +
                          "which outlines the historical development of this innovation/technology/concept?")
        self.helptext2 = ("Click this text to see the most straight-forward example (Nuclear power).")
        self.helptext3 = ("The section does not necessarily need to have the word 'history' in its title.")     
        self.helptext4 = ("Click this text to see an example where it is captioned 'Origins' (Nanotechnology).")            
        self.helptext5 = ("It could also be at a lower level, but if located too deep in the sections tree it might\n" +
                          "just describe the history of a specific use instead of the innovation/technology in general.")
        self.helptext6 = ("Click this text to see an example where two sections labeled 'history' outline the\n" +
                          "history of applications of the technology this article describes (Data compression).")

        # HELP LABELS
        self.help_label1 = Label(root, bg = "ghost white", width=M100, height=3,
                                 text=self.helptext1, anchor="s")
        self.help_label2 = Label(root, bg = "ghost white", width=M60, height=2, fg="darkgray", cursor="hand2",
                                 text=self.helptext2, anchor="n")
        self.help_label2.bind("<Button-1>", self.open_example1_in_browser)
        
        self.help_label3 = Label(root, bg = "ghost white", width=M100, height=1,
                                 text=self.helptext3, anchor="s")
        self.help_label4 = Label(root, bg = "ghost white", width=M60, height=2, fg="darkgray", cursor="hand2",
                                 text=self.helptext4, anchor="n")
        self.help_label4.bind("<Button-1>", self.open_example2_in_browser)
        
        self.help_label5 = Label(root, bg = "ghost white", width=M100, height=2,
                                 text=self.helptext5, anchor="s",)
        self.help_label6 = Label(root, bg = "ghost white", width=M60, height=3, fg="darkgray", cursor="hand2",
                                 text=self.helptext6, anchor="n")
        self.help_label6.bind("<Button-1>", self.open_example3_in_browser)
        '''
        # ARTICLE LABEL
        self.article_label_count_variable = StringVar()
        self.article_label_count = Label(root, bg="lightgrey", width=20, height=1, textvariable=self.article_label_count_variable,
                                         font="Helvetica 16 bold")
        self.article_label_title_variable = StringVar()
        self.article_label_title = Label(root, bg="lightgrey", width=80, height=1, textvariable=self.article_label_title_variable,
                                         font="Helvetica 16 bold", anchor="sw")

        # URL LABEL
        self.url_label_variable = StringVar()
        self.url_label = Label(root, bg="lightgrey", width=M80, height=1,
                               textvariable=self.url_label_variable, fg="blue", cursor="hand2", anchor="nw")
        self.url_label.bind("<Button-1>", self.open_url_in_browser)

        # HISTORY SECTION NAME LABEL AND LISTBOX
        self.history_section_name_label = Label(root, bg="ghost white", width=M20, height=21, anchor=CENTER,
                                                text=("\n".join(["In this part of the evaluation you once again decide",
                                                                 "if a given Wikipedia article has any sections which",
                                                                 "detail the history of a technology or innovation.",
                                                                 " ",
                                                                 "This time you also have to select the headings of",
                                                                 "the sections which you think describe the history",
                                                                 "of this technology or innovation from the list of",
                                                                 "headings you can see on the right. You can only",
                                                                 "select sections at the top level, not sub-sections.",
                                                                 " ",
                                                                 "'[ARTICLE TITLE] --- Introduction ---' refers to the",
                                                                 "text just above the box that says 'Contents' and might",
                                                                 "not exist for each and every article you have to label.",
                                                                 "If it does not exists, simply ignore this heading.",
                                                                 " ",
                                                                 "You can select more than one heading from the list.",
                                                                 "You can un-select a heading by clicking it again.",
                                                                 " ",
                                                                 "Articles in this evaluation will not have a designated",
                                                                 "history section, i.e. with the exact heading 'History'.",
                                                                 " ",
                                                                 "However, some will have a section that describes the",
                                                                 "history. As an example, look at the section 'Origins'",
                                                                 "in the Wikipedia article on 'Nanotechnology':"]))
                                                )
        self.history_section_name_label_link = Label(root, bg="ghost white", width=M20, height=1, anchor="n", cursor="hand2", fg="blue",
                                                     text="Nanotechnology")
        self.history_section_name_label_link.bind(
            "<Button-1>", self.open_example2_in_browser)

        self.frame = Frame(root, height=22)
        self.scrollbar = Scrollbar(self.frame, orient="vertical", width=15)
        self.listbox = Listbox(self.frame, selectmode="multiple",
                               yscrollcommand=self.scrollbar.set, selectbackground="light blue", height=22)
        self.listbox.pack(side="left", expand=True, fill="both")
        self.scrollbar.config(command=self.listbox.yview)
        self.scrollbar.pack(side="right", fill="y")

        # BUTTONS

        self.button_ye = Button(
            root, text="YES", width=M40, height=1, command=self.yes)
        self.button_na = Button(
            root, text="NOT LABELED/\nI DON'T KNOW", width=M20, height=1, command=self.na)
        self.button_no = Button(
            root, text="NO", width=M40, height=1, command=self.no)

        self.button_prevprev = Button(
            root, text="<<", width=M20, height=2, command=self.prevprev)
        self.button_prev = Button(
            root, text="<", width=M20, height=2, command=self.prev)
        self.button_find = Button(
            root, text="NEXT UNLABELED", width=M20, height=2, command=self.find)
        self.button_next = Button(
            root, text=">", width=M20, height=2, command=self.next)
        self.button_nextnext = Button(
            root, text=">>", width=M20, height=2, command=self.nextnext)

        # PACK ALL ELEMENTS
        """
        self.article_box.pack(expand=True, fill='both')
        """
        self.article_label_count.grid(
            column=0, row=0, rowspan=2, sticky='NSEW')
        self.article_label_title.grid(
            column=1, row=0, columnspan=4, sticky='NSEW')
        self.url_label.grid(column=1, row=1, columnspan=4, sticky='NSEW')

        self.history_section_name_label.grid(
            column=0, columnspan=2, row=2, rowspan=6, sticky='NSEW')
        self.history_section_name_label_link.grid(
            column=0, columnspan=2, row=8, sticky='NSEW')
        self.frame.grid(column=2, row=2, rowspan=7,
                        columnspan=3, sticky="NSEW")
        '''
        self.help_label1.grid(column=0, row=2, columnspan=5, sticky='NSEW')
        self.help_label2.grid(column=1, row=3, columnspan=3, sticky='NSEW')
        self.help_label3.grid(column=0, row=4, columnspan=5, sticky='NSEW')
        self.help_label4.grid(column=1, row=5, columnspan=3, sticky='NSEW')
        self.help_label5.grid(column=0, row=6, columnspan=5, sticky='NSEW')
        self.help_label6.grid(column=1, row=7, columnspan=3, sticky='NSEW')
        '''
        self.button_ye.grid(column=0, row=9, columnspan=2, sticky='NSEW')
        self.button_na.grid(column=2, row=9, sticky='NSEW')
        self.button_no.grid(column=3, row=9, columnspan=2, sticky='NSEW')

        self.button_prevprev.grid(column=0, row=10, sticky='NSEW')
        self.button_prev.grid(column=1, row=10, sticky='NSEW')
        self.button_find.grid(column=2, row=10, sticky='NSEW')
        self.button_next.grid(column=3, row=10, sticky='NSEW')
        self.button_nextnext.grid(column=4, row=10, sticky='NSEW')

        self.update()
        self.open_url_in_browser(None)

        root.mainloop()

    def map_evaluation_state(self, evaluation_state):
        return {True: "YES",
                False: "NO",
                None: "N/A"}[evaluation_state]

    def open_url_in_browser(self, event):
        webbrowser.open(self.url_label_variable.get().strip())

    def open_example1_in_browser(self, event):
        webbrowser.open(
            "https://en.wikipedia.org/w/index.php?title=Nuclear_power&oldid=1080251670")

    def open_example2_in_browser(self, event):
        webbrowser.open(
            "https://en.wikipedia.org/w/index.php?title=Nanotechnology&oldid=1065752578")

    def open_example3_in_browser(self, event):
        webbrowser.open(
            "https://en.wikipedia.org/w/index.php?title=Data_compression&oldid=1079974790")

    def update(self):
        self.article_label_count_variable.set(
            str(self.index + 1) + "/" + str(len(self.articles)))
        self.article_label_title_variable.set(
            self.articles[self.index]["article_title"])
        self.url_label_variable.set(self.articles[self.index]["url"])
        self.listbox.delete(0, self.listbox.size())
        headings = ([self.articles[self.index]["article_title"] + " --- Introduction ---"] +
                    list(self.articles[self.index]["heading_tree"]
                         [self.articles[self.index]["article_title"]].keys()))
        for index, section_heading in enumerate(headings, 1):
            self.listbox.insert(index, section_heading)
        if self.articles[self.index]["history_section_name"] is not None:
            for heading in self.articles[self.index]["history_section_name"]:
                self.listbox.select_set(headings.index(heading))

        self.button_ye["background"] = "light blue" if self.articles[self.index][self.to_label] == True else "lightgray"
        self.button_no["background"] = "light blue" if self.articles[self.index][self.to_label] == False else "lightgray"
        self.button_na["background"] = "light blue" if self.articles[self.index][self.to_label] is None else "lightgray"

    def save(self):
        self.articles[self.index]["history_section_name"] = self.get_selected_headings()
        with open(self.sample_filepath, "w", newline="", encoding="utf-8") as file:
            file.write("[\n")
            file.write(",\n".join([dumps(article)
                       for article in self.articles]))
            file.write("\n]")

    def decrement(self):
        self.index -= 1
        if self.index == -1:
            self.index = len(self.articles) - 1
            return 1
        return 0

    def increment(self):
        self.index += 1
        if self.index == len(self.articles):
            self.index = 0
            return 1
        return 0

    def change_color(self):
        self.listbox.config(
            bg="#" + "".join([str(hex(c)).split("x")[-1].rjust(2, "0") for c in [self.r, self.g, self.b]]))
        if self.g != 0xff and self.b != 0xff:
            self.g += 1
            self.b += 1
            self.listbox.after(self.colour_timer, self.change_color)
        else:
            self.g = 0x0
            self.b = 0x0

    def get_selected_headings(self):
        headings = []
        for index in self.listbox.curselection():
            headings.append(self.listbox.get(index))
        return headings

    def find(self):
        if ((self.articles[self.index][self.to_label] == True and self.get_selected_headings())
                or (self.articles[self.index][self.to_label] in [False, None] and not self.get_selected_headings())):
            self.save()
            self.increment()
            if [entry[self.to_label] for entry in self.articles].count(None) != 0:
                while True:
                    self.update()
                    if self.articles[self.index][self.to_label] is None:
                        break
                    elif self.articles[self.index][self.to_label] == True and not self.get_selected_headings():
                        break
                    elif self.articles[self.index][self.to_label] in [False, None] and self.get_selected_headings():
                        break
                    self.increment()
                self.open_url_in_browser(None)
            else:
                self.index = 0
                webbrowser.open(
                    "https://c.tenor.com/x8v1oNUOmg4AAAAd/rickroll-roll.gif")
            self.update()
        else:
            self.change_color()

    def yes(self):
        if self.get_selected_headings():
            self.articles[self.index][self.to_label] = True
            self.save()
            self.find()
        else:
            self.change_color()

    def no(self):
        if not self.get_selected_headings():
            self.articles[self.index][self.to_label] = False
            self.save()
            self.find()
        else:
            self.change_color()

    def na(self):
        if not self.get_selected_headings():
            self.articles[self.index][self.to_label] = None
            self.save()
            self.find()
        else:
            self.change_color()

    def prev(self):
        if ((self.articles[self.index][self.to_label] == True and self.get_selected_headings())
                or (self.articles[self.index][self.to_label] in [False, None] and not self.get_selected_headings())):
            self.save()
            self.decrement()
            self.update()
            if self.articles[self.index][self.to_label] is None:
                self.open_url_in_browser(None)
        else:
            self.change_color()

    def prevprev(self):
        if ((self.articles[self.index][self.to_label] == True and self.get_selected_headings())
                or (self.articles[self.index][self.to_label] in [False, None] and not self.get_selected_headings())):
            self.save()
            for i in range(10):
                self.decrement()
            self.update()
            if self.articles[self.index][self.to_label] is None:
                self.open_url_in_browser(None)
        else:
            self.change_color()

    def next(self):
        if ((self.articles[self.index][self.to_label] == True and self.get_selected_headings())
                or (self.articles[self.index][self.to_label] in [False, None] and not self.get_selected_headings())):
            self.save()
            self.increment()
            self.update()
            if self.articles[self.index][self.to_label] is None:
                self.open_url_in_browser(None)
        else:
            self.change_color()

    def nextnext(self):
        if ((self.articles[self.index][self.to_label] == True and self.get_selected_headings())
                or (self.articles[self.index][self.to_label] in [False, None] and not self.get_selected_headings())):
            self.save()
            for i in range(10):
                self.increment()
            self.update()
            if self.articles[self.index][self.to_label] is None:
                self.open_url_in_browser(None)
        else:
            self.change_color()


if __name__ == "__main__":
    app = Evaluator("", "history_section")
