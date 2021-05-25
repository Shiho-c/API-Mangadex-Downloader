from PyQt5.QtWidgets import * 
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import * 
from PyQt5.QtCore import * 
from functools import partial
from api_details import links, find_nani

import sys
import requests
import json
import time
import os
from threading import Thread

class Window(QMainWindow):
  
    def __init__(self):
        super().__init__()
  
        self.setWindowTitle("Python ")
        window_width, window_height = 794, 511
        window_startingpoint = 0
        self.setFixedSize(window_width, window_height)
        #self.setGeometry(window_startingpoint, window_startingpoint, window_width, window_height)
        self.UiComponents()
  
        #no idea where to put variables
        self.searched_dict = {}
        self.clicked_dict = {}
        self.tmp_data_dict = {}
        self.searched_chaps = {}
        self.searched_chaps_info = {}
        self.selected_title = ""
        self.selected_chapter = ""
        self.last_selected_title = ""
        self.last_selected_chapter = ""
        self.current_base_url = ""

        # showing all the widgets
        self.center()
        self.show()
        
    def set_button_flat(self, button, change_image, icon_dir=None):
        button.setFlat(True)
        button.setStyleSheet("QPushButton:pressed {background-color: transparent;}")
        if change_image:
            button.setIcon(QtGui.QIcon(icon_dir))
    def UiComponents(self):

        # creating widgets
        self.title_listbox = QListWidget(self)
        self.chapter_listbox = QListWidget(self)
        self.search_box = QLineEdit(self)
        self.current_status = QLabel("Status: ",self )


        download_button = QPushButton("Download", self)
        search_button = QPushButton("Search", self)
        manga_header = QLabel("Manga Titles: ",self)
        chapter_header = QLabel("Chapters: ",self )
        doujinshi_check = QCheckBox("Doujinshi", self)
        self.set_button_flat(search_button, True, "components/search.png")
        self.set_button_flat(download_button, True, "components/download.png")
        #widget_list = [self.title_listbox, self.chapter_listbox,self.search_box, search_button]

        #gotta do something about this shitty longass part but maybe next time
        self.search_box.setGeometry(10, 21, 113, 20)
        self.current_status.setGeometry(10, 1, 161, 16)
        self.title_listbox.setGeometry(10, 75, 231, 371)
        self.chapter_listbox.setGeometry(250, 75, 231, 371)
        search_button.setGeometry(108, 18, 91, 31)
        download_button.setGeometry(250, 23, 72, 23)
        manga_header.setGeometry(10, 40, 141, 31)
        chapter_header.setGeometry(250, 50, 151, 21)
        doujinshi_check.setGeometry(10, 450, 151, 17)
        manga_header.setFont(QFont("Yu Gothic UI Light", 16))
        chapter_header.setFont(QFont("Yu Gothic UI Light", 16))
        #setting up widgets' functions
        search_button.clicked.connect(self.clicked_search)
        download_button.clicked.connect(self.clicked_download)
        self.title_listbox.itemClicked.connect(self.title_box_selectionChanged)
        self.chapter_listbox.itemClicked.connect(self.chapter_box_box_selectionChanged)


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

    def download_image(self, image_list, manga_title, base_url):
        print("Holy cow test")
        if not os.path.exists(manga_title):
            os.makedirs(manga_title)
        for x in range(len(image_list)):
            with open('{}/page {}.png'.format(manga_title, x), 'wb+') as handle:
                    image_url = base_url + image_list[x]
                    print(image_url)
                    response = requests.get(image_url, stream=True)

                    if not response.ok:
                        print (response.text)
                        #break

                    for block in response.iter_content(1024):
                        if not block:
                            break

                        handle.write(block)
    def clicked_download(self):

        image_list = self.searched_chaps[self.selected_title]["chapters"][self.selected_chapter]
        
        t = Thread(target=self.download_image, args = (image_list, self.last_selected_title, self.current_base_url, ))
        t.start()
            


    def clicked_search(self):
        manga_title = self.search_box.text()
        self.title_listbox.clear()
        self.searched_dict.clear()
        params = {"limit":100, "title":manga_title}
        response = requests.get(links["search"], params=params)
        results = response.json()["results"]
        self.fetch_titles(results)


    def chapter_box_box_selectionChanged(self, item):
        if item.text() == self.last_selected_chapter:
            #to stop the code from doing requests to the url since some people are autistic and triple clicks
            return
        self.selected_chapter = item.text()
        self.last_selected_chapter = item.text()


        image_list = self.searched_chaps[self.selected_title]["chapters"][self.selected_chapter]
        
        manga_id = self.searched_chaps_info[self.selected_title][self.selected_chapter]["id"]
        manga_hash = self.searched_chaps_info[self.selected_title][self.selected_chapter]["hash"]
        response = requests.get(links["get_baseurl"].format(manga_id))
        base_url = response.json()["baseUrl"]
        self.current_base_url = "{}/data/{}/".format(base_url, manga_hash)
        print(self.current_base_url)



    def title_box_selectionChanged(self, item):
        if item.text() == self.last_selected_title:
            #to stop the code from doing requests to the url since some people are autistic and triple clicks
            return
        manga_name = item.text()
        self.selected_title = manga_name
        self.last_selected_title = manga_name
        if not manga_name in self.clicked_dict.keys():
            self.clicked_dict[manga_name], self.searched_chaps[manga_name],self.searched_chaps[manga_name]["chapters"]  = {}, {}, {}
            self.searched_chaps_info[manga_name] = {}
            self.chapter_listbox.clear()
            t = Thread(target=self.fetch_chapters, args = (manga_name,))
            t.start()

                
        else:
            self.chapter_listbox.clear()
            for chapters in self.searched_chaps[manga_name]["chapters"]:
                self.chapter_listbox.addItem(chapters)
            #print("{} is already in the clicked titles\nClicked titles: {}".format(manga_name, self.clicked_dict))
          

    def fetch_chapters(self, manga_name):
        url = links["manga_feed"].format(self.searched_dict[manga_name]["id"])
        offset = 0
        params = {"limit":500, "order[chapter]" : "asc", "translatedLanguage[]" : "en", "offset": offset}
        max_result = 500
        while max_result == 500:
            params["offset"] = offset
            response = requests.get(url, params=params)
            result = response.json()['results']
            for x in range(len(result)):
                self.searched_chaps[manga_name]["chapters"]["Chapter " + str(result[x]['data']['attributes']['chapter'])] = result[x]['data']['attributes']['data']
                #create a new key called chapter then  store manga id and hash there 
                self.searched_chaps_info[manga_name]["Chapter " + str(result[x]['data']['attributes']['chapter'])] = {}
                self.searched_chaps_info[manga_name]["Chapter " + str(result[x]['data']['attributes']['chapter'])]["id"] = result[x]['data']['id']
                self.searched_chaps_info[manga_name]["Chapter " + str(result[x]['data']['attributes']['chapter'])]["hash"] = result[x]['data']['attributes']['hash']

                self.chapter_listbox.addItem("Chapter " + str(result[x]['data']['attributes']['chapter']))
            max_result = len(result)
            offset+=500

    def fetch_titles(self, results):
        for x in range(len(results)):
            self.searched_dict[results[x]["data"]["attributes"]["title"]["en"]] = {}
            self.searched_dict[results[x]["data"]["attributes"]["title"]["en"]]["id"] = results[x]["data"]["id"]
            self.searched_dict[results[x]["data"]["attributes"]["title"]["en"]]["description"] = results[x]["data"]["attributes"]["description"]["en"]
            for b in find_nani:
                self.searched_dict[results[x]["data"]["attributes"]["title"]["en"]][b] = results[x]["data"]["attributes"][b]
        for titles in self.searched_dict:
            self.title_listbox.addItem(titles)
            print(titles)
    
  
# create pyqt5 app
App = QApplication(sys.argv)
  
# create the instance of our Window
window = Window()
  
# start the app
sys.exit(App.exec())
