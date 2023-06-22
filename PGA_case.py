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
vectordb = create_vector_db('Belastingen_huis.docx', 'faiss')
query = 'Hi ik heb een woonboot waarmee ik rondvaar door Nederland en ik vroeg mij af of ik dit bij mij belastingaangifte moet optellen? '

docs = vectordb.similarity_search(query)
return_answer = chain.run(input_documents=docs, question=query + ' Geef een zo compleet en duidelijk mogelijk antwoord. Verzin geen antwoorden, zodra je de informatie niet kan vinden zeg dat dan.')
print(return_answer)