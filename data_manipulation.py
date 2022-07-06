import csv
from email.mime import base
import pprint
import requests
import sqlite3
from bs4 import BeautifulSoup
import re
import time
from db import insert
import os
import json
import random
PATH = os.path.dirname(".\\data_\\")


def load_json(name, part=""):
    file_name = f"data{part}_{name}.json"
    p = os.path.join(PATH, file_name)
    print(p)
    with open(p) as f:
        data = json.load(f)
    mapping = {}
    for k, v in data.items():
        print(k)
        for links in v:
            print(links['link'])
            link = links['link']
            mapping[link] = get_html(link)
    # print(len(data['firebase-realtime-database']))

    with open(os.path.join(PATH, f"{name}{part}_html.json"), "w") as f:
        json.dump(mapping, f, indent=4)


classes = {
    'network': {},
    'database': {},
    'security': {},
    "os": {},
    "programming": {}
}
sites = {
    "serverfault": ['network', 'database', 'security'],
    "stackoverflow": []
}


programming_tags = "/tags?pagesize=10&order=desc&sort=popular&site=stackoverflow"

baseUri = "https://api.stackexchange.com/2.3"
main_tags = ['network', 'database', 'security', "os"]

# tags = "/tags?pagesize=10&order=desc&sort=popular&inname=network&site=superuser"


def write_to_json(name, file_number=""):
    json_file_name = f"data{file_number}_{name}.json"
    with open(os.path.join(PATH, json_file_name), "w") as js:
        json.dump(classes[name], js, indent=4)


def get_question_html(url):
    req = requests.get(url)
    return req.content


def get_html(url):
    req = requests.get(url)
    return req.text


def get_question(question_url):
    req = requests.get(question_url)

    bs = BeautifulSoup(req.content, 'html.parser')
    question = bs.find(class_="js-post-body")
    answers = bs.find_all("div", {"id": re.compile("answer-.*")})
    for answer in answers:
        vote = answer.find("div", attrs={"data-value": True})
        print(vote['data-value'])

    # for q in questions:
    #     vote = q.find(class_="js-vote-count")

    # texts = bs.find_all("div", {"id": re.compile('answer.')})
    # # for t in texts[1:2]:
    # #     print(t.find(class_='js-post-body'))
    # print(texts)


def get_questions(tag_name, site_name, pagesize=10, page_num=1):
    questions_url = f"{baseUri}/search/advanced?page={page_num}&pagesize={pagesize}&order=desc&sort=votes&tagged={tag_name}&site={site_name}"
    print("\t", questions_url)
    res = requests.get(questions_url)
    print(res.json())
    result = []
    data = res.json()['items']
    for item in data:
        tmp = {}
        for key in ['link', 'title', 'tags']:
            tmp[key] = item[key]
        result.append(tmp)

    # pprint.pprint(result)
    return result


def get_tags(list_of_dicts):
    """convert [{key1: value1}, ... , {keyN: valueN}] to [value1, ... , valueN]"""
    return [obj['name'] for obj in list_of_dicts]


def get_programming_tags(page=1):
    """"""
    programming_tags = "/tags?page={page}&pagesize=10&order=desc&sort=popular&site=stackoverflow"
    req = requests.get(f"{baseUri}{programming_tags}")
    data = req.json()['items']
    tags = get_tags(data)
    # classes['programming']['tags'] = tags
    pprint.pprint(tags)

    return tags


def get_tags_(tag_name, network_name, pagesize=10, page_num=1):
    """For every main tag(i.e 'os', 'network', ...),get most voted 10 tags that are related to it"""
    apiUrl = f"{baseUri}/tags?page={page_num}&pagesize={pagesize}&order=desc&sort=popular&inname={tag_name}&site={network_name}"
    print(apiUrl)
    res = requests.get(apiUrl)
    print(res)
    data = res.json()['items']
    tags = [obj['name'] for obj in data]

    pprint.pprint(tags)
    return tags


def os_tags():
    tags = []
    l = [{"name": "linux", "size": 5}, {"name": "windows", "size": 4},
         {"name": "operating-systems", "size": 1}]
    for item in l:
        tags_ = get_tags_(item['name'], 'superuser', item['size'],)
        tags.extend(tags_)
    print(tags)
    return tags


def fetch_related_tags(tag_name):
    pass


# get_programming_tags()

# pprint.pprint(os_tags())

