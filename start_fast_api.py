from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from pydantic import BaseModel
from chatbot.chatbot import (setup_vector_store, setup_embedding_model, get_output_prompt_for_one_employee,
                             get_summary_chain, get_summary, get_output, get_personal_ids_for_query,
                             get_image_description)
import os
from langchain_openai import OpenAI
import requests


class TextInput(BaseModel):
    input_text: str = "Wer kann mir beim Thema IT Security helfen?"


class VectorStoreUpdateInput(BaseModel):
    id: int  # d for database person that should be updated in vector store


class ImageQuestion(BaseModel):
    additional_text: str = None


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


@app.post("/send-image/")
async def describe_image(additional_text: ImageQuestion, file: UploadFile = File(...)):
    # Ensure the uploaded file is an image
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image.")
    try:
        # Read the image file as binary
        image_data = await file.read()
        # Optionally, check the image size if needed (e.g., max size limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

        # Call OpenAI GPT-4 model with vision capabilities

    result = 'blub'
    return {"result_text": result}


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
    if personal_ids == []:
        return ("Damit kann ich dir leider nicht weiterhelfen. Stelle eine Frage im Bezug zu Personen unseres"
                + " Unternehmens.")
    for personal_id in personal_ids:
        employee_data = requests.get(f"{db_url}/receive/person?id={personal_id}",
                                     headers={"Authorization": f"Bearer {os.environ['DB_TOKEN']}"}).json()
        summary = get_summary(summary_chain, query, employee_data)
        output = get_output(output_prompt, employee_data, summary)
        outputs.append(output)
    final_output = ("Die folgenden Mitarbeiter können dir behilflich sein: \n"
                    + "\n".join(outputs))
    return final_output


def process_image_query(query, image_path, vector_store, summary_chain, output_prompt):
    with open(image_path, "rb") as image_file:
        image_data = image_file.read()
    image_description = get_image_description(image_data)

    process_query(image_description + " " + query.input_text, vector_store, summary_chain, output_prompt)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
