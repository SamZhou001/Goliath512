import hashlib
import asyncio

def digest(string):
    if not isinstance(string, bytes):
        string = str(string).encode('utf8')
    return hashlib.sha1(string).digest()

async def gather_dict(dic):
    cors = list(dic.values())
    results = await asyncio.gather(*cors)
    return dict(zip(dic.keys(), results))