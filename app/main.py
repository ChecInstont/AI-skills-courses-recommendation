import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from app.google_search import google_search_results
from app.llm import llm_response

load_dotenv()

logging.basicConfig(level=logging.INFO)

app = FastAPI()

templates = Jinja2Templates(directory="static")

@app.get("/status")
async def get_status():
    return JSONResponse(content={"status":"Ok"},status_code=200)


@app.get("/health")
async def get_health():
    return JSONResponse(content={"health":"Ok"},status_code=200)



@app.post("/api/skill-course-extraction")
async def get_temp(request : Request):
    req_body = await request.json()
    job_role = req_body.get("job_role")
    result = None
    current_year = datetime.now().year

    try:
        if job_role:
            query = f"trending skills for {job_role} {current_year}"
            search_results = await google_search_results(query=query)
            result = await llm_response(job_role=job_role,search_results=search_results)
    except Exception as e:
        logging.exception(e)

    response = {"response":{"result":result}}
    return JSONResponse(content=response.get("response"),status_code=200)


def make_folder(folder_name):
    """creates folders in run time"""
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
        return True
    return None

@app.get("/{file_path:path}")
async def serve_static_files(file_path: str):
    file_location = os.path.join("static", file_path)
    if os.path.isfile(file_location):
        return FileResponse(file_location)
    return FileResponse(os.path.join("static", "index.html"))