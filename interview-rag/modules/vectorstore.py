import os
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
from typing import List
from dotenv import load_dotenv

# Initialize embeddings and splitter
load_dotenv()

EMB = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
SPLITTER = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
INDEX_PATH = os.path.join("data", "faiss_index")

system_prompt = "You are a user researcher. You have access to uploaded transcripts of user interviews. You are given a question and you need to answer it based on the transcripts. Reference specific quotes or data points from the transcripts to support your answer. If you don't have enough information, say so."

def load_or_init():
    if os.path.isdir(INDEX_PATH):
        return FAISS.load_local(INDEX_PATH, EMB)
    # Create a dummy document to initialize the index
    dummy_doc = Document(page_content="dummy", metadata={"transcript_id": "init"})
    return FAISS.from_documents([dummy_doc], EMB)


def persist(db):
    db.save_local(INDEX_PATH)


def add_transcript_chunks(db, transcript_id: str, text: str):
    texts = SPLITTER.split_text(text)
    docs: List[Document] = []
    for i, chunk in enumerate(texts):
        docs.append(Document(
            page_content=chunk,
            metadata={"transcript_id": transcript_id, "chunk": i}
        ))
    db.add_documents(docs)
    persist(db)


def run_llm_chain(docs: List[Document], question: str, system_prompt: str = system_prompt) -> str:
    from langchain.chat_models import ChatLlamaCpp
    from langchain.chains import RetrievalQA
    from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

    # Create the prompt template with system message
    system_template = SystemMessagePromptTemplate.from_template(system_prompt)
    human_template = HumanMessagePromptTemplate.from_template("{question}")
    chat_prompt = ChatPromptTemplate.from_messages([system_template, human_template])

    qa = RetrievalQA.from_chain_type(
        llm=ChatLlamaCpp(temperature=0),
        chain_type="stuff",
        retriever=None,
        return_source_documents=False,
        chain_type_kwargs={"prompt": chat_prompt}
    )
    qa.retriever = lambda _: docs  # override retriever
    result = qa.run(question)
    return result
