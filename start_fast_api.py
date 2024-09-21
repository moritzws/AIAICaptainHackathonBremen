from fastapi import FastAPI
from pydantic import BaseModel
from chatbot.chatbot import (setup_vector_store, setup_embedding_model, get_output_prompt, get_summary_chain,
                             get_summary, get_output, get_personal_ids_for_query)
import os
from langchain_openai import OpenAI


class TextInput(BaseModel):
    input_text: str = "Wer kann mir beim Thema IT Security helfen?"


# Set OpenAI API key to env variable OPENAI_API_KEY
# Set your database token to env variable DB_TOKEN="database_usage_token"

app = FastAPI()
llm = OpenAI()
embedding_model = setup_embedding_model()
vector_store = setup_vector_store(embedding_model, db_token=os.environ["DB_TOKEN"])
summary_chain = get_summary_chain(llm=llm)
output_prompt = get_output_prompt()


@app.get("/")
async def root():
    return {"status": "Server is up and running"}


@app.post("/ask_bot/")
async def process_text(input_query: TextInput):
    result_text = vector_store.similarity_search(input_query.input_text, k=3)
    return {"result_text": result_text}


@app.post("/update_vector_store/")
async def update_vector_store():
    try:
        # Trigger the update process (e.g., reload documents, re-index, etc.)
        pass
        return {"status": "Vector store update triggered successfully"}
    except Exception as e:
        return {"status": "Failed to trigger update", "error": str(e)}


"""
def process_query(query, vector_store, summary_chain, output_prompt):
    personal_ids = get_personal_ids_for_query(query, vector_store)
    summary = get_summary(summary_chain, query, name, job, job_description)
    output = get_output(output_prompt, name, job, summary)
"""

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
