import langchain
import pandas as pd
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.schema import Document
import requests
import os

db_url = "https://gpt.hansehart.de/api/service"

def setup_embedding_model():
    model = "text-embedding-3-large"
    embedding_model = OpenAIEmbeddings(model=model)
    return embedding_model


def setup_vector_store(embedding_model, db_url, db_token):
    database = requests.get(db_url, headers={"Authorization": f"Bearer {db_token}"}).json()
    documents = create_documents_from_db(database)

    """
    path_to_xlsx = "KI-HackathonxROSSMANN_Challenge_Ansprechpartner-Chatbot.xlsx"
    df = pd.read_excel(path_to_xlsx)
    documents = create_documents_from_df(df)
    """

    vector_store = Chroma(embedding_function=embedding_model)
    vector_store.add_documents(documents=documents)
    return vector_store


def get_personal_ids_for_query(query, vector_store):
    documents = vector_store.similarity_search(query.input_text, k=3)
    ids = [document.metadata.get("personal_id") for document in documents]
    return ids


def create_documents_from_db(database):
    documents = []
    for employee in database:
        job_description = employee.get("beschreibung") if employee.get("beschreibung") else ""
        programs = employee.get("programme") if employee.get("programme") else ""
        personal_id = employee.get("id")

        description_document = Document(page_content=job_description, metadata={"personal_id": personal_id})
        job_document = Document(page_content=programs, metadata={"personal_id": personal_id})

        documents.append(job_document)
        documents.append(description_document)
    return documents


def create_documents_from_df(df):
    documents = []
    for index, row in df.iterrows():
        document = Document(page_content=row["Beschreibung der Position und Zuständigkeiten bei Problemen"], metadata={"personal_id": index})
        documents.append(document)
        document = Document(page_content=row.fillna("")["Betreute Programme"], metadata={"personal_id": index})
        documents.append(document)
    return documents


def delete_employee_from_vector_store(personal_id, vector_store):
    document_ids = vector_store.get(where={"personal_id": personal_id}.get("ids"))
    vector_store.delete(ids=document_ids)
    return vector_store


def add_employee_to_vector_store(personal_id, vector_store):
    employee = requests.get(f"{db_url}/receive/person?id={personal_id}",
                            headers={"Authorization": f"Bearer {os.environ['DB_TOKEN']}"}).json()

    job_description = employee.get("beschreibung") if employee.get("beschreibung") else ""
    programs = employee.get("programme") if employee.get("programme") else ""
    personal_id = employee.get("id")

    description_document = Document(page_content=job_description, metadata={"personal_id": personal_id})
    job_document = Document(page_content=programs, metadata={"personal_id": personal_id})
    vector_store.add_documents(documents=description_document)
    vector_store.add_documents(documents=job_document)


def update_employee_by_personal_id(personal_id, vector_store):
    delete_employee_from_vector_store(personal_id, vector_store)
    add_employee_to_vector_store(personal_id, vector_store)
    return vector_store


def get_summary_chain(llm):
    summary_template = """
    Erstelle eine kurze Zusammenfassung, warum der Mitarbeiter bei der Anfrage helfen kann. Schreibe nur einen Satz,
    maximal zwei. Der Satz soll grammatisch korrekt und vollständig sein. Gehe eher darauf ein, was der Mitarbeiter
    macht und von welchen Themen er Kenntnisse hat. Wiederhole nicht, auch nicht umschrieben, die Anfrage.
    Nenne den Mitarbeiter nur beim Vornamen.

    Anfrage: {query}
    Vorname: {first_name}
    Nachname: {last_name}
    Job: {job}
    Beschreibung des Jobs: {job_description}

    Diese Person kann helfen, weil:
    """
    summary_prompt = PromptTemplate(
        input_variables=["query", "first_name", "last_name", "job", "job_description"],
        template=summary_template
    )
    summary_chain = LLMChain(llm=llm, prompt=summary_prompt)
    return summary_chain


def get_summary(summary_chain, query, first_name, last_name, job, job_description):
    summary = summary_chain.invoke(input={"query": query, "first_name": first_name, "last_name": last_name, "job": job,
                                          "job_description": job_description})
    return summary


def get_output_prompt_for_one_employee():
    template = """
    {first_name} {last_name}, {job}\n{summary}
    """
    output_prompt = PromptTemplate(
        input_variables=["first_name", "last_name", "job", "summary"],
        template=template,
    )
    return output_prompt


def get_output(output_prompt, first_name, last_name, job, summary):
    # Benutze die generierte Zusammenfassung im Prompt
    output = output_prompt.format(
        first_name=first_name,
        last_name=last_name,
        job=job,
        summary=summary["text"]
    )
    return output

"""
def main():
    embedding_model = setup_embedding_model(openai_key)
    vector_store = setup_vector_store(openai_key)

    query = "wer ist scrum master?"
    results = vector_store.similarity_search(query, k=3)
"""

