import requests as r
ADDR = "http://127.0.0.1:8000/api"
def p(content: str,name="queue",key=""):
    res = r.post(f"{ADDR}/write/{name}", json={"key":key, "content":content})
    return res.json()

def g(name="queue",key="",stack=False):
    if stack:
        res = r.get(f"{ADDR}/stack_pop/{name}",json={"key":key})
    else:
        res = r.get(f"{ADDR}/pop/{name}",json={"key":key})
    jres = res.json()
    return jres
def length(name="queue"):
    res = r.get(f"{ADDR}/length/{name}")
    jres = res.json()
    return jres
def new_queue(name,wk="",rk=""):
    res = r.put(f"{ADDR}/manage/{name}",json={"write_secret":wk,"read_secret":rk})
    print(res)
    return res.json()
def delete_queue(name, dk):
    res = r.delete(f"{ADDR}/manage/{name}",json={"key":dk})
def update_key(name,dk,newkey,writeOrRead="write"):
    res = r.post(f"{ADDR}/change_{writeOrRead}_key/{name}",json={"key":dk,"target_content":newkey})
    print(res.status_code)
    print(res.content)
    return res.json()