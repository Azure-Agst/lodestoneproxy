#!/usr/bin/env python3

import requests
from bottle import route, response, run, redirect
from bs4 import BeautifulSoup as BS

BASE_URL = "https://na.finalfantasyxiv.com/lodestone"

def get_soup(url):
    """Gets data from URL and returns a soup"""
    data = requests.get(url)
    if data.status_code != 200:
        raise Exception(f"Failed to fetch data! ({data.status_code})")
    return BS(data.text, "html.parser")

@route("/char/<id>")
def char(id):
    """Returns character data"""

    # get character
    try:
        soup = get_soup(f"{BASE_URL}/character/{id}")
    except Exception as e:
        response.status_code = 400
        return {"error": str(e)}

    # parse name
    name = soup.find("p", class_="frame__chara__name").text

    # parse world info
    s_data = soup.find("p", class_="frame__chara__world").text.split(" ")
    server = s_data[0]
    datacenter = s_data[1][1:-1]

    # parse class/level info
    l_data = soup.find("div", class_="character__class__data").text.split(" ")[1]
    c_data = soup.find("div", class_="character__class__arms")\
        .find("div", class_="db-tooltip__item_equipment__class")
    cur_level = int(l_data)
    cur_class = c_data.text

    # parse race/clan/gender
    r_data = soup.find("p", class_="character-block__name").contents
    race = r_data[0]
    clan = r_data[2].split(" / ")[0]
    gender_unicode = r_data[2].split(" / ")[1]
    if gender_unicode == "\u2642":
        gender = "Male"
    elif gender_unicode == "\u2640":
        gender = "Female"
    else:
        gender = "Unknown"

    # parse character parameters
    attrs = {}
    tables = soup.find_all("table", class_="character__param__list")
    for t in tables:
        for row in t.find_all("tr"):
            attrs[row.th.text] = int(row.td.text)

    # parse image assets
    avatar = soup.find("div", class_="frame__chara__face").find("img")['src']
    fullbody = soup.find("a", class_="js__image_popup")['href']
    classjobicon = soup.find("div", class_="character__class_icon").find("img")['src']

    # return data
    return {
        "name": name,
        "avatar": avatar,
        "server": server,
        "datacenter": datacenter,
        "race": race,
        "clan": clan,
        "gender": gender,
        "fullbody": fullbody,
        "classjob": cur_class,
        "classjobicon": classjobicon,
        "level": cur_level,
        "attributes": attrs
    }

@route("/char/<id>/avatar")
def char_avatar(id):
    """Returns character avatar"""

    # get character
    try:
        soup = get_soup(f"{BASE_URL}/character/{id}")
    except Exception as e:
        response.status_code = 400
        return {"error": str(e)}
    
    # format and return
    avatar = soup.find("div", class_="frame__chara__face").find("img")['src']
    response.set_header("Content-Type", "image/png")
    return requests.get(avatar).content

@route("/health-check")
def health():
    return "OK"

@route("/")
def index():
    return redirect(BASE_URL)

if __name__ == "__main__":
    run(host="localhost", port=8080)