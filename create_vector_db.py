from langchain import FAISS
from langchain.document_loaders import TextLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter, CharacterTextSplitter
from PyPDF2 import PdfReader
from langchain.vectorstores import Chroma
from constants import OPENAI_API_KEY
import os
from docx import Document as pydoc
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY


def create_vector_db(path, method):

    # read data from the file and put them into a variable called raw_text
    raw_text = ''
    if 'pdf' in path:
        reader = PdfReader(path)
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                raw_text += text
    else:
        doc = pydoc(path)
        for para in doc.paragraphs:
            raw_text += para.text + "\n"

    # text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    # texts = text_splitter.split_documents(raw_text)

    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=400,
        chunk_overlap=40,
        length_function=len
    )
    texts = text_splitter.split_text(raw_text)

    persist_directory = 'db_' + method

    # Download embeddings from OpenAI
    embeddings = OpenAIEmbeddings()

    if method == 'chroma':

        vectordb = Chroma.from_texts(texts=texts,
                                     embedding=embeddings,
                                     persist_directory=persist_directory
                                     )
        vectordb.persist()
    else:
        vectordb = FAISS.from_texts(texts, embeddings)


    return vectordb



create_vector_db('test_belasting.pdf', 'faiss')