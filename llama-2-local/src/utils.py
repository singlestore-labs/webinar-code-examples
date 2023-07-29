'''
===========================================
        Module: Util functions
===========================================
'''
import box
import yaml
import os

from langchain import PromptTemplate
from langchain.chains import RetrievalQA
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS, SingleStoreDB
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFLoader, DirectoryLoader
from src.prompts import qa_template
from src.llm import build_llm

# Import config vars
with open('config/config.yml', 'r', encoding='utf8') as ymlfile:
    cfg = box.Box(yaml.safe_load(ymlfile))


def set_qa_prompt():
    """
    Prompt template for QA retrieval for each vectorstore
    """
    prompt = PromptTemplate(template=qa_template,
                            input_variables=['context', 'question'])
    return prompt


def build_retrieval_qa(llm, prompt, vectordb):
    dbqa = RetrievalQA.from_chain_type(llm=llm,
                                       chain_type='stuff',
                                       retriever=vectordb.as_retriever(search_kwargs={'k': cfg.VECTOR_COUNT}),
                                       return_source_documents=cfg.RETURN_SOURCE_DOCUMENTS,
                                       chain_type_kwargs={'prompt': prompt}
                                       )
    return dbqa


def setup_dbqa():
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2",
                                       model_kwargs={'device': 'cpu'})
    
    loader = DirectoryLoader(cfg.DATA_PATH,
                             glob='*.pdf',
                             loader_cls=PyPDFLoader)
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=cfg.CHUNK_SIZE,
                                                   chunk_overlap=cfg.CHUNK_OVERLAP)
    texts = text_splitter.split_documents(documents)

    os.environ["SINGLESTOREDB_URL"] = "admin:83nnuP3IAHOig4inMZWmV8vtRLvEWtTk@svc-1581bd74-8c1f-4de2-b3c0-c72858bb7a02-dml.aws-london-1.svc.singlestore.com:3306/llamaindex_notebook_test"
    vectorstore = SingleStoreDB(embeddings, distance_strategy="DOT_PRODUCT", table_name="demo0")

    # if you want to build a new vectorstore, use the following line instead of the above
    # vectorstore = SingleStoreDB.from_documents(texts, embeddings, distance_strategy="DOT_PRODUCT", table_name="demo0")

    llm = build_llm()
    qa_prompt = set_qa_prompt()
    dbqa = build_retrieval_qa(llm, qa_prompt, vectorstore)

    return dbqa
