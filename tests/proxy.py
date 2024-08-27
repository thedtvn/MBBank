# this use to bypass mbbank ip block on github actions
import asyncio
import re
import time
import uuid
import random
import aiohttp

from yarl import URL

USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
EXT_BROWSER = "chrome"
PRODUCT = "cws"
CCGI_URL = "https://client.hola.org"
cache = {}

async def get_ver():
    async with aiohttp.ClientSession() as s:
        async with s.get("https://clients2.google.com/service/update2/crx",
                         params={"acceptformat": ["crx2,crx3"], "prodversion": ["113.0"],
                                 "x": ["id=gkojfkhlekighikafcpjkiklfbnlmeio&uc="]}) as r:
            response_text = await r.text()
            return re.findall("version=\"(.+?)\"", response_text)[1]


async def background_init(user_id, EXT_VER, proxy):
    if "background_init" in cache:
        return cache["background_init"]
    post_data = {
        "login": "1",
        "ver": EXT_VER,
    }
    query_string = {
        "uuid": user_id,
    }
    async with aiohttp.ClientSession(base_url=CCGI_URL, headers={"User-Agent": USER_AGENT}) as s:
        async with s.post("/client_cgi/background_init", params=query_string, data=post_data, proxy=proxy) as r:
            data = await r.json()
            cache["background_init"] = data
            return data


async def vpn_countries():
    EXT_VER = await get_ver()
    query_string = {
        "ver": EXT_VER,
    }
    async with aiohttp.ClientSession(base_url=CCGI_URL, headers={"User-Agent": USER_AGENT}) as s:
        async with s.post("/client_cgi/vpn_countries.json", params=query_string) as r:
            return await r.json()


# exclude = "exclude_host1,exclude_host2,exclude_host3"
# exclude ex = "zagent2645.hola.org,zagent2640.hola.org,zagent734.hola.org"
async def get_proxy(country: str = "us", proxy=None, exclude=None):
    EXT_VER = await get_ver()
    user_uuid = uuid.uuid4().hex
    username = f"user-uuid-{user_uuid}-is_prem-0"
    session_key = (await background_init(user_uuid, EXT_VER, proxy))["key"]
    ping_id = random.random()
    pram = {
        "country": country.lower(),
        "src_country": country.upper(),
        "limit": 3,
        "ping_id": ping_id,
        "ext_ver": EXT_VER,
        "browser": EXT_BROWSER,
        "product": PRODUCT,
        "uuid": user_uuid,
        "session_key": session_key,
        "is_premium": 0,
        "exclude": int(bool(exclude))
    }
    data = {
        "uuid": user_uuid,
        "session_key": session_key,
        "install_ts": str(time.time() * 1000),
        "install_ver": EXT_VER,
        "ping_id": str(ping_id),
        "exclude": exclude
    }
    async with aiohttp.ClientSession(base_url=CCGI_URL, headers={"User-Agent": USER_AGENT}) as s:
        async with s.post("/client_cgi/zgettunnels", params=pram, data=data, proxy=proxy) as r:
            data = await r.json()
    ip_list = [URL.build(scheme=i[1], host=i[0], port=24241, user=username, password=data["agent_key"]) for i in
               data["protocol"].items()]
    return ip_list

async def main():
    exclude = []
    while True:
        proxy = await get_proxy(country="vn", exclude=",".join(exclude))
        for i in proxy:
            try:
                async with aiohttp.ClientSession() as s:
                    async with s.get("https://online.mbbank.com.vn", proxy=i) as r:
                        print(f"http_proxy={i}")
                        break
            except aiohttp.client_exceptions.ClientProxyConnectionError:
                exclude.append(i.host)

asyncio.run(main())
