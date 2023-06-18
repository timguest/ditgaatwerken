from langchain import OpenAI
from langchain.chains.question_answering import load_qa_chain
import os
from langchain.embeddings import OpenAIEmbeddings
from constants import OPENAI_API_KEY
from langchain.vectorstores import Chroma

from create_vector_db import create_vector_db


os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# Download embeddings from OpenAI
# embeddings = OpenAIEmbeddings()
#
# vectordb = Chroma(persist_directory='db', embedding_function=embeddings)
chain = load_qa_chain(OpenAI(), chain_type="stuff")
vectordb = create_vector_db('belastingen.docx', 'faiss')
query = 'Zijn mijn kosten voor mijn zorgrobot aftrekbaar?'

docs = vectordb.similarity_search(query)
return_answer = chain.run(input_documents=docs, question=query + 'Geef een zo compleet en duidelijk mogelijk antwoord en geef een voorbeeld')
print(return_answer)