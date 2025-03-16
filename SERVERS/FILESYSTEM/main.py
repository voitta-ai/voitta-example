import sys
sys.path.append("../..")
from voitta import VoittaResponse

import io
import os
import requests
from fastapi import FastAPI, Depends, HTTPException, Header, Form
from fastapi.responses import RedirectResponse, StreamingResponse

from typing import List
import pandas as pd
import numpy as np
import asyncio

import json
import httpx
import yaml

import hashlib

import glob
import os

from dotenv import load_dotenv
load_dotenv("../../.env")


app = FastAPI()


@app.get("/__prompt__")
def prompt():
    return ("These functions fasilitate access to the server filesystem")


@app.post("/list_files", 
             description="Lists files at a given location",
             openapi_extra={"x-CPM": "1.0"})
def list_files(authorization: str = Header(None), 
               oauthtoken: str = Header(None),
               path: str = Form(..., description="The folder to list the files in"),
               limit:int = Form (100, description="maximum number of files to return (default 100)")):

    
    if os.path.exists(path):
        files = os.listdir(path)
        return VoittaResponse(status="ok", data=json.dumps(json.dumps(files)))
    else:
        return VoittaResponse(status="fail", message="path not found")


@app.post("/get_file", 
             description="Get the file content. This will return any file as text",
             openapi_extra={"x-CPM": "1.0"})
def query_knowledge_graph(authorization: str = Header(None), 
               oauthtoken: str = Header(None),
               path: str = Form(..., description="Path to the file"),
               limit:int = Form (10000, description="Maximum size to resutrn, bytes (default 10000)")):

    if os.path.exists(path):
        with open (path, "r") as f:
            data = f.read()
            return VoittaResponse(status="ok", data=data)
    else:
        return VoittaResponse(status="fail", message="file not found")