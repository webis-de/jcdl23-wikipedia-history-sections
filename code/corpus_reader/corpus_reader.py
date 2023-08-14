from tkinter import *
from tkinter import filedialog as fd
from json import load
from json.decoder import JSONDecodeError
from regex import sub
from html import unescape
import webbrowser

class CorpusReader:

    def __init__(self):
       
        self.root = Tk()
        self.root.resizable(False, False)

        while True:
            try:
                filepath = fd.askopenfilename(initialdir = ".")#"../../../corpora/webis-WikiSciTech-23.json"#
                with open(filepath) as file:
                    self.corpus_full = sorted(load(file), key=lambda entry: entry["article_title"].lower())
                break
            except JSONDecodeError:
                continue
            except TypeError:
                exit()
        self.corpus = self.corpus_full.copy()
        
        self.root.title("Webis Science & Technology History Corpus")
        

        self.radio_selection = IntVar()
        self.radio_selection.set(1)

        self.options = [
            ("all history sections", 1),
            ("designated exact match history sections", 2),
            ("designated fuzzy match history sections", 3),
            ("non-designated history sections", 4)
        ]

        self.label_article_title = Label(
            self.root, text="Article Title:", width=30, anchor=W)
        self.label_article_title.grid(row=0, column=0, columnspan=2)
        self.text_article_title = Text(self.root, height=1, width=29, padx=5, pady=5)
        self.text_article_title.grid(row=0, column=2, columnspan=1)
        self.text_article_title.config(state=DISABLED)

        self.label_pageid = Label(
            self.root, text="Page ID:", width=30, anchor=W)
        self.label_pageid.grid(row=1, column=0, columnspan=2)
        self.text_pageid = Text(self.root, height=1, width=29, padx=5, pady=5)
        self.text_pageid.grid(row=1, column=2, columnspan=1)
        self.text_pageid.config(state=DISABLED)

        self.label_revid = Label(
            self.root, text="Revision ID:", width=30, anchor=W)
        self.label_revid.grid(row=2, column=0, columnspan=2)
        self.text_revid = Text(self.root, height=1, width=29, padx=5, pady=5)
        self.text_revid.grid(row=2, column=2, columnspan=1)
        self.text_revid.config(state=DISABLED)

        self.label_timestamp = Label(
            self.root, text="Timestamp:", width=30, anchor=W)
        self.label_timestamp.grid(row=3, column=0, columnspan=2)
        self.text_timestamp = Text(self.root, height=1, width=29, padx=5, pady=5)
        self.text_timestamp.grid(row=3, column=2, columnspan=1)
        self.text_timestamp.config(state=DISABLED)

        self.check_selection = IntVar()
        check_button_text = ("clean Wikitext")# +
