from dotenv import load_dotenv
import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
# wrapper inside langchain, so doesn't come from langchain
from langchain.llms import OpenAI
# to know what you are spending
from langchain.callbacks import get_openai_callback


def main():
    load_dotenv()
    st.set_page_config(page_title="Talk with PDF Paultje 🧠")
    st.header("Talk with PDF Paultje 🧠")

    pdf = st.file_uploader("Drop it like it's hot!!🔥🔥🔥", type="pdf")

    # extract the text
    # let you loop through the pages.
    if pdf is not None:
        pdf_reader = PdfReader(pdf)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()

        # split into chunks
        text_splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size= 1000,
            chunk_overlap= 200,
            # how to measure the length
            length_function= len
        )

        chunks = text_splitter.split_text(text)

        embeddings = OpenAIEmbeddings()

        # to search Faiss to do the semantic search in the knowledge base
        knowledge_base = FAISS.from_texts(chunks, embeddings)

        user_question = st.text_input("Ask PDF Paultje something about you pdf 🤔🤔🤔")
        if user_question:
            # creates the chunk that are most relevant for the question.
            docs = knowledge_base.similarity_search(user_question)

            # now we need to answer the question based on the chunks
            llm = OpenAI()
            chain = load_qa_chain(llm, chain_type="stuff")
            with get_openai_callback() as cb:
                response = chain.run(input_documents= docs, question= user_question)
                print(cb)

            st.write(response)

if __name__ == '__main__':
    main()