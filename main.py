from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from api_details import links, find_nani, tags
from api_functions import fetch_base_url, fetch_titles, fetch_chaps, fetch_key_hash_manga, fetch_key_hash_chapter
from PIL import Image
import sys
import re
import requests
import os
from threading import Thread
import queue
import faulthandler
faulthandler.enable()


class MangaWorker(QThread):
    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.queue = queue.Queue(maxsize=0)

    def run(self):
        while True:
            item = self.queue.get()
            mode = item[0]
            manga_name = item[1]
            manga_cache = item[2]
            if mode == "Chapter":
                manga_chapters = item[3]
                fetch_key_hash_chapter(manga_name, manga_cache, manga_chapters)
            else:
                fetch_key_hash_manga(manga_name, manga_cache)
            self.queue.task_done()

    def queue_chapter(self, manga_name, manga_cache, manga_chapters):
        print("{} {} has been queued!".format(manga_name, manga_chapters))
        self.queue.put(["Chapter", manga_name, manga_cache, manga_chapters])

    def queue_manga(self, manga_name, manga_cache):
        print("{} has been queued!".format(manga_name))
        self.queue.put(["Manga", manga_name, manga_cache])


class Window(QWidget):

    def __init__(self,):
        super().__init__()

        self.setWindowTitle("Python ")
        window_width, window_height = 794, 511
        window_startingpoint = 0
        self.setGeometry(window_startingpoint, window_startingpoint, window_width, window_height)
        self.ui_components()
        self.manga_worker_1 = MangaWorker()
        self.manga_worker_1.start()

        self.searched_dict = {}
        self.clicked_manga_list = []
        self.tmp_data_dict = {}
        self.searched_chaps = {}
        self.last_selected_title = ""
        self.last_selected_chapter = ""
        self.hidden_title_rows = []
        self.searched_cache = {}
        self.chapters_pressed = []
        self.center()
        self.show()


    def closeEvent(self, event):
        pass


    def set_button_flat(self, button, change_image, icon_dir=None):
        button.setFlat(True)
        button.setStyleSheet("QPushButton:pressed {background-color: transparent;}")
        if change_image:
            button.setIcon(QtGui.QIcon(icon_dir))

    def ui_components(self):
        self.title_listbox = QListWidget(self)
        self.chapter_listbox = QListWidget(self)
        self.chapter_listbox.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.search_box = QLineEdit(self)
        self.current_status = QLabel("Status: ", self )
        self.main_layout = QGridLayout(self)

        download_chapter_button = QPushButton("Download Chapter", self)
        download_manga_button = QPushButton("Download Manga", self)
        search_button = QPushButton("Search", self)
        manga_header = QLabel("Manga Titles: ",self)
        chapter_header = QLabel("Chapters: ",self )
        self.doujin_checkbox = QCheckBox("Doujinshi", self)
        self.chapter_numbers = QLineEdit("Input the chapters here ex: 20-50", self)


        self.set_button_flat(search_button, True, "components/search.png")
        self.set_button_flat(download_chapter_button, True, "components/download.png")
        self.set_button_flat(download_manga_button, True, "components/download.png")

        self.main_layout.addWidget(self.current_status,0, 0)
        # second row. We use a QHBoxlayout to layout the QLineEdit and the two buttons
        hlayout = QHBoxLayout(self)
        hlayout.setContentsMargins(0,0,0,0)
        hlayout.addWidget(self.search_box)
        hlayout.addWidget(search_button)
        hlayout.addWidget(download_chapter_button)
        hlayout.addWidget(download_manga_button)
        # add QHLayout to second row in grid layout
        self.main_layout.addLayout(hlayout, 1, 0, 1, 2)

        self.main_layout.addWidget(manga_header, 2, 0)
        self.main_layout.addWidget(chapter_header, 2, 1)
        self.main_layout.addWidget(self.title_listbox, 3, 0)
        self.main_layout.addWidget(self.chapter_listbox, 3, 1)

        # add checkbox
        self.main_layout.addWidget(self.doujin_checkbox, 4, 0)
        self.main_layout.addWidget(self.chapter_numbers, 4, 1)
        manga_header.setFont(QFont("Yu Gothic UI Light", 16))
        chapter_header.setFont(QFont("Yu Gothic UI Light", 16))
        #setting up widgets' functions / signals
        search_button.clicked.connect(self.clicked_search)
        download_chapter_button.clicked.connect(self.clicked_download_chapter)
        download_manga_button.clicked.connect(self.clicked_download_manga)
        self.title_listbox.itemClicked.connect(self.title_box_selectionChanged)
        self.chapter_listbox.itemClicked.connect(self.chapter_box_box_selectionChanged)
        self.doujin_checkbox.stateChanged.connect(self.doujin_checkboxToggled)

        titles_scrollbar = QScrollBar(self)
        chapters_scrollbar = QScrollBar(self)

        # setting style sheet to the scroll bar
        titles_scrollbar.setStyleSheet("background : lightgreen;")
        chapters_scrollbar.setStyleSheet("background : lightgreen;")

        self.title_listbox.setVerticalScrollBar(titles_scrollbar)
        self.chapter_listbox.setVerticalScrollBar(chapters_scrollbar)
        value = self.title_listbox.verticalScrollBar()
        value2 = self.chapter_listbox.verticalScrollBar()

    def clicked_download_manga(self):
        self.manga_worker_1.queue_manga(self.last_selected_title, self.searched_cache)

    def clicked_download_chapter(self):
        tmp_clist = []
        for c in self.chapter_listbox.selectedItems():
            tmp_clist.append(c.text())
        self.manga_worker_1.queue_chapter(self.last_selected_title, self.searched_cache, tmp_clist)

    def clicked_search(self):
        self.hidden_title_rows.clear()
        self.title_listbox.clear()
        self.searched_dict.clear()
        manga_title = self.search_box.text()
        if self.doujin_checkbox.isChecked():
            params = {"limit":100, "title":manga_title}
        else:
            params = {"limit":100, "title":manga_title, "excludedTags[]" : tags["Doujinshi"]}
        response = requests.get(links["search"], params=params)
        results = response.json()["results"]
        fetch_titles(results, self.searched_dict, self.searched_cache, self.title_listbox)

    def doujin_checkboxToggled(self):
        if self.doujin_checkbox.isChecked() == True:
            for x in range(self.title_listbox.count()):
                title = self.title_listbox.item(x).text()
                if self.searched_dict[title]["Doujinshi"] == "True":
                    self.title_listbox.setRowHidden(x, True)
                    self.hidden_title_rows.append(x)
        else:
            for x in self.hidden_title_rows:
                self.title_listbox.setRowHidden(x, False)

    def chapter_box_box_selectionChanged(self, item):
        if item.text() == self.last_selected_chapter:
            #to stop the code from doing useless requests to the url since some people are autistic and triple clicks
            return

        self.last_selected_chapter = item.text()

    def title_box_selectionChanged(self, item):
        if item.text() == self.last_selected_title:
            #to stop the code from doing useless requests to the url since some people are autistic and triple clicks
            return
        manga_name = item.text()
        self.last_selected_title = manga_name
        if manga_name not in self.clicked_manga_list:
            self.clicked_manga_list.append(manga_name)
            self.chapter_listbox.clear()
            t = Thread(target=fetch_chaps, args=(manga_name, self.searched_cache, self.searched_chaps, self.chapter_listbox)).start()
        else:
            self.chapter_listbox.clear()
            for chapters in self.searched_chaps[manga_name]["Chapters"]:
                self.chapter_listbox.addItem(chapters)

    def center(self):
        frame_gm = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        center_point = QApplication.desktop().screenGeometry(screen).center()
        frame_gm.moveCenter(center_point)
        self.move(frame_gm.topLeft())


App = QApplication(sys.argv)

window = Window()
sys.exit(App.exec())
