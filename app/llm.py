import os
import logging
import json
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

# Initialize LangChain with the custom Gemini LLM
api_key = os.getenv("GOOGLE_API_KEY")
model = os.getenv("LLM_MODEL")
if not api_key:
    raise ValueError("API key for Gemini is missing.")

llm_model = ChatGoogleGenerativeAI(model=model, api_key=api_key)


template = """

Your task is extract expected json based on the given array of google search results.

* **Search Results: {search_results}

* **Job Role: {job_role}

* **Instructions:

* Provide response based on your ability.

Do not include Extra Words or symbols which is irrelevant.

* **Expected Output:

{
    "job_role": "Software Developer",
    "year": 2025,
    "trending_skills": ["Artificial Intelligence", "Machine Learning", "Software Engineering"],
    "courses": [
      {
        "course_title": "Machine Learning Specialization",
        "platform": "Coursera",
        "url": "https://www.coursera.org/specializations/machine-learning"
      },
      {
        "course_title": "Advanced Software Engineering",
        "platform": "Udemy",
        "url": "https://www.udemy.com/course/software-engineering/"
      }
    ]
  }

"""

async def llm_response(job_role,search_results,template=template,llm_model=llm_model):
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