# get_questions("linux", 'superuser')
# https://superuser.com/questions/164553/automatically-answer-yes-when-using-apt-get-install
# ss = get_question_html(
#     "https://superuser.com/questions/117841/when-reading-a-file-with-less-or-more-how-can-i-get-the-content-in-colors")


def all_questions_for_tag(tag_name, page=1):
    if tag_name == "os":
        tags = os_tags()
    elif tag_name in ["programming", "database"]:
        tags = get_tags_(tag_name=tag_name, network_name='stackoverflow')
    else:
        tags = get_tags_(tag_name=tag_name, network_name='superuser')
    print(tags)
    time.sleep(120)
    for tag in tags:
        print(f"tag: {tag}")
        if tag_name in ["programming", "database"]:
            qs = get_questions(tag, 'stackoverflow', page_num=page)

        else:
            qs = get_questions(tag, 'superuser', page_num=page)

        time.sleep(6)
        classes[tag_name][tag] = qs
        print(type(qs))
        for q in qs:
            question_url = q['link']
            print(question_url)

    # insert(target=class_, tags=",".join(
    #     q['tags']), link=question_url, title=q['title'], content=get_question_html(question_url))
    # if class_ == "programming":
    #     tags = get_programming_tags()


# for cls in ['database']:  # ['network', 'database', 'security']:

#     all_questions_for_tag(cls)
#     pprint.pprint(classes)

#     write_to_json(cls)
#     time.sleep(3*60)

# tags = os_tags()
# print(tags)
# r = get_questions("kali-linux", 'stackoverflow')
# print(len(r))

r = "https://stackoverflow.com/questions/2704652/monad-in-plain-english-for-the-oop-programmer-with-no-fp-background"
# get_question(r)


def fetch_htmls(tag, part):
    # fetch htmls for links in json files

    load_json(tag, part)


# tags = ["network",  "os", "programming", "security",""database""]
# for tag in tags:
#     fetch_htmls(tag)


def merge_files(tag_name, writer, part=""):

    with open(os.path.join(PATH, f"{tag_name}{part}_html.json")) as f1:
        htmls = json.load(f1)

    with open(os.path.join(PATH, f"data{part}_{tag_name}.json")) as f2:
        links = json.load(f2)

    print(len(htmls))
    print(len(links))

    for sub_tag, sub_tag_items in links.items():

        print(sub_tag)
        for item_data in sub_tag_items:
            link = item_data['link']
            title = item_data['title']
            tags = ",".join(item_data['tags'])
            print("\tLink: ", link)
            print("\tTitle: ", title)
            print("\tTags: ", tags)

            # print("htmls[link] len ", len(htmls[link]))
            bs = BeautifulSoup(htmls[link], "html.parser")
            main = bs.find("div", {"id": "mainbar"})
            # print("cutted len ", len(main))
            # print(len(main.text))

            html_content = re.sub('\s+', ' ', main.text)
            # print("without whitespaces ", len(html_content))

            writer.writerow(
                [title, link, sub_tag, tags, html_content, tag_name])


def check_htmls():
    with open(os.path.join(PATH, "network_html.json")) as f:
        d = json.load(f)
        print(d.keys())
        print(
            "faster than I can send a pixel to the screen" in d['https://superuser.com/questions/419070/transatlantic-ping-faster-than-sending-a-pixel-to-the-screen'])


# merge_files("database")
# tags = [ "os", "programming", "security", "database"]"network"
# csv_headers = ["title", "link", "sub_tag", "tags", "content", "target"]
# with open(os.path.join(PATH, "data.csv"), 'w+', encoding="UTF-8") as c:
#     writer = csv.writer(c)
#     writer.writerow(csv_headers)
#     for tag in tags:

#         merge_files(tag, writer)

if __name__ == "__main__":

    # os_tags()

    # print(all_questions_for_tag("network", page=2))
    # write_to_json("network", 2)
    # fetch_htmls("network", 2)
    tags = ["os", "programming", "security", "database"]  # "network"
    csv_headers = ["title", "link", "sub_tag", "tags", "content", "target"]
    with open(os.path.join(PATH, "data.csv"), 'a', encoding="UTF-8") as c:
        writer = csv.writer(c)
        for tag in tags:
            # writer.writerow(csv_headers)
            print(all_questions_for_tag(tag, page=2))
            time.sleep(120)
            write_to_json(tag, 2)
            time.sleep(120)
            fetch_htmls(tag, 2)
            time.sleep(120)
            merge_files(tag, writer, 2)
            time.sleep(120)
