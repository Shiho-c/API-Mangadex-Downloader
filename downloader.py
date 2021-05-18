
# importing libraries
from PyQt5.QtWidgets import * 
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import * 
from PyQt5.QtCore import * 
from functools import partial
from api_details import links
from api_details import find_nani

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


        # showing all the widgets
        self.show()
        
    def clicked_search(self, value):
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
            self.list_widget.addItem(titles)
            


    # method for components
    def UiComponents(self):
  
        # creating a Widgets
        self.list_widget = QListWidget(self)
        self.search_box = QLineEdit(self)
        search_button = QPushButton("bruh", self)

        # setting widgets coordinates
        self.search_box.setGeometry(0, 0, 100, 20)
        search_button.setGeometry(self.search_box.geometry().x() + self.search_box.geometry().width() + 20, 0, 100,20)
        self.list_widget.setGeometry(0, self.search_box.geometry().x() + self.search_box.geometry().height() + 20, 150, 200)
        

        #setting up buttons' functions
        search_button.clicked.connect(self.clicked_search)


        # list widget items
        '''random = "https://api.mangadex.org/manga/random"
        for x in range(20):
            response = requests.get(random)        
            object = QListWidgetItem(str(response.json()['data']['attributes']['title']))
  
            list_widget.addItem(object)'''


  
        # scroll bar
        scroll_bar = QScrollBar(self)
  
        # setting style sheet to the scroll bar
        scroll_bar.setStyleSheet("background : lightgreen;")
  
        # setting vertical scroll bar to it
        self.list_widget.setVerticalScrollBar(scroll_bar)
  
  
        # getting vertical scroll bar
        value = self.list_widget.verticalScrollBar()
  
  
  
  
# create pyqt5 app
App = QApplication(sys.argv)
  
# create the instance of our Window
window = Window()
  
# start the app
sys.exit(App.exec())
