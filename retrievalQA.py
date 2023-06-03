import os
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.llms import OpenAI
from langchain.chains import RetrievalQA
from langchain.document_loaders import TextLoader
from langchain.document_loaders import DirectoryLoader
print('ok')

from constants import OPENAI_API_KEY


os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

#
loader = DirectoryLoader('./new_articles/', glob="./*.txt", loader_cls=TextLoader)

documents = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
texts = text_splitter.split_documents(documents)

persist_directory = 'db'

embedding = OpenAIEmbeddings()

# # So now we have all the embeddings of the documents in a directory
vectordb = Chroma.from_documents(documents= texts,
                                 embedding= embedding,
                                 persist_directory= persist_directory
                                 )

vectordb = Chroma(persist_directory=persist_directory,
                  embedding_function=embedding)

# Make a retriever.
retriever = vectordb.as_retriever()

docs = retriever.get_relevant_documents("How much many did Pando raise? ")

# If you only want to retrieve two docs
retriever = vectordb.as_retriever(search_kwargs={"k":2})
# you can check the search type
retriever.search_type
# you can check the search kwargs
retriever.search_kwargs

# create the chain to answer questions
qa_chain = RetrievalQA.from_chain_type(llm=OpenAI(),
                                       chain_type="stuff",
                                       retriever= retriever,
                                       return_source_documents=True)

# function to print response and get the source
def process_llm_response(llm_response):
    print(llm_response['result'])
    print('\n\nSources:')
    for source in llm_response['source_documents']:
        print(source.metadata['source'])

query = "How much money did Pando raise?"
llm_response = qa_chain(query)
process_llm_response(llm_response)




