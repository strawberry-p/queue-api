from fastapi import FastAPI, HTTPException
import api_core as a
from pydantic import BaseModel
app = FastAPI()
WRITE_PROTECT = ("info_queue", "info_event")
class Write(BaseModel):
    key: str | None = ""
    content: str

class Key(BaseModel):
    key: str | None = ""

def dir_pop(name: str,key: str, s_q: bool):
    try:
        info = a.q_info(name)
    except IndexError:
        raise HTTPException(404)
    if key == info[5] or name == "queue":
        if s_q:
            ret = a.queue_pop(info[1]-1,name) #info[1] is length
            #equivalent to the last item in stack, LIFO
        else:
            ret = a.queue_pop(0,name)
        if ret[1] == "":
            return {"content": ret[0]}
        else:
            raise HTTPException(400,detail=ret[1])
    else:
        raise HTTPException(403)

@app.post("/api/write/{name}", status_code=201) #Created
def wq_write(name: str, key: Write):
    try:
        info = a.q_info(name)
    except IndexError: #q_info raises an IndexError if the fetchmany returns an empty array (no result)
        raise HTTPException(404)
    if (key.key == info[4] or name == "queue") and (name not in WRITE_PROTECT):
        if a.san_bool(name):
            a.queue_write(key.content, name)
        else:
            raise HTTPException(400,detail="sanitise_name")
    else:
        raise HTTPException(403)

@app.get("/api/stack_pop/{name}")
def wq_stack_pop(name: str, key: Key):
    return dir_pop(name, str(key.key), True)

@app.get("/api/pop/{name}")
def wq_pop(name: str, key: Key):
    return dir_pop(name, str(key.key), False)

class Create(BaseModel):
    write_secret: str | None = ""
    read_secret: str | None = ""

@app.put("/api/manage/{name}")
def wq_new(name: str, secrets: Create, status_code=201):
    res = a.queue_new(name,str(secrets.write_secret),str(secrets.read_secret))
    if res[1] == "invalid_name":
        raise HTTPException(status_code=400,detail="invalid name")
    elif res[1] != "":
        raise HTTPException(400)
    else:
        return res[0] #delete_secret
    
@app.delete("/api/manage/{name}",status_code=204)
def wq_delete(name: str, key: Key):
    res = a.queue_delete(name,key.key)
    if res != "":
        raise HTTPException(403,detail=res)

class Keychange:
    key: str | None = ""
    target_content: str | None = ""

@app.post("/api/change_write_key/{name}",status_code=204)
def wq_write_key_change(name: str, keychange: Keychange):
    try:
        err = a.queue_change_keys(name,keychange.key,keychange.target_content,False)
    except IndexError:
        raise HTTPException(404,detail=f"{name} not found")
    if err != "":
        if "sanit" in err:
            raise HTTPException(400,detail=err)
        else:
            raise HTTPException(403,detail=err)
    