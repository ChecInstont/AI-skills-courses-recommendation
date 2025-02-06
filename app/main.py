import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from pydantic import BaseModel
from fastapi import FastAPI, File, UploadFile
from fastapi.requests import Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from app.google_search import google_search_results
from app.llm import llm_response
from app.resume.extract_resume import ResumeParser

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



@app.post("/api/resume-parser")
async def upload_resume_file(file: UploadFile = File(...)):
    response = {}
    try:
        file_name = file.filename
        file = await file.read()
        resume_parser = ResumeParser(file=file,file_name=file_name)
        response = await resume_parser.parse_resume()
    except Exception as e:
        response = {"response":{"error":str(e)},"status_code":500}
    finally:
        return JSONResponse(content=response.get("response"),status_code=response.get("status_code"))

async def extract_skills_courses(job_role):
    result = {}
    try:
        current_year = datetime.now().year
        if job_role:
            query = f"trending skills for {job_role} {current_year}"
            search_results = await google_search_results(query=query)
            result = await llm_response(job_role=job_role,search_results=search_results)
    except Exception as e:
        logging.exception(e)
    return result

@app.post("/api/skill-course-extraction")
async def get_temp(request : Request):
    req_body = await request.json()
    job_role = req_body.get("job_role")
    result = None

    result = await extract_skills_courses(job_role=job_role)

    response = {"response":{"result":result}}
    return JSONResponse(content=response.get("response"),status_code=200)


@app.post("/api/skill-course-extraction/resume")
async def job_role(file: UploadFile = File(...)):
    response = {}
    try:
        file_name = file.filename
        file = await file.read()
        resume_parser = ResumeParser(file=file,file_name=file_name)
        parsed_text = resume_parser.parse_resume()
        response = get_job_role(parsed_text)
        job_role = response.get("job_role)
        result = await extract_skills_courses(job_role=job_role)
        response = {"response":result,"status_code":200}
    except Exception as e:
        response = {"response":{"error":str(e)},"status_code":500}
    finally:
        return JSONResponse(content=response.get("response"),status_code=response.get("status_code"))

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
