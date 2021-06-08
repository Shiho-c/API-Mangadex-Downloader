import requests 
import os, errno
from threading import Thread
from api_details import links, find_nani, tags
from custom_functions import download_image


def fetch_base_url(manga_id, manga_hash):
    response = requests.get(links["get_baseurl"].format(manga_id))
    base_url = response.json()["baseUrl"]
    final_base_url = "{}/data/{}/".format(base_url, manga_hash)
    return final_base_url

def fetch_titles(results, searched_dict, listbox):
    for x in range(len(results)):
        searched_dict[results[x]["data"]["attributes"]["title"]["en"]] = {}
        searched_dict[results[x]["data"]["attributes"]["title"]["en"]]["Doujinshi"] = "False"
        searched_dict[results[x]["data"]["attributes"]["title"]["en"]]["id"] = results[x]["data"]["id"]
        
        for y in results[x]["data"]["attributes"]["tags"]:
            if tags["Doujinshi"] == y["id"]:
                searched_dict[results[x]["data"]["attributes"]["title"]["en"]]["Doujinshi"] = "True"
                break
        for b in find_nani:
            searched_dict[results[x]["data"]["attributes"]["title"]["en"]][b] = results[x]["data"]["attributes"][b]
    for title in searched_dict:
        listbox.addItem(title)


def fetch_key_hash(manga_name, searched_dict):
    url = links["manga_feed"].format(searched_dict[manga_name]["id"])
    offset = 0
    
    params = {"limit":500, "order[chapter]" : "asc", "translatedLanguage[]" : "en", "offset": offset}
    max_result = 500
    response = requests.get(url, params=params)
    result = response.json()['results']
    #while max_result == 500:
    params["offset"] = offset
    response = requests.get(url, params=params)
    result = response.json()['results']
    while max_result == 500:
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
        offset+=500
    print("Finished downloading Manga!")


def fetch_chaps(manga_name, searched_dict, searched_chaps, listbox):
    url = links["manga_feed"].format(searched_dict[manga_name]["id"])
    offset = 0
    
    params = {"limit":500, "order[chapter]" : "asc", "translatedLanguage[]" : "en", "offset": offset}
    max_result = 500
    searched_chaps[manga_name] = {}
    searched_chaps[manga_name]["Chapters"] = []
    while max_result == 500:
        params["offset"] = offset
        response = requests.get(url, params=params)
        result = response.json()['results']
        for x in range(len(result)):
            #searched_chaps[manga_name]["chapters"]["Chapter " + str(result[x]['data']['attributes']['chapter'])] = result[x]['data']['attributes']['data']
            #create a new key called chapter then  store manga id and hash there 
            searched_chaps[manga_name]["Chapters"].append("Chapter " + str(result[x]['data']['attributes']['chapter']))
            listbox.addItem("Chapter " + str(result[x]['data']['attributes']['chapter']))
        max_result = len(result)
        offset+=500


