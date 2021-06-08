import requests 
from api_details import links, find_nani, tags


def fetch_base_url(chaps_dict, title, current_chap):
    manga_id = chaps_dict[title][current_chap]["id"]
    manga_hash = chaps_dict[title][current_chap]["hash"]
    response = requests.get(links["get_baseurl"].format(manga_id))
    base_url = response.json()["baseUrl"]
    final_base_url = "{}/data/{}/".format(base_url, manga_hash)
    return final_base_url

def fetch_titles(results, searched_dict, listbox):
    for x in range(len(results)):
        searched_dict[results[x]["data"]["attributes"]["title"]["en"]] = {}
        searched_dict[results[x]["data"]["attributes"]["title"]["en"]]["Doujinshi"] = "False"
        searched_dict[results[x]["data"]["attributes"]["title"]["en"]]["id"] = results[x]["data"]["id"]
        searched_dict[results[x]["data"]["attributes"]["title"]["en"]]["description"] = results[x]["data"]["attributes"]["description"]["en"]
        
        for y in results[x]["data"]["attributes"]["tags"]:
            if tags["Doujinshi"] == y["id"]:
                searched_dict[results[x]["data"]["attributes"]["title"]["en"]]["Doujinshi"] = "True"
                break
        for b in find_nani:
            searched_dict[results[x]["data"]["attributes"]["title"]["en"]][b] = results[x]["data"]["attributes"][b]
    titles = []
    for t in searched_dict:
        titles.append(t)
    return titles

def fetch_chaps(manga_name, searched_dict, searched_chaps, searched_chaps_info, listbox):
    url = links["manga_feed"].format(searched_dict[manga_name]["id"])
    offset = 0
    
    params = {"limit":500, "order[chapter]" : "asc", "translatedLanguage[]" : "en", "offset": offset}
    max_result = 500
    while max_result == 500:
        params["offset"] = offset
        response = requests.get(url, params=params)
        result = response.json()['results']
        for x in range(len(result)):
            searched_chaps[manga_name]["chapters"]["Chapter " + str(result[x]['data']['attributes']['chapter'])] = result[x]['data']['attributes']['data']
            #create a new key called chapter then  store manga id and hash there 
            searched_chaps_info[manga_name]["Chapter " + str(result[x]['data']['attributes']['chapter'])] = {}
            searched_chaps_info[manga_name]["Chapter " + str(result[x]['data']['attributes']['chapter'])]["id"] = result[x]['data']['id']
            searched_chaps_info[manga_name]["Chapter " + str(result[x]['data']['attributes']['chapter'])]["hash"] = result[x]['data']['attributes']['hash']

            listbox.addItem("Chapter " + str(result[x]['data']['attributes']['chapter']))
        max_result = len(result)
        offset+=500
