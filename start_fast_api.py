from fastapi import FastAPI
from chatbot import (setup_vector_store, setup_embedding_model, get_output_prompt, get_summary_chain, get_summary,
                     get_output, get_personal_ids_for_query)
from api_key import api_key
import os
from langchain_openai import OpenAI

os.environ["OPENAI_API_KEY"] = api_key
app = FastAPI()
llm = OpenAI()

@app.get("/run-main")
def run_main():
    embedding_model = setup_embedding_model()
    vector_store = setup_vector_store(embedding_model)

    summary_chain = get_summary_chain(llm=llm)
    output_prompt = get_output_prompt()

    query = "wer ist scrum master?"
    results = vector_store.similarity_search(query, k=3)
    return {"results": results}

"""
def process_query(query, vector_store, summary_chain, output_prompt):
    personal_ids = get_personal_ids_for_query(query, vector_store)
    summary = get_summary(summary_chain, query, name, job, job_description)
    output = get_output(output_prompt, name, job, summary)
"""

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
