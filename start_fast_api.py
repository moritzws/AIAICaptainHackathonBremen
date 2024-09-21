from fastapi import FastAPI
from pydantic import BaseModel
from chatbot.chatbot import (setup_vector_store, setup_embedding_model, get_output_prompt_for_one_employee,
                             get_summary_chain, get_summary, get_output, get_personal_ids_for_query)
import os
from langchain_openai import OpenAI
import requests

class TextInput(BaseModel):
    input_text: str = "Wer kann mir beim Thema IT Security helfen?"


class VectorStoreUpdateInput(BaseModel):
    id: int  # d for database person that should be updated in vector store


# Set OpenAI API key to env variable OPENAI_API_KEY
# Set your database token to env variable DB_TOKEN="database_usage_token"

db_url = "https://gpt.hansehart.de/api/service"

app = FastAPI()
llm = OpenAI()
embedding_model = setup_embedding_model()
vector_store = setup_vector_store(embedding_model, f"{db_url}/receive/persons", os.environ["DB_TOKEN"])
summary_chain = get_summary_chain(llm=llm)
output_prompt = get_output_prompt_for_one_employee()


@app.get("/")
async def root():
    return {"status": "Server is up and running"}


@app.post("/ask_bot/")
async def process_text(input_query: TextInput):
    result_text = process_query(input_query, vector_store, summary_chain, output_prompt)
    return {"result_text": result_text}


@app.post("/update_vector_store/")
async def update_vector_store(update_input: VectorStoreUpdateInput):
    try:
        print(update_input.id)

        # Trigger the update process (e.g., reload documents, re-index, etc.)
        pass
        return {"status": "Vector store update triggered successfully"}
    except Exception as e:
        return {"status": "Failed to trigger update", "error": str(e)}


def process_query(query, vector_store, summary_chain, output_prompt):
    outputs = []
    personal_ids = get_personal_ids_for_query(query, vector_store)
    for personal_id in personal_ids:
        employee_data = requests.get(f"{db_url}/receive/person?id={personal_id}",
                                     headers={"Authorization": f"Bearer {os.environ['DB_TOKEN']}"}).json()
        summary = get_summary(summary_chain, query, employee_data.get("vorname"), employee_data.get("nachname"),
                              employee_data.get("position"), employee_data.get("beschreibung"))
        output = get_output(output_prompt, employee_data.get("vorname"), employee_data.get("nachname"),
                            employee_data.get("position"), summary)
        outputs.append(output)
    final_output = ("Die folgenden Mitarbeiter können dir behilflich sein: \n"
                    + "\n".join(outputs))
    return final_output


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
