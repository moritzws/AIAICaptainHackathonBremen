import langchain
import pandas as pd
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.schema import Document
import os

def setup_embedding_model():
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


def get_summary_chain(llm):
    summary_template = """
    Erstelle eine kurze Zusammenfassung, warum der Mitarbeiter bei der Anfrage helfen kann. Schreibe nur einen Satz, maximal zwei.
    Gehe eher darauf ein, was der Mitarbeiter macht und von welchen Themen er Kenntnisse hat. Wiederhole nicht, auch nicht umschrieben, die Anfrage.

    Anfrage: {query}
    Name: {name}
    Job: {job}
    Beschreibung des Jobs: {job_description}

    Diese Person kann helfen, weil:
    """
    summary_prompt = PromptTemplate(
        input_variables=["query", "name", "job", "job_description"],
        template=summary_template,
    )
    summary_chain = LLMChain(llm=llm, prompt=summary_prompt)
    return summary_chain


def get_summary(summary_chain, query, name, job, job_description):
    summary = summary_chain.invoke(input={"query":query, "name":name, "job":job, "job_description":job_description})
    return summary


def get_output_prompt():
    template = """
    Du kannst dich an einen der folgenden Mitarbeiter wenden: \n
    {name}, {job}\n{summary}
    """
    output_prompt = PromptTemplate(
        input_variables=["name", "job", "summary"],
        template=template,
    )
    return output_prompt


def get_output(output_prompt, name, job, summary):
    # Benutze die generierte Zusammenfassung im Prompt
    output = output_prompt.format(
        name=name,
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
