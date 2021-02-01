import requests
import random

from typing import List
from lxml.html import fromstring


def get_rand_from_list(array: list):
    return array[random.randint(0, len(array))]


def get_proxies(max_n: int = 10) -> List[dict]:
    url = "https://free-proxy-list.net/"
    response = requests.get(url)
    parser = fromstring(response.text)
    proxies = set()
    for i in parser.xpath("//tbody/tr")[:299]:
        proxy = ":".join([i.xpath(".//td[1]/text()")[0], i.xpath(".//td[2]/text()")[0]])
        if i.xpath(".//td[7]/text()")[0] == "yes":
            proxies.add(proxy)

    return [{"http": proxy, "https": proxy} for proxy in list(proxies)[:max_n]]
