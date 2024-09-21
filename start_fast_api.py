from fastapi import FastAPI
from pydantic import BaseModel
from chatbot.chatbot import setup_vector_store, setup_embedding_model


class TextInput(BaseModel):
    input_text: str


app = FastAPI()
embedding_model = setup_embedding_model()
vector_store = setup_vector_store(embedding_model)


# Set OpenAI API key to env variable OPENAI_API_KEY

@app.get("/")
async def root():
    return {"status": "Server is up and running"}


@app.post("/ask_bot/")
async def process_text(input_query: TextInput):
    result_text = vector_store.similarity_search(input_query.input_text, k=3)
    return {"result_text": result_text}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
