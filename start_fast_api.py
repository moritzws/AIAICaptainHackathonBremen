from fastapi import FastAPI
from pydantic import BaseModel
from chatbot.chatbot import (setup_vector_store, setup_embedding_model, get_output_prompt, get_summary_chain,
get_summary, get_output, get_personal_ids_for_query)
import os
from langchain_openai import OpenAI

class TextInput(BaseModel):
    input_text: str

# Set OpenAI API key to env variable OPENAI_API_KEY

app = FastAPI()
llm = OpenAI()
embedding_model = setup_embedding_model()
vector_store = setup_vector_store(embedding_model)
summary_chain = get_summary_chain(llm=llm)
output_prompt = get_output_prompt()


@app.get("/")
async def root():
    return {"status": "Server is up and running"}


@app.post("/ask_bot/")
async def process_text(input_query: TextInput):
    result_text = vector_store.similarity_search(input_query.input_text, k=3)
    return {"result_text": result_text}

"""
def process_query(query, vector_store, summary_chain, output_prompt):
    personal_ids = get_personal_ids_for_query(query, vector_store)
    summary = get_summary(summary_chain, query, name, job, job_description)
    output = get_output(output_prompt, name, job, summary)
"""

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
