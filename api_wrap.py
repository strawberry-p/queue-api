from fastapi import FastAPI, HTTPException, Path
from typing import Annotated
import api_core as a
from pydantic import BaseModel
with open("description.md") as file:
    description = file.read()
app = FastAPI(title="Queue/stack API",summary="Queue/stack data structures API with remote writing and reading",description=description)
WRITE_PROTECT = ("info_queue", "info_event")
NAMETYPE = Annotated[str,Path(description="Name of the target queue table",example="queue")]
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
            return ret[0]
        else:
            raise HTTPException(400,detail=ret[1])
    else:
        raise HTTPException(403)

@app.post("/api/write/{name}", status_code=201,summary="Add an item to the target queue's table") #Created
def write(name: NAMETYPE, key: Write):
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

@app.get("/api/stack_pop/{name}",
         summary="Retrieve and pop the last item from the given queue/stack table",
         response_description="Content of the retrieved item in plaintext. \"\" means the queue is empty.")
def stack_pop(name: NAMETYPE, key: str = ""):
    return dir_pop(name, key, True)

@app.get("/api/pop/{name}",
         summary="Retrieve and pop the first item from the given queue table",
         response_description="Content of the retrieved item in plaintext. \"\" means the queue is empty.")
def pop(name: NAMETYPE, key: str = ""):
    return dir_pop(name, key, False)

@app.get("/api/length/{name}",
         summary="Returns the length of the given queue table",
         response_description="Returns the length in plaintext")
def length(name: NAMETYPE):
    if a.san_bool(name):
        try:
            return a.length_get(name)
        except IndexError:
            raise HTTPException(404,detail=f"{name} not found")
    else:
        raise HTTPException(400,detail="sanitise_name")

class CreateQueue(BaseModel):
    write_secret: str | None = ""
    read_secret: str | None = ""

@app.put("/api/manage/{name}",status_code=201,
         summary="Create a new queue table with the input write and read keys",
         description="(the read and write keys are stored in plaintext in the server. it is recommended to use random strings as the read/write keys.)",
         response_description="Returns the queue table's delete key")
def new(name: NAMETYPE, secrets: CreateQueue):
    res = a.queue_new(name,str(secrets.write_secret),str(secrets.read_secret))
    if res[1] == "invalid_name":
        raise HTTPException(status_code=400,detail="invalid name")
    elif res[1] != "":
        raise HTTPException(400)
    else:
        return res[0] #delete_secret
    
@app.delete("/api/manage/{name}",status_code=204,
            summary="Delete the given queue you have created using its corresponding delete key")
def delete(name: NAMETYPE, key: str):
    res = a.queue_delete(name,key)
    if res != "":
        raise HTTPException(403,detail=res)

class Keychange(BaseModel):
    key: str | None = ""
    target_content: str | None = ""

@app.post("/api/change_write_key/{name}",status_code=204,
          summary="Change a given queue's write key using its corresponding delete key")
def write_key_change(name: NAMETYPE, keychange: Keychange):
    try:
        err = a.queue_change_keys(name,keychange.key,keychange.target_content,False)
    except IndexError:
        raise HTTPException(404,detail=f"{name} not found")
    if err != "":
        if "sanit" in err:
            raise HTTPException(400,detail=err)
        else:
            raise HTTPException(403,detail=err)
        
@app.post("/api/change_read_key/{name}",status_code=204,
          summary="Change a given queue's write key using its corresponding delete key")
def read_key_change(name: NAMETYPE, keychange: Keychange):
    try:
        err = a.queue_change_keys(name,keychange.key,keychange.target_content,True)
    except IndexError:
        raise HTTPException(404,detail=f"{name} not found")
    if err != "":
        if "sanit" in err:
            raise HTTPException(400,detail=err)
        else:
            raise HTTPException(403,detail=err)
    