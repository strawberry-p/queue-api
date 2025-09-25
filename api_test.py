import requests as r
ADDR = "http://127.0.0.1:8000/api"
def p(content: str,name="queue",key=""):
    res = r.post(f"{ADDR}/write/{name}", json={"key":key, "content":content})
    print(f"status {res.status_code}")
    if res.status_code > 299:
        print(res.content)
        return res.headers
    else:
        return res.json()

def g(name="queue",key="",stack=False):
    if stack:
        res = r.get(f"{ADDR}/stack_pop/{name}",params={"key":key})
    else:
        res = r.get(f"{ADDR}/pop/{name}",params={"key":key})
    print(f"status {res.status_code}")
    if res.status_code > 299:
        print(res.content)
        return res.headers
    else:
        return res.json()
def length(name="queue"):
    res = r.get(f"{ADDR}/length/{name}")
    errcode = res.status_code
    print(f"status {errcode}")
    if res.status_code > 299:
        print(res.content)
        return res.headers
    else:
        return res.json()
def new_queue(name,wk="",rk=""):
    res = r.put(f"{ADDR}/manage/{name}",json={"write_secret":wk,"read_secret":rk})
    print(res)
    errcode = res.status_code
    print(f"status {errcode}")
    if res.status_code > 299:
        print(res.content)
        return res.headers
    else:
        return res.json()
def delete_queue(name, dk):
    res = r.delete(f"{ADDR}/manage/{name}",params={"key":dk})
    errcode = res.status_code
    print(f"status {errcode}")
    if errcode > 299:
        print(res.content)
        print(res.headers)
def update_key(name,dk,newkey,writeOrRead="write"):
    res = r.post(f"{ADDR}/change_{writeOrRead}_key/{name}",json={"key":dk,"target_content":newkey})
    print(res.status_code)
    print(res.content)
    if res.status_code > 299:
        print(res.content)
        return res.headers
    else:
        return res.json()