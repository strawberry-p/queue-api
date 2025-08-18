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
    if key.key == info[5]:
        if s_q:
            res = a.queue_pop(info[1]-1,name) #info[1] is length
            #equivalent to the last item in stack, LIFO
        else:
            res = a.queue_pop(0,name)
        return {"content": res}
    else:
        raise HTTPException(403)

@app.post("/api/write/{name}", status_code=201) #Created
def wq_write(name: str, key: Write):
    try:
        info = a.q_info(name)
    except IndexError: #q_info raises an IndexError if the fetchmany returns an empty array (no result)
        raise HTTPException(404)
    if key.key == info[4]:
        a.queue_write(key.content, name)
    else:
        raise HTTPException(403)

@app.get("/api/stack_pop/{name}")
def wq_stack_pop(name: str, key: Key):
    return dir_pop(name, key.key, True)

@app.get("/api/pop/{name}")
def wq_pop(name: str, key: Key):
    return dir_pop(name, key.key, False)