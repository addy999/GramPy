import time
import chromedriver_binary

from requests_html import AsyncHTMLSession
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .urls import ACCOUNT_URL, LOGIN_URL
from .parse import *
from .utils import get_rand_from_list
from itertools import cycle
from requests.exceptions import ProxyError

import nest_asyncio

nest_asyncio.apply()


def login(login_user: str, login_pass: str) -> AsyncHTMLSession:

    session = AsyncHTMLSession()
    user_agent = session.headers["User-Agent"]
    options = webdriver.ChromeOptions()
    options.headless = True
    options.add_argument(f"user-agent={user_agent}")
    driver = webdriver.Chrome(options=options)

    # Login
    driver.get(LOGIN_URL)
    init_title = driver.title
    delay = 3  # seconds
    username_input = WebDriverWait(driver, delay).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[name=username]"))
    )
    password_input = driver.find_elements_by_css_selector("input[name=password]")[0]
    username_input.send_keys(login_user)
    password_input.send_keys(login_pass)
    driver.find_elements_by_css_selector("button[type=submit]")[0].click()

    # Get media
    while driver.title == init_title:
        time.sleep(0.1)

    cookies_we_got_list = [
        {cookie["name"]: cookie["value"]} for cookie in driver.get_cookies()
    ]
    cookies_we_got = {}
    [cookies_we_got.update(parsed) for parsed in cookies_we_got_list]
    driver.quit()
    session.cookies.update(cookies_we_got)

    return session


class Gram:
    def __init__(self, login_user, login_pass, proxies=None):

        self.session = login(login_user, login_pass)
        self.proxies = proxies

    async def get_batch_posts(self, usernames: list):
        proxy_cycle = cycle(self.proxies)
        getters = [
            lambda: self.get_posts(username, next(proxy_cycle))
            for username in usernames
        ]

        return self.session.run(*getters)

    async def get_posts(self, username: str, proxy_to_use=None):

        if proxy_to_use:
            use_proxy = (
                proxy_to_use if proxy_to_use else get_rand_from_list(self.proxies)
            )
        else:
            use_proxy = None

        try:
            resp = await self.session.get(
                ACCOUNT_URL.format(username), proxies=use_proxy
            )
        except ProxyError:
            resp = await self.session.get(ACCOUNT_URL.format(username))

        data = get_data_from_resp(resp)
        return nodes_to_posts(data.graphql.user.edge_owner_to_timeline_media.edges)
