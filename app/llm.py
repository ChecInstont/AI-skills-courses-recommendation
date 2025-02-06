import os
import logging
import json
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from app.utils.prompts import skills_courses_template

load_dotenv()

# Initialize LangChain with the custom Gemini LLM
api_key = os.getenv("GOOGLE_API_KEY")
model = os.getenv("LLM_MODEL")
if not api_key:
    raise ValueError("API key for Gemini is missing.")

llm_model = ChatGoogleGenerativeAI(model=model, api_key=api_key)

async def llm_response(job_role,search_results,template=skills_courses_template,llm_model=llm_model):
    response = {}
    try:
        search_results = str(search_results)
        prompt = template.replace("{search_results}",search_results).replace("{job_role}",job_role)
        response = llm_model.invoke(prompt).content
        if isinstance(response,str) and ("{" in response or "}" in response):
          response = json.loads(response)
    except Exception as e:
        logging.exception(e)
    return response