##                             "(remove URLs," +
##                             " filelinks," +
##                             " references," +
##                             " surplus spaces and" +
##                             " template data)")
        self.clean_text_check = Checkbutton(self.root, text=check_button_text, variable=self.check_selection, onvalue=1, command=self.article_selection, height = 2)
        self.clean_text_check.grid(row=5, column=0, columnspan=1, sticky=W)

        self.listbox = Listbox(self.root, height=50, width=29)
        self.listbox.grid(row=6, column=0)
        self.listbox.bind("<<ListboxSelect>>", self.article_selection)

        self.scrollbar_listbox = Scrollbar(
            self.root, width=15, orient="vertical", command=self.listbox.yview)
        self.scrollbar_listbox.grid(row=6, column=1, sticky="ns", pady=2)
        self.listbox['yscrollcommand'] = self.scrollbar_listbox.set

        self.text_section_text = Text(self.root, height=53, width=74)
        self.text_section_text.config(state=DISABLED)
        self.text_section_text.grid(row=6, column=2, columnspan=2)
        self.scrollbar_textbox = Scrollbar(
            self.root, width=15, orient="vertical", command=self.text_section_text.yview)
        self.scrollbar_textbox.grid(row=6, column=4, sticky="ns", pady=1)
        self.text_section_text['yscrollcommand'] = self.scrollbar_textbox.set

        for index, article_title in enumerate([entry["article_title"] for entry in self.corpus], 1):
            self.listbox.insert(index, unescape(article_title).strip())

        for txt, val in self.options:
            r = Radiobutton(self.root,
                            text=txt,
                            variable=self.radio_selection,
                            command=lambda: self.corpus_selection(
                                self.radio_selection.get()),
                            value=val,
                            width=40,
                            anchor=W)
            r.grid(row=val-1, column=3)

        self.url_label = Label(self.root, fg="blue", cursor="hand1", wraplength=0, height = 2)
        self.url_label.grid(row=5, column=1, columnspan=4, sticky="w")
        
        self.article_selection()       
        
        self.root.mainloop()

    def open_url(self, url):
        webbrowser.open(url)

    def clean_wikitext(self, wikitext):
        # HELPER FUNCTION TO CLEAN WIKITEXT
        string = wikitext#.replace("\n", " ")
        string = sub("&lt.*?&gt;", "", string)
        string = sub("{{.*?}}", "", string)
        string = sub(" +", " ", string)
        string = sub("http.*? ", " ", string)
        string = sub("\[\[File:.*?\]\]", " ", string)
        return unescape(string).strip()

    def update_textbox(self, textbox, content):
        textbox.configure(state='normal')
        textbox.delete('1.0', END)
        textbox.insert(END, content)
        textbox.configure(state='disabled')
        textbox.bind("<Button>", textbox.focus_set())

    def article_selection(self, placeholder=None):
        try:
            selection = self.listbox.curselection()[0]
        except:
            selection = 0
        
        self.update_textbox(self.text_article_title,
                            unescape(self.corpus[selection]["article_title"]).strip())
        self.update_textbox(
            self.text_pageid, self.corpus[selection]["pageid"])
        self.update_textbox(
            self.text_revid, self.corpus[selection]["revid"])
        self.update_textbox(
            self.text_timestamp, self.corpus[selection]["timestamp"][:-1].split("T"))
        self.update_textbox(self.text_section_text, ("\n\n" + "="*74).join([k + "\n\n" + (self.clean_wikitext(v) if self.check_selection.get() == 1 else v) for k, v in self.corpus[selection]["history_section_texts"].items()]))
        URL = "https://en.wikipedia.org/w/index.php?title=" + self.text_article_title.get("1.0",END).strip() + "&oldid=" + self.text_revid.get("1.0",END)
        URL_TEXT = ("\n" + URL) if len(URL) < 80 else URL[:80] + "..."
        self.url_label.bind("<Button-1>", lambda e: self.open_url(URL))
        self.url_label.config(text=URL_TEXT)

    def corpus_selection(self, option):
        for textbox in [self.text_article_title, self.text_pageid, self.text_revid, self.text_timestamp, self.text_section_text]:
            textbox.configure(state='normal')
            textbox.delete("1.0", END)
            textbox.configure(state='disabled')
            textbox.bind("<Button>", textbox.focus_set())
        self.url_label.config(text="")
        selection = option
        if selection:
            self.listbox.delete(0, END)
            if selection == 1:
                self.corpus = self.corpus_full.copy()
            if selection == 2:
                self.corpus = [
                    entry for entry in self.corpus_full if entry["history_section_designated_exact"]]
            if selection == 3:
                self.corpus = [
                    entry for entry in self.corpus_full if entry["history_section_designated_fuzzy"]]
            if selection == 4:
                self.corpus = [
                    entry for entry in self.corpus_full if entry["history_section_non_designated"]]
            for index, article_title in enumerate([entry["article_title"] for entry in self.corpus], 1):
                self.listbox.insert(index, unescape(article_title).strip())


##with open("corpora/webis-WikiSciTech-23.json") as file:
##    corpus_full = sorted(
##        load(file), key=lambda entry: entry["article_title"].lower())

cr = CorpusReader()
