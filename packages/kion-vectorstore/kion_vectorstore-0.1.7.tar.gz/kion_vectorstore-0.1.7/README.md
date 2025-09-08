kion_vectorstore

License: MIT

Overview
kion_vectorstore is a Python library and GUI application for managing vector stores in PostgreSQL (with pgvector) using LangChain.
It lets you upload PDFs or .txt files, organize them into collections, perform semantic search, and query them via an OpenAI-powered chat UI.
You can also delete files or whole collections from a simple web interface.

Features
- Upload PDFs and text files
- Organize documents into named collections
- OpenAI-powered semantic search across selected collections
- Delete individual files or entire empty collections
- Use functions programmatically in Python
- Simple Flask-based web UI

Prerequisites
- Python 3.8+
- PostgreSQL installed locally or reachable on your network
- pgvector extension enabled in your database
  See: https://github.com/pgvector/pgvector

Quick Start
1) Install the package
   pip install kion-vectorstore

2) Create a .env file (once per project) using the CLI
   env-init --path "<-your folder name->" - Enter *ONLY* the name of your folder (*DO NOT ENTER A PATH*)
   # Add --force to overwrite an existing .env:
   # e.g. env-init --path "env" --force

3) Fill in your .env
   OPENAI_API_KEY=sk-...
   OPENAI_MODEL=gpt-4o-mini
   OPENAI_EMBEDDING_MODEL=text-embedding-3-small
   PGHOST=localhost
   PGUSER=postgres
   PGPASSWORD=yourpassword
   PGDATABASE=yourdb
   PGPORT=5432

4) Launch the web app
   Option A: Use the CLI
     kion-vectorstore-web

   Option B: From Python
     python -m kion_vectorstore.app

   The app will open http://127.0.0.1:5000/ in your browser.

Using the Web UI
- File Loader tab: upload .txt or .pdf files to a collection (set chunk size/overlap)
- Remove Files tab: select a collection, list files, and delete
- Chat tab: pick collections and ask questions; the assistant answers using only your documents

Programmatic Use
Initialize config once in your Python script, then use the plugin:
  from kion_vectorstore import initialize_config, PGVectorPlugin
  from langchain_openai import OpenAIEmbeddings

  initialize_config(".env")
  embeddings = OpenAIEmbeddings()  # uses OPENAI_API_KEY from env
  db = PGVectorPlugin(embedding_model=embeddings)
  print(db.list_collections())

Notes
- This package ships a .env template inside the package. The env-init CLI copies it to your project.
- Static HTML files are served from within the installed package; you do not need to copy them.

Troubleshooting
- If you see "Configuration has not been initialized", ensure your .env exists and initialize_config has been called (the web app does this automatically).
- Ensure the pgvector extension is installed in your database, and the required LangChain tables exist (they are created on first insert by langchain_community.vectorstores.PGVector).

License
MIT © 2025 Kion Consulting
