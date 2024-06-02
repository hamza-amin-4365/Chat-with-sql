import streamlit as st
import pandas as pd
import sqlite3
import os
import logging
from langchain_community.utilities import SQLDatabase
from langchain_community.llms import HuggingFaceEndpoint
from langchain_experimental.sql.base import SQLDatabaseChain
from langchain.chains import create_sql_query_chain
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from operator import itemgetter
from dotenv import load_dotenv

load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# Create or connect to a SQLite database
conn = sqlite3.connect('testdb.db')
c = conn.cursor()

def create_table_with_fk(table_name, df, foreign_keys):
    try:
        columns = ', '.join([f'"{column}" TEXT' if df[column].dtype == 'object' else f'"{column}" {df[column].dtype}' for column in df.columns])
        
        foreign_key_constraints = ', '.join([f'FOREIGN KEY ("{fk}") REFERENCES "{ref_table}" ("{fk}")' for fk, ref_table in foreign_keys.items()])
        create_table_sql = f'CREATE TABLE "{table_name}" ({columns}{", " + foreign_key_constraints if foreign_key_constraints else ""})'

        c.execute(create_table_sql)
        conn.commit()
        logger.info(f"Table {table_name} created in the database with foreign keys!")
        df.to_sql(table_name, conn, if_exists='append', index=False, method='multi')
    except Exception as e:
        logger.error(f"Error creating table {table_name}: {e}")

# Function to find potential foreign keys
def find_potential_foreign_keys(df_list, uploaded_files):
    foreign_keys = {}
    for i, df1 in enumerate(df_list):
        for j, df2 in enumerate(df_list):
            if i != j:
                common_columns = set(df1.columns).intersection(df2.columns)
                for column in common_columns:
                    if df1[column].dtype == 'int64' and df2[column].dtype == 'int64':
                        foreign_keys[column] = os.path.splitext(uploaded_files[j].name)[0]
    return foreign_keys

# Streamlit app
def main():
    st.title('CSV to SQLite Streamlit App with Foreign Keys')
    
    uploaded_files = st.file_uploader("Choose CSV files", accept_multiple_files=True)
    if uploaded_files:
        if len(uploaded_files) > 5:
            st.error("You can upload no more than 5 CSV files.")
        else:
            df_list = [pd.read_csv(uploaded_file) for uploaded_file in uploaded_files]
            foreign_keys = find_potential_foreign_keys(df_list, uploaded_files)
            for uploaded_file, df in zip(uploaded_files, df_list):
                table_name = os.path.splitext(uploaded_file.name)[0]
                create_table_with_fk(table_name, df, foreign_keys)
            st.success("Database created successfully!")

    # Language model setup
    api_key = os.getenv("huggingfacehub_api_token")
    llm = HuggingFaceEndpoint(
    huggingfacehub_api_token=api_key,
    repo_id = "mistralai/Mistral-7B-Instruct-v0.2",
    temperature=0.5,
    model_kwargs={"max_length": 20}
    )

    # Connect to the new database
    db = SQLDatabase.from_uri("sqlite:///testdb.db", sample_rows_in_table_info=3)

    prompt_template = '''
        Given an input question, first create a syntactically correct SQLite query to run, then look at the results of the query and return the answer to the input question.
        Unless the user specifies in the question a specific number of examples to obtain, query for at most 10 results using the LIMIT clause as per SQLite. You can order the results to return the most informative data in the database.
        Never query for all columns from a table. You must query only the columns that are needed to answer the question. Wrap each column name in double quotes (") to denote them as delimited identifiers.
        Pay attention to use only the column names you can see in the tables below. Be careful to not query for columns that do not exist. Also, pay attention to which column is in which table.
        Pay attention to user question, think like the user is dumb but you are not if the user do not enters specific details about the question it is your duty to generate syntactically correct query and do not through errors you get from database instead simply say please provide more details about the question you asked.
        Pay attention to use date('now') function to get the current date, if the question involves "today".

        Question: Question here
        SQLQuery: SQL Query to run
        SQLResult: Result of the SQLQuery
        Answer: Final answer here

        Only use the following tables:
        {table_info}

        Question: {input}
        '''
    PROMPT = PromptTemplate.from_template(prompt_template, variables=['input'])

    sql_db_chain = SQLDatabaseChain.from_llm(llm=llm, db=db, verbose=True, prompt=PROMPT)
    st.subheader("Ask Questions about the Data")
    user_question = st.text_input("Enter your question:")
    if user_question:
        try:
            logger.info(f"User question: {user_question}")
            response = sql_db_chain.invoke(user_question)
            answer = response['result']
            st.write(answer)
        except Exception as e:
            st.error(f"Error processing the question: {e}")


if __name__ == "__main__":
    main()
