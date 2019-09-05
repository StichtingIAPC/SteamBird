from typing import Union
from urllib.parse import quote

import requests
import vobject
from vobject.base import Component


def read_vcard(vcard_url) -> Union[Component, None]:
    try:
        vcard = requests.get(vcard_url).text
        return vobject.readOne(vcard)
    except:
        return None


def search_people(search_query):
    url = "https://people.utwente.nl/data/search?query={}".format(quote(search_query))
    people = requests.get(url, headers={
        'Accept': 'application/json',
        'Referer': 'https://people.utwente.nl/',
    }).json()['data']

    return people
