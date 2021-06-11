from PyQt5.QtWidgets import * 
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import * 
from PyQt5.QtCore import * 
from functools import partial

from api_details import links, find_nani, tags
from api_functions import fetch_base_url, fetch_titles, fetch_chaps
from PIL import Image
import sys
import re
import requests
import time
import os, errno
from threading import Thread

manga_queue = {}
class Manga():
    def __init__(self):
        super().__init__()
    


    def thread_download(self):
        t = Thread(target=self.download_image)
        t.start()

    def download_image(self):
        #if not os.path.exists(self.title):
            #os.makedirs(self.title)
        for key in manga_queue:
            for b in range(len(manga_queue[key]["Chapters"])):
                current_iterated_chapter = manga_queue[key]["Chapters"][0]
                print("Currently Downloading: {} {}".format(key, current_iterated_chapter))
                del manga_queue[key]["Chapters"][0]
                current_iterated_images = manga_queue[key][current_iterated_chapter]["image_list"]
                current_iterated_base_url = manga_queue[key][current_iterated_chapter]["base_url"]
                
                try:
                    os.makedirs(key)
                except OSError as e:
                    if e.errno != errno.EEXIST:
                        raise
                if not os.path.exists(current_iterated_chapter):
                    current_chapdir = os.path.join(os.getcwd(), key, current_iterated_chapter)
                    try:
                        os.makedirs(current_chapdir)
                    except OSError as e:
                        if e.errno != errno.EEXIST:
                            raise
                    for x in range(len(current_iterated_images)):
                        with open('{}/{}.{}'.format(current_chapdir, x, current_iterated_images[x][-3:]), 'wb+') as handle:
                                image_url = current_iterated_base_url + current_iterated_images[x]
                                response = requests.get(image_url, stream=True)


                                if not response.ok:
                                    pass

                                for block in response.iter_content(1024):
                                    if not block:
                                        break

                                    handle.write(block)
            
                print("Converting {} {} to pdf file".format(key, current_iterated_chapter))
                img_name_list = os.listdir(current_chapdir)
                img_name_list.sort(key=lambda f: int(re.sub('\D', '', f)))
                img_list = []
                im1 = Image.new("RGB", (800, 1280), (255, 255, 255))
                for x in img_name_list:
                    im2 = Image.open(current_chapdir + "/" + x)
                    object = im2.convert('RGB')
                    img_list.append(object)
                    im2.close()
                    os.remove(current_chapdir + "/" + x)
                im1.save(current_chapdir + "/" + current_iterated_chapter + ".pdf", "PDF" ,resolution=100.0, save_all=True, append_images=img_list)
                im1.close()
                print("{} {} has been converted to pdf file".format(key, current_iterated_chapter))
        
class Window(QWidget):
  
    def __init__(self,):
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
        self.last_selected_title = ""
        self.last_selected_chapter = ""
        self.current_base_url = ""
        self.hidden_title_rows = []
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
        self.chapter_listbox.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.search_box = QLineEdit(self)
        self.current_status = QLabel("Status: ",self )
        self.main_layout = QGridLayout(self)

        
        download_button = QPushButton("Download", self)
        search_button = QPushButton("Search", self)
        manga_header = QLabel("Manga Titles: ",self)
        chapter_header = QLabel("Chapters: ",self )
        self.doujin_checkbox = QCheckBox("Doujinshi", self)
        self.chapter_numbers = QLineEdit("Input the chapters here ex: 20-50", self)
        
        
        self.set_button_flat(search_button, True, "components/search.png")
        self.set_button_flat(download_button, True, "components/download.png")
        #widget_list = [self.title_listbox, self.chapter_listbox,self.search_box, search_button]



        self.main_layout.addWidget(self.current_status,0, 0)
        # second row. We use a QHBoxlayout to layout the QLineEdit and the two buttons
        hlayout = QHBoxLayout(self)
        hlayout.setContentsMargins(0,0,0,0)
        hlayout.addWidget(self.search_box)
        hlayout.addWidget(search_button)
        hlayout.addWidget(download_button)
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
        #setting up widgets' functions / signalss
        search_button.clicked.connect(self.clicked_search)
        download_button.clicked.connect(self.clicked_download)
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
        
    
    def clicked_download(self):
        
        for s_chapter in self.chapter_listbox.selectedItems():
            current_chapter = s_chapter.text()
            manga_queue[self.last_selected_title]["Chapters"].append(current_chapter)
            manga_queue[self.last_selected_title][current_chapter] = {}
            manga_queue[self.last_selected_title][current_chapter]["base_url"] = fetch_base_url(self.searched_chaps_info, self.last_selected_title, current_chapter)
            manga_queue[self.last_selected_title][current_chapter]["image_list"] = self.searched_chaps[self.last_selected_title]["chapters"][current_chapter]
        m = Manga()
        m.thread_download()
            #base_url = fetch_base_url(self.searched_chaps_info, self.last_selected_title, current_chapter)

            #image_list = self.searched_chaps[self.last_selected_title]["chapters"][current_chapter]
            #m = Manga(image_list, self.last_selected_title, current_chapter, base_url)
            #m.thread_download()
            
            


    def clicked_search(self):
        #print(self.hidden_title_rows)
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
        titles = fetch_titles(results, self.searched_dict, self.title_listbox)
        for title in titles:
            manga_queue[title] = {}
            manga_queue[title]["Chapters"] = []
            self.title_listbox.addItem(title)


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
            #to stop the code from doing requests to the url since some people are autistic and triple clicks
            return
        self.last_selected_chapter = item.text()


        
        manga_id = self.searched_chaps_info[self.last_selected_title][self.last_selected_chapter]["id"]
        manga_hash = self.searched_chaps_info[self.last_selected_title][self.last_selected_chapter]["hash"]
        response = requests.get(links["get_baseurl"].format(manga_id))
        base_url = response.json()["baseUrl"]
        self.current_base_url = "{}/data/{}/".format(base_url, manga_hash)



    def title_box_selectionChanged(self, item):
        if item.text() == self.last_selected_title:
            #to stop the code from doing requests to the url since some people are autistic and triple clicks
            return
        manga_name = item.text()
        self.last_selected_title = manga_name
        if not manga_name in self.clicked_dict.keys():
            self.clicked_dict[manga_name], self.searched_chaps[manga_name],self.searched_chaps[manga_name]["chapters"]  = {}, {}, {}
            self.searched_chaps_info[manga_name] = {}
            self.chapter_listbox.clear()
            t = Thread(target=fetch_chaps, args = (manga_name, self.searched_dict, self.searched_chaps, self.searched_chaps_info, self.chapter_listbox))
            t.start()

                
        else:
            self.chapter_listbox.clear()
            for chapters in self.searched_chaps[manga_name]["chapters"]:
                self.chapter_listbox.addItem(chapters)
            #print("{} is already in the clicked titles\nClicked titles: {}".format(manga_name, self.clicked_dict))
          



    
  
# create pyqt5 app
App = QApplication(sys.argv)
  
# create the instance of our Window
window = Window()
  
# start the app
sys.exit(App.exec())
