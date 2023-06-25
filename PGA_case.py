from langchain import OpenAI, PromptTemplate
from langchain.chains.question_answering import load_qa_chain
import os
from langchain.embeddings import OpenAIEmbeddings
from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate

from constants import OPENAI_API_KEY
from langchain.vectorstores import Chroma

from create_vector_db import create_vector_db


os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
prompt_template = """You are a helpful assistant that is specialized in dutch tax law. Based on the context that you get,
strictly stick with this context and give a complete and clear answer to the user in the language of the question. 
If you don't find any relevant info return I don't think I have an answer, it is very important that the answers are right.

{context}

Question: {question}
Answer in the language that the question is asked in:"""
PROMPT = PromptTemplate(
    template=prompt_template, input_variables=["context", "question"]
)
chain = load_qa_chain(OpenAI(temperature=0), chain_type="stuff", prompt=PROMPT)

question= 'Hi ik heb een woonboot waarmee ik rondvaar door Nederland en ik vroeg mij af of ik dit bij mij belastingaangifte moet optellen? '

# get a chat completion from the formatted messages

# Download embeddings from OpenAI
# embeddings = OpenAIEmbeddings()
#
# vectordb = Chroma(persist_directory='db', embedding_function=embeddings)
vectordb = create_vector_db('Belastingen_huis.docx', 'faiss')

docs = vectordb.similarity_search(question)
answer = chain.run(input_documents=docs, question=question)
print(answer)