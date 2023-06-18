from langchain.document_loaders import TextLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter, CharacterTextSplitter
from PyPDF2 import PdfReader
from langchain.vectorstores import Chroma
from constants import OPENAI_API_KEY
import os
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

reader = PdfReader('test_belasting.pdf')


# read data from the file and put them into a variable called raw_text
raw_text = ''
for i, page in enumerate(reader.pages):
    text = page.extract_text()
    if text:
        raw_text += text

# text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
# texts = text_splitter.split_documents(raw_text)

text_splitter = CharacterTextSplitter(
    separator = "\n",
    chunk_size = 1000,
    chunk_overlap  = 200,
    length_function = len,
)
texts = text_splitter.split_text(raw_text)

persist_directory = 'db'

# Download embeddings from OpenAI
embeddings = OpenAIEmbeddings()

vectordb = Chroma.from_texts(texts=texts,
                                 embedding=embeddings,
                                 persist_directory=persist_directory
                                 )


vectordb.persist()