import os
import re
import sqlite3
import pandas as pd
import pickle
from typing import Tuple, List
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from dotenv import load_dotenv
load_dotenv()
VECTORSTORE_PATH = "./faiss_index"
SQLITE_PATH = "./argo_cleaned.db"
TABLE_NAME = "profiles"
embed = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = FAISS.load_local(VECTORSTORE_PATH, embed, allow_dangerous_deserialization=True)
from SCHEMA import DB_SCHEMA, PROMPT
db_schema = DB_SCHEMA.format(TABLE_NAME=TABLE_NAME)
def retrieve_context(query: str, k: int = 6):
    docs = vectorstore.similarity_search(query, k=k)
    contexts = [d.page_content for d in docs]
    return contexts, docs
def get_sql_query(contexts: List[str], user_question: str) -> str:
    system_message = SystemMessage(content="You are an expert translator from English queries to SQL for the ARGO profiles database. You are given the database schema and some context information from the database. Use this information to generate accurate SQL queries.")
    human_template = PROMPT.format(table=TABLE_NAME, db_schema=db_schema, context="\n".join(contexts), question=user_question)
    human_message = HumanMessage(content=human_template)
    chatbot = ChatOpenAI(model_name="gpt-4o-mini",temperature=0.0)
    result = chatbot.invoke([system_message, human_message])
    sql_text = result.content.strip()
    return sql_text
def get_data_from_sql(sql_query):
    conn = sqlite3.connect(SQLITE_PATH)
    try:
        df = pd.read_sql_query(sql_query, conn)
    finally:
        conn.close()
    return df   
def get_conversational_ai_output(context,user_question):
    prompt = ChatPromptTemplate.from_template("""
    You are an expert assistant helping with Argo float oceanographic data.
    You have two tasks depending on the user’s question:

    1. **Descriptive / factual questions** (e.g. "profiles in Jan 2025", "salinity at 13N 84E"):
       - Use the provided CONTEXT only.
       - Answer in natural language, summarizing float ID, date, lat/lon, depth, temperature, salinity.
       - Never invent values that are not present in the context.

    2. **Statistical / aggregation questions** (e.g. containing terms like avg, average, max, min, count, trend, comparison):
       - Do NOT attempt to calculate values yourself.
       - Instead, return exactly this message:
         "This requires numerical aggregation. Please see the generated SQL query and result table/plot below for details."

    ---

    User Question:
    {user_question}

    Context Profiles:
    {context}

    Remember:
    - Always ground answers in the context.
    - If unsure, politely say you cannot answer with the given data.
    - Do NOT hallucinate SQL queries here — that will be handled separately.
    """)
    messages = prompt.format_messages(user_question=user_question, context="\n".join(context))
    chatbot_ca = ChatOpenAI(model_name="gpt-4", temperature=0.2)
    results = chatbot_ca.invoke(messages)
    return results.content
def main(user_question = None):
    if user_question:
        user_question = user_question
    else:
        user_question = input("Enter the Question: ")
    # user_question  = "Show me salinity and temprature profiles from floats near 80 east and 90 east in january 2025"
    contexts, docs = retrieve_context(user_question, k=10)
    ca_output = get_conversational_ai_output(contexts,user_question)
    sql_query = get_sql_query(contexts, user_question)
    print("Generated SQL Query: ",sql_query)
    df = get_data_from_sql(sql_query)
    return df, ca_output