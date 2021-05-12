# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import requests
import json

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


def get_token(username, password):
    auth_url = "https://api.mangadex.org/auth/login"
    data = {"username": username, "password": password}
    response = requests.post(auth_url, json=data)
    print(response.json()["token"]["session"])
    print("test commit")


def retrieve_chapters(chapter_id):
    target_url = "https://api.mangadex.org/manga/{}/feed".format(chapter_id)
    params = {"limit": 100, "order[chapter]": "asc", "locales[]": "en"}
    response = requests.get(target_url, params=params)
    json_response = json.loads(response.text)
    c_number = []
    c_title = []
    c_id = []
    for x in range(len(json_response["results"])):
        c_number.append(json_response["results"][x]["data"]["attributes"]["chapter"])
        c_title.append(json_response["results"][x]["data"]["attributes"]["title"])
        c_id.append(json_response["results"][x]["data"]["id"])

    return c_number, c_title, c_id


def search(search_q):
    search_url = "https://api.mangadex.org/manga"
    params = {"title": search_q, "excludedTags[]": "b13b2a48-c720-44a9-9c77-39c9979373fb"}
    response = requests.get(search_url, params=params)
    m_ids = []
    m_titles = []
    json_response = json.loads(response.text)

    for x in range(len(json_response["results"])):
        # print(json_response["results"][x]["data"])
        m_ids.append(json_response["results"][x]["data"]["id"])
        m_titles.append(json_response["results"][x]["data"]["attributes"]["title"])

    # for title in json_response["results"][0]["data"]["attributes"]["title"]:
    # manga_title.append(title)
    return m_ids, m_titles


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    manga_ids, manga_titles, chapter_number, chapter_title, chapter_id = [], [], [], [], []
    search_input = input("Search: ")
    manga_ids, manga_titles = search(search_input)

    manga_id = input("Manga id: ")
    chapter_number, chapter_title, chapter_id = retrieve_chapters(manga_id)
    print(chapter_id[0])

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
