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
        window_width, window_height = 900, 500
        window_startingpoint = 0
        self.setGeometry(window_startingpoint, window_startingpoint, window_width, window_height)
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
        

    def UiComponents(self):

        # creating widgets
        self.title_listbox = QListWidget(self)
        self.chapter_listbox = QListWidget(self)
        self.search_box = QLineEdit(self)
        download_button = QPushButton("Download", self)
        search_button = QPushButton("Search", self)
        #widget_list = [self.title_listbox, self.chapter_listbox,self.search_box, search_button]


        # setting widgets coordinates
        self.search_box.setGeometry(0, 0, 100, 20)
        
        search_button.setGeometry(self.search_box.geometry().x() + self.search_box.geometry().width() + 20, 0, 100,20)
        
        download_button.setGeometry(search_button.geometry().x() + search_button.geometry().width() + 20, 0, 100,20)
        
        self.title_listbox.setGeometry(0, self.search_box.geometry().x() + self.search_box.geometry().height() + 20, 150, 200)
        
        self.chapter_listbox.setGeometry(self.title_listbox.geometry().x()+self.title_listbox.geometry().width() + 20, self.search_box.geometry().x() + self.search_box.geometry().height() + 20, 150, 200)
        

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
        print("Holy cow")
        if not os.path.exists(manga_title):
            os.makedirs(manga_title)
        for x in range(len(image_list)):
            with open('{}/page {}.png'.format(manga_title, x), 'wb+') as handle:
                    image_url = base_url + image_list[x]
                    print(image_url)
                    response = requests.get(image_url, stream=True)

                    if not response.ok:
                        print (response.status_code)
                        #break

                    for block in response.iter_content(1024):
                        if not block:
                            break

                        handle.write(block)
    def clicked_download(self):

        image_list = self.searched_chaps[self.selected_title]["chapters"][self.selected_chapter]
        
       # pool = Pool()
        #pool.map(self.download_image, image_list)
        #self.download_image(image_list)
        #download_image(image_list)
        #pool = multiprocessing.Pool()
        #pool.map(self.download_image, image_list)
        t = Thread(target=self.download_image, args = (image_list, self.last_selected_title, self.current_base_url, ))
        #t.setDaemon(True)
        t.start()
        #t.join()
            


    def clicked_search(self):
        self.title_listbox.clear()
        self.searched_dict.clear()
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
            print(titles)

    def chapter_box_box_selectionChanged(self, item):
        if item.text() == self.last_selected_chapter:
            #to stop the code from doing requests to the url since some people are autistic and triple clicks
            return
        self.selected_chapter = item.text()
        self.last_selected_chapter = item.text()

        print("Selected Title: ", self.selected_title)
        print("Selected Chapter: {}".format(item.text()))

        image_list = self.searched_chaps[self.selected_title]["chapters"][self.selected_chapter]
        
        manga_id = self.searched_chaps_info[self.selected_title][self.selected_chapter]["id"]
        manga_hash = self.searched_chaps_info[self.selected_title][self.selected_chapter]["hash"]
        response = requests.get(links["get_baseurl"].format(manga_id))
        base_url = response.json()["baseUrl"]
        #still have to iterate the image list and shits
        #print("shit", self.searched_chaps_info[self.selected_title])
        #print(manga_hash, manga_id)
        self.current_base_url = "{}/data/{}/".format(base_url, manga_hash)
        print(self.current_base_url)



    def title_box_selectionChanged(self, item):
        if item.text() == self.last_selected_title:
            #to stop the code from doing requests to the url since some people are autistic and triple clicks
            return
        manga_name = item.text()
        self.selected_title = manga_name
        self.last_selected_title = manga_name
        #print("Selected item id: ", self.searched_dict[item.text()]["id"])
        if not manga_name in self.clicked_dict.keys():
            self.clicked_dict[manga_name], self.searched_chaps[manga_name],self.searched_chaps[manga_name]["chapters"]  = {}, {}, {}
            self.searched_chaps_info[manga_name] = {}

            url = links["manga_feed"].format(self.searched_dict[item.text()]["id"])
            params = {"limit":100, "order[chapter]" : "asc", "translatedLanguage[]" : "en"}
            response = requests.get(url, params=params)
            result = response.json()['results']
            tmp_list = []
            
            self.chapter_listbox.clear()
            for x in range(len(result)):
                self.searched_chaps[manga_name]["chapters"]["Chapter " + str(result[x]['data']['attributes']['chapter'])] = result[x]['data']['attributes']['data']
                #create a new key called chapter then  store manga id and hash there 
                self.searched_chaps_info[manga_name]["Chapter " + str(result[x]['data']['attributes']['chapter'])] = {}
                self.searched_chaps_info[manga_name]["Chapter " + str(result[x]['data']['attributes']['chapter'])]["id"] = result[x]['data']['id']
                self.searched_chaps_info[manga_name]["Chapter " + str(result[x]['data']['attributes']['chapter'])]["hash"] = result[x]['data']['attributes']['hash']

                self.chapter_listbox.addItem("Chapter " + str(result[x]['data']['attributes']['chapter']))
                
        else:
            self.chapter_listbox.clear()
            for chapters in self.searched_chaps[manga_name]["chapters"]:
                self.chapter_listbox.addItem(chapters)
            print("{} is already in the clicked titles\nClicked titles: {}".format(manga_name, self.clicked_dict))
          


    
    
  
# create pyqt5 app
App = QApplication(sys.argv)
  
# create the instance of our Window
window = Window()
  
# start the app
sys.exit(App.exec())
