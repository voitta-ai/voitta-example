from dotenv import load_dotenv
import glob
import hashlib
import yaml
import httpx
import json
import asyncio
import numpy as np
import pandas as pd
from typing import List
from fastapi.responses import RedirectResponse, StreamingResponse
from fastapi import FastAPI, Depends, HTTPException, Header, Form
import requests
import os
import io
import uvicorn
from voitta import VoittaResponse
import sys
sys.path.append("../..")


load_dotenv("../../.env")

# Get port from environment variable, default to 50000
PORT = int(os.getenv("FILESYSTEM_SERVER_PORT", 50000))

app = FastAPI()

# Add startup event to print server information


@app.on_event("startup")
async def startup_event():
    print(f"Filesystem server running on port {PORT}")


@app.get("/__prompt__")
def prompt():
    return ("These functions fasilitate access to the server filesystem")


@app.post("/list_files",
          description="Lists files at a given location",
          openapi_extra={"x-CPM": "1.0"})
def list_files(authorization: str = Header(None),
               oauthtoken: str = Header(None),
               path: str = Form(...,
                                description="The folder to list the files in"),
               limit: int = Form(100, description="maximum number of files to return (default 100)")):

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
                          path: str = Form(...,
                                           description="Path to the file"),
                          limit: int = Form(10000, description="Maximum size to resutrn, bytes (default 10000)")):

    if os.path.exists(path):
        with open(path, "r") as f:
            data = f.read()
            return VoittaResponse(status="ok", data=data)
    else:
        return VoittaResponse(status="fail", message="file not found")


# Run the server if this file is executed directly
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=PORT)
