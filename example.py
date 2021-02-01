from lib import Gram, get_proxies
import asyncio

login_username = ""
login_password = ""

proxies = get_proxies(10)  # Get (max) 10 proxies

print("Logging in...")
g = Gram(login_username, login_password, proxies=proxies)


async def get_posts():
    posts = await g.get_posts("google")
    print("Getting latest posts from Google...")
    print(posts[0])


loop = asyncio.get_event_loop()
loop.run_until_complete(get_posts())


async def get_batch_posts():
    batch_results = await g.get_batch_posts(
        ["gidenmedia", "android", "tiffanyleighdesign"]
    )
    print("Getting latest posts in a batch...")
    print([posts[0] for posts in batch_results])


loop.run_until_complete(get_batch_posts())
