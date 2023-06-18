from PyPDF2 import PdfReader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter
from langchain.vectorstores import ElasticVectorSearch, Pinecone, Weaviate, FAISS, Chroma
from constants import OPENAI_API_KEY
from langchain.chains import RetrievalQA
from langchain.document_loaders import TextLoader
from langchain.llms import OpenAI

# Get your API keys from openai, you will need to create an account.
# Here is the link to get the keys: https://platform.openai.com/account/billing/overview
import os
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# Download embeddings from OpenAI
embeddings = OpenAIEmbeddings()

vectordb = Chroma(persist_directory='db', embedding_function=embeddings)
retriever = vectordb.as_retriever()
qa_chain = RetrievalQA.from_chain_type(llm=OpenAI(), chain_type='stuff', retriever=retriever, return_source_documents=False)
response = qa_chain('Is mijn bril aftrekbaar voor de Belastingdienst?')

# convert text to embedding
# this will convert the text to embedding and store it.
docsearch = FAISS.from_texts(texts, embeddings)

# question answer chain
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI

# you cna choose different models of gpt.
chain = load_qa_chain(OpenAI(), chain_type="stuff")

query = "Wanneer zijn mijn zorgkosten aftrekbaar"
# search in the embeddings, symantacaly
docs = docsearch.similarity_search(query)
hoi = chain.run(input_documents=docs, question=query)

print(hoi)