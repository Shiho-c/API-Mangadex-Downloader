import requests 
import os, errno
from os import path
from threading import Thread
from api_details import links, find_nani, tags
from custom_functions import download_image

def fetch_base_url(manga_id, manga_hash):
    response = requests.get(links["get_baseurl"].format(manga_id))
    base_url = response.json()["baseUrl"]
    final_base_url = "{}/data/{}/".format(base_url, manga_hash)
    return final_base_url

def fetch_titles(results, searched_dict, searched_cache, listbox):
    for x in range(len(results)):
        searched_dict[results[x]["data"]["attributes"]["title"]["en"]] = {}
        searched_dict[results[x]["data"]["attributes"]["title"]["en"]]["Doujinshi"] = "False"
        searched_dict[results[x]["data"]["attributes"]["title"]["en"]]["id"] = results[x]["data"]["id"]
        
        searched_cache[results[x]["data"]["attributes"]["title"]["en"]] = {}
        searched_cache[results[x]["data"]["attributes"]["title"]["en"]]["Doujinshi"] = "False"
        searched_cache[results[x]["data"]["attributes"]["title"]["en"]]["id"] = results[x]["data"]["id"]

        for y in results[x]["data"]["attributes"]["tags"]:
            if tags["Doujinshi"] == y["id"]:
                searched_dict[results[x]["data"]["attributes"]["title"]["en"]]["Doujinshi"] = "True"
                searched_cache[results[x]["data"]["attributes"]["title"]["en"]]["Doujinshi"] = "True"
                break
        for b in find_nani:
            searched_dict[results[x]["data"]["attributes"]["title"]["en"]][b] = results[x]["data"]["attributes"][b]
            searched_cache[results[x]["data"]["attributes"]["title"]["en"]][b] = results[x]["data"]["attributes"][b]
    for title in searched_dict:
        listbox.addItem(title)


def fetch_key_hash_chapter(manga_name, manga_cache, manga_chapters):
    print("Chapter dl has been triggered for ", manga_name)

    tmp_chaps = {}
    url = links["manga_feed"].format(manga_cache[manga_name]["id"])
    offset = 0
    max_result = 500
    params = {"limit": 500, "order[chapter]": "asc", "translatedLanguage[]": "en", "offset": offset}
    while max_result == 500:
        params["offset"] = offset
        response = requests.get(url, params=params)
        result = response.json()['results']
        for x in range(len(result)):
            tmp_chaps["Chapter " + str(result[x]['data']['attributes']['chapter'])] = {}
            tmp_chaps["Chapter " + str(result[x]['data']['attributes']['chapter'])]["id"] = result[x]['data']['id']
            tmp_chaps["Chapter " + str(result[x]['data']['attributes']['chapter'])]["hash"] = result[x]['data']['attributes']['hash']              
            tmp_chaps["Chapter " + str(result[x]['data']['attributes']['chapter'])]["images"] = result[x]['data']['attributes']['data']
        max_result = len(result)
        offset += 500

    for chapter in manga_chapters:
        current_chapter = chapter.text()
        print("Downloading {} {}".format(manga_name, current_chapter))
        chapter_path = os.path.join(os.getcwd(), manga_name, current_chapter)
        os.makedirs(chapter_path)

        base_url = fetch_base_url(tmp_chaps[current_chapter]["id"], tmp_chaps[current_chapter]["hash"]) + "/"

        download_image(base_url, tmp_chaps[current_chapter]["images"], chapter_path, current_chapter)


def fetch_key_hash_manga(manga_name, searched_dict):
    print("Manga dl has been triggered for ", manga_name)
    if path.exists(os.path.join(os.getcwd(), manga_name)):
        return
    
    print("Downloading manga: ", manga_name)
    os.makedirs(os.path.join(os.getcwd(), manga_name))
    url = links["manga_feed"].format(searched_dict[manga_name]["id"])
    max_result = 500
    offset = 0 
    params = {"limit": 500, "order[chapter]" : "asc", "translatedLanguage[]": "en", "offset": offset}

    while max_result == 500:
        params["offset"] = offset
        response = requests.get(url, params=params)
        result = response.json()['results']
        for x in range(len(result)):
            manga_id = result[x]['data']['id']
            manga_hash = result[x]['data']['attributes']['hash']
            manga_chapter = "Chapter " + str(result[x]['data']['attributes']['chapter'])
            chapter_directory = os.path.join(os.getcwd(), manga_name, manga_chapter)
            os.makedirs(chapter_directory)
            images = result[x]['data']['attributes']['data']
            base_url = fetch_base_url(manga_id, manga_hash) + "/"

            download_image(base_url, images, chapter_directory, manga_chapter)
            
        max_result = len(result)
        offset += 500
    print("Finished downloading manga: ", manga_name)


def fetch_chaps(manga_name, searched_dict, searched_chaps, listbox):
    url = links["manga_feed"].format(searched_dict[manga_name]["id"])
    offset = 0
    
    params = {"limit": 500, "order[chapter]" : "asc", "translatedLanguage[]": "en", "offset": offset}
    max_result = 500
    searched_chaps[manga_name] = {}
    searched_chaps[manga_name]["Chapters"] = []
    local_c_list = []
    while max_result == 500:
        params["offset"] = offset
        response = requests.get(url, params=params)
        result = response.json()['results']
        for x in range(len(result)):
            searched_chaps[manga_name]["Chapters"].append("Chapter " + str(result[x]['data']['attributes']['chapter']))

            local_c_list.append("Chapter " + str(result[x]['data']['attributes']['chapter']))
        max_result = len(result)
        offset += 500
    for a in local_c_list:
        listbox.addItem(a)
    print("isDone")


