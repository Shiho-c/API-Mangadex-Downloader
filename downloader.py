
# importing libraries
from PyQt5.QtWidgets import * 
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import * 
from PyQt5.QtCore import * 
from functools import partial
from api_details import links, find_nani, chapter_nani

import sys
import requests
import json
import time

class Window(QMainWindow):
  
    def __init__(self):
        super().__init__()
  
        # setting title
        self.setWindowTitle("Python ")
  
        # setting geometry
        self.setGeometry(100, 100, 500, 400)

        # calling method
        self.UiComponents()
  
        #no idea where to put variables
        self.searched_dict = {}
        self.clicked_dict = {}
        self.tmp_data_dict = {}
        self.searched_chaps = {}
        self.searched_chaps_ids = {}


        # showing all the widgets
        self.show()
        
    def clicked_search(self):
        params = {"limit":100, "title":self.search_box.text()}
        response = requests.get(links["search"], params=params)
        print("searching {}".format(self.search_box.text()))
        results = response.json()["results"]
        for x in range(len(results)):
            self.searched_dict[results[x]["data"]["attributes"]["title"]["en"]] = {}
            self.searched_dict[results[x]["data"]["attributes"]["title"]["en"]]["id"] = results[x]["data"]["id"]
            self.searched_dict[results[x]["data"]["attributes"]["title"]["en"]]["description"] = results[x]["data"]["attributes"]["description"]["en"]
            for b in find_nani:
                self.searched_dict[results[x]["data"]["attributes"]["title"]["en"]][b] = results[x]["data"]["attributes"][b]
        #print(self.searched_dict)
        for titles in self.searched_dict:
            self.title_listbox.addItem(titles)


    def selection_changed(self, item):
        manga_name = item.text()
        #print("Selected item id: ", self.searched_dict[item.text()]["id"])
        if not manga_name in self.clicked_dict.keys():
            print("Triggering")
            self.clicked_dict[manga_name] = {}
            self.searched_chaps[manga_name] = {}
            self.searched_chaps[manga_name]["chapters"] = {}
            
            url = links["manga_feed"].format(self.searched_dict[item.text()]["id"])
            params = {"limit":100, "order[chapter]" : "asc", "locales[]" : "en"}
            response = requests.get(url, params=params)
            result = response.json()['results']
            tmp_list = []
            self.chapter_listbox.clear()
            for x in range(len(result)):
                self.searched_chaps[manga_name]["chapters"]["Chapter " + str(result[x]['data']['attributes']['chapter'])] = result[x]['data']['attributes']['data']
                #self.searched_chaps_ids[manga_name]["chapters"]["Chapter " + str(result[x]['data']['attributes']['chapter'])] = result[x]['data']['id']
                self.chapter_listbox.addItem("Chapter " + str(result[x]['data']['attributes']['chapter']))
                #self.searched_chaps[manga_name]["chapters"]['title'] = result[x]['data']['attributes']['title']
            print(self.searched_chaps_ids)     
        else:
            self.chapter_listbox.clear()
            for chapters in self.searched_chaps[manga_name]["chapters"]:
                self.chapter_listbox.addItem(chapters)
            print("{} is already in the clicked titles\nClicked titles: {}".format(manga_name, self.clicked_dict))
          


    # method for components
    def UiComponents(self):
  
        # creating widgets
        self.title_listbox = QListWidget(self)
        self.chapter_listbox = QListWidget(self)
        self.search_box = QLineEdit(self)
        search_button = QPushButton("bruh", self)

        # setting widgets coordinates
        self.search_box.setGeometry(0, 0, 100, 20)
        search_button.setGeometry(self.search_box.geometry().x() + self.search_box.geometry().width() + 20, 0, 100,20)
        self.title_listbox.setGeometry(0, self.search_box.geometry().x() + self.search_box.geometry().height() + 20, 150, 200)
        self.chapter_listbox.setGeometry(self.title_listbox.geometry().x()+self.title_listbox.geometry().width() + 20, self.search_box.geometry().x() + self.search_box.geometry().height() + 20, 150, 200)
        

        #setting up widgets' functions
        search_button.clicked.connect(self.clicked_search)
        self.title_listbox.itemClicked.connect(self.selection_changed)
        self.chapter_listbox.itemClicked.connect(self.selection_changed)


        # list widget items
        '''random = "https://api.mangadex.org/manga/random"
        for x in range(20):
            response = requests.get(random)        
            object = QListWidgetItem(str(response.json()['data']['attributes']['title']))
  
            title_listbox.addItem(object)'''


  
        # scroll bar
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
  
  
  
  
# create pyqt5 app
App = QApplication(sys.argv)
  
# create the instance of our Window
window = Window()
  
# start the app
sys.exit(App.exec())
