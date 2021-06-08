from PyQt5.QtWidgets import * 
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import * 
from PyQt5.QtCore import * 
from functools import partial

from api_details import links, find_nani, tags
from api_functions import fetch_base_url, fetch_titles, fetch_chaps, fetch_key_hash
from PIL import Image
import sys
import re
import requests
import time
import os, errno
from threading import Thread
import queue
from fpdf import FPDF
manga_queue = queue.Queue()


class Window(QWidget):
  
    def __init__(self,):
        super().__init__()
  
        self.setWindowTitle("Python ")
        t = Thread(target=self.manga_queue_worker)
        t.start()
        window_width, window_height = 794, 511
        window_startingpoint = 0
        self.setGeometry(window_startingpoint, window_startingpoint, window_width, window_height)
        #self.setGeometry(window_startingpoint, window_startingpoint, window_width, window_height)
        self.UiComponents()
  
        #no idea where to put variables
        self.searched_dict = {}
        self.manga_info = {}
        self.clicked_manga_list = []
        self.tmp_data_dict = {}
        self.searched_chaps = {}
        self.searched_chaps_info = {}
        self.last_selected_title = ""
        self.last_selected_chapter = ""
        self.current_base_url = ""
        self.hidden_title_rows = []
        # showing all the widgets
        self.center()
        self.show()
        
        
    def closeEvent(self, event):
        pass


    def set_button_flat(self, button, change_image, icon_dir=None):
        button.setFlat(True)
        button.setStyleSheet("QPushButton:pressed {background-color: transparent;}")
        if change_image:
            button.setIcon(QtGui.QIcon(icon_dir))
    def UiComponents(self):

        # creating widgets
        self.title_listbox = QListWidget(self)
        self.chapter_listbox = QListWidget(self)
        self.chapter_listbox.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.search_box = QLineEdit(self)
        self.current_status = QLabel("Status: ",self )
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
  
        # setting vertical scroll bar to it
        self.title_listbox.setVerticalScrollBar(titles_scrollbar)
        self.chapter_listbox.setVerticalScrollBar(chapters_scrollbar)
  
  
        # getting vertical scroll bar
        value = self.title_listbox.verticalScrollBar()
        value2 = self.chapter_listbox.verticalScrollBar()



    def center(self):
        frameGm = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        centerPoint = QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())
        

    def manga_queue_worker(self):
        while True:
            manga_name = manga_queue.get()
            print(f'Working on {manga_name}')
            os.makedirs(os.path.join(os.getcwd(), manga_name))
            fetch_key_hash(manga_name, self.searched_dict)
            print(f'Finished {manga_name}')
            manga_queue.task_done()


    def clicked_download_manga(self):
        manga_queue.put(self.last_selected_title)
        print(self.last_selected_title, " has been added to the queue list!")
        #t = Thread(target=self.add_queue_info)
        #t.start()


    def clicked_download_chapter(self):
        pass
                    

    def clicked_search(self):
        #print(self.hidden_title_rows)
        self.hidden_title_rows.clear()
        self.title_listbox.clear()
        self.searched_dict.clear()
        self.manga_info.clear()
        manga_title = self.search_box.text()
        if self.doujin_checkbox.isChecked():
            params = {"limit":100, "title":manga_title}
        else:
            params = {"limit":100, "title":manga_title, "excludedTags[]" : tags["Doujinshi"]}
        response = requests.get(links["search"], params=params)
        results = response.json()["results"]
        fetch_titles(results, self.searched_dict, self.title_listbox)
            


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


        
        manga_id = self.searched_chaps_info[self.last_selected_title][self.last_selected_chapter]["id"]
        manga_hash = self.searched_chaps_info[self.last_selected_title][self.last_selected_chapter]["hash"]
        response = requests.get(links["get_baseurl"].format(manga_id))
        base_url = response.json()["baseUrl"]
        self.current_base_url = "{}/data/{}/".format(base_url, manga_hash)



    def title_box_selectionChanged(self, item):
        if item.text() == self.last_selected_title:
            #to stop the code from doing useless requests to the url since some people are autistic and triple clicks
            return
        manga_name = item.text()
        self.last_selected_title = manga_name
        if not manga_name in self.clicked_manga_list:
            self.clicked_manga_list.append(manga_name)
            self.chapter_listbox.clear()
            t = Thread(target=fetch_chaps, args = (manga_name, self.searched_dict, self.searched_chaps, self.chapter_listbox))
            t.start()

                
        else:
            self.chapter_listbox.clear()
            for chapters in self.searched_chaps[manga_name]["Chapters"]:
                self.chapter_listbox.addItem(chapters)
            #print("{} is already in the clicked titles\nClicked titles: {}".format(manga_name, self.clicked_dict))
          



    
  
# create pyqt5 app
App = QApplication(sys.argv)
  
# create the instance of our Window
window = Window()
  
# start the app
sys.exit(App.exec())
