from fastapi import FastAPI
import api_core as a
app = FastAPI()
WRITE_PROTECT = ("info_queue", "info_event")