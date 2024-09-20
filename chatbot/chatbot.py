import langchain
import pandas as pd
from langchain.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.schema import Document
import os

def setup_embedding_model(key):
    os.environ["OPENAI_API_KEY"] = api_key
    model = "text-embedding-3-small"
    embedding_model = OpenAIEmbeddings(model=model)
    return embedding_model


def setup_vector_store(embedding_model):
    path_to_xlsx = "/Users/annka/Downloads/KI-HackathonxROSSMANN_Challenge_Ansprechpartner-Chatbot.xlsx"
    df = pd.read_excel(path_to_xlsx)
    documents = create_documents(df)
    vector_store = Chroma(embedding_function=embedding_model)
    vector_store.add_documents(documents=documents)
    return vector_store


def get_job_description_for_query(query, vector_store):
    results = vector_store.similarity_search(query, k=3)
    return results


def create_documents(df):
    documents = []
    personal_ids = []
    for index, row in df.iterrows():
        document = Document(page_content=row["Beschreibung der Position und Zuständigkeiten bei Problemen"], metadata={"name":row["Name"], "personal_id": index})
        documents.append(document)
        document = Document(page_content=row.fillna("")["Betreute Programme"], metadata={"name": row["Name"], "personal_id": index})
        documents.append(document)
    return documents


def delete_employee_by_personal_id(personal_id, vector_store):
    document_ids = vector_store.get(where={"personal_id": personal_id}.get("ids"))
    vector_store.delete(ids=document_ids)
    return vector_store


def update_employee_by_personal_id(personal_id, vector_store):
    document_ids = vector_store.get(where={"personal_id": personal_id}.get("ids"))
    documents = []
    vector_store.update_documents(ids=document_ids, documents=documents)
    return vector_store


def main():
    embedding_model = setup_embedding_model(openai_key)
    vector_store = setup_vector_store(openai_key)

    query = "wer ist scrum master?"
    results = vector_store.similarity_search(query, k=3)


