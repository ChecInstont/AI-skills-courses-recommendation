import logging
import json
import re
import os

from app.utils.prompt_template import gemini_model
from app.utils.prompts import skills_courses_template
from dotenv import load_dotenv
load_dotenv()

async def gemini_llm(input):
    response = await gemini_model(input)
    response = response["candidates"][0]["content"]["parts"][0]["text"]
    # response = gemini_chain.run(input_json)
    logging.info(f"Gemini response: {response}")
    return response


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


async def llm_model(input):
    response = ""
    try:
        current_model_name = os.getenv("CURRENT_LLM_MODEL")
        if current_model_name=="GEMINI":
            response = await gemini_llm(input=input)
            response = format_llm_response(raw_response=response)
        else:
            response = {"error":"Only GEMINI model is available"}
    except Exception as e:
        response = {"error":str(e)}
    finally:
        return response


def format_llm_response(raw_response):
    try:
        if "`" in raw_response:
            raw_response = raw_response.replace("```json\n", "").replace("```", "").strip()
        if "**Explanation:**" in raw_response:
            raw_response = raw_response.split("**Explanation:**")[0]
        raw_response = json.loads(raw_response)
    except Exception as e:
        logging.error(f"Error occured : {str(e)}")
    
    return raw_response
    
