import os
import shutil
import streamlit as st

from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# Configurations
CHROMA_PATH = "chroma"
DATA_PATH = "data/"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
CHUNK_SIZE = 300
CHUNK_OVERLAP = 100

def generate_data_store():
    try:
        st.info("Chargement des documents...")
        documents = load_documents()
        st.success(f"{len(documents)} documents chargés.")

        st.info("Découpage des textes...")
        chunks = split_text(documents)
        st.success(f"{len(chunks)} chunks créés.")

        st.info("Création de la base Chroma...")
        save_to_chroma(chunks)
        st.success("Base Chroma générée avec succès.")

    except Exception as e:
        st.error(f"Erreur : {e}")

def load_documents() -> list[Document]:
    loader = DirectoryLoader(DATA_PATH, glob="*.md")
    return loader.load()

def split_text(documents: list[Document]) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        add_start_index=True
    )
    return splitter.split_documents(documents)

def save_to_chroma(chunks: list[Document]):
    # Supprime l'ancienne base
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)

    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

    # Création
    db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_PATH
    )
    db.persist()
