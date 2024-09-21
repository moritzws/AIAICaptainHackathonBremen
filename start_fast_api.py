from fastapi import FastAPI
from chatbot.chatbot import setup_vector_store, setup_embedding_model

app = FastAPI()


@app.get("/run-main")
def run_main():
    embedding_model = setup_embedding_model()
    vector_store = setup_vector_store(embedding_model)

    query = "wer ist scrum master?"
    results = vector_store.similarity_search(query, k=3)
    return {"results": results}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
