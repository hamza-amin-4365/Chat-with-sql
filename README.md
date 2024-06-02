# CSV to SQLite Streamlit App with Foreign Keys

## Table of Content
- [Overview](#overview)
- [Motivation](#motivation)
- [Technical Aspect](#technical-aspect)
- [Installation And Run](#installation-and-run)
- [Directory Tree](#directory-tree)
- [To Do](#to-do)
- [Bug / Feature Request](#bug---feature-request)
- [Technologies Used](#technologies-used)
- [Team](#team)
- [License](#license)
- [Credits](#credits)

## Overview
This project is a Streamlit application that allows users to upload multiple CSV files and create a SQLite database with tables corresponding to each CSV file. The application also handles foreign key relationships between the tables based on common integer columns found in the CSV files.

## Motivation
The motivation behind this project was to provide a user-friendly way to convert CSV data into a SQLite database, while also automatically handling foreign key relationships between the tables. This can be useful for data analysis, querying, and integration with other applications that work with SQLite databases.

## Technical Aspect
The application uses the following technologies and libraries:

- **Streamlit**: A Python library for building interactive web applications.
- **Pandas**: A popular data manipulation and analysis library for Python.
- **SQLite3**: A Python library for working with SQLite databases.
- **LangChain**: A framework for building applications with large language models (LLMs).
- **HuggingFace Endpoint**: An LLM provided by HuggingFace for natural language processing tasks.

The application follows these steps:

1. Allow the user to upload multiple CSV files through the Streamlit interface.
2. Read the CSV files into Pandas DataFrames.
3. Analyze the DataFrames to find potential foreign key relationships based on common integer columns.
4. Create a SQLite database and tables corresponding to each CSV file, with foreign key constraints based on the detected relationships.
5. Provide an interface for the user to ask questions about the data.
6. Use the LangChain framework and the HuggingFace LLM to generate SQL queries based on the user's questions.
7. Execute the generated SQL queries on the SQLite database and display the results to the user.

## Installation And Run
1. Clone the repository or download the source code.
2. Install the required packages by running the following command:

```bash
pip install -r requirements.txt
