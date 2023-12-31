import os
import glob
from typing import List
from multiprocessing import Pool
from tqdm import tqdm
from langchain.document_loaders import (
    CSVLoader,
    EverNoteLoader,
    PDFMinerLoader,
    TextLoader,
    UnstructuredEmailLoader,
    UnstructuredEPubLoader,
    UnstructuredHTMLLoader,
    UnstructuredMarkdownLoader,
    UnstructuredODTLoader,
    UnstructuredPowerPointLoader,
    UnstructuredWordDocumentLoader,
)
from langchain.docstore.document import Document
import time
from openai import OpenAI
from copy import copy
from langchain.text_splitter import RecursiveCharacterTextSplitter
import psycopg2

# 设置代理，如果没有，可以注释掉
import os
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:10809'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:10809'

# 选择本地中文分词模型
# sys.path.append('..')
from text2vec import SentenceModel
s_model = SentenceModel("shibing624/text2vec-bge-large-chinese")
# s_model = SentenceModel("shibing624/text2vec-base-chinese")

# 文本分块的大小
chunk_size = 800
chunk_overlap = 30

from pydantic import BaseModel, Field

# Map file extensions to document loaders and their arguments
LOADER_MAPPING = {
    ".csv": (CSVLoader, {}),
    ".doc": (UnstructuredWordDocumentLoader, {}),
    ".docx": (UnstructuredWordDocumentLoader, {}),
    ".enex": (EverNoteLoader, {}),
    ".epub": (UnstructuredEPubLoader, {}),
    ".html": (UnstructuredHTMLLoader, {}),
    ".md": (UnstructuredMarkdownLoader, {}),
    ".odt": (UnstructuredODTLoader, {}),
    ".pdf": (PDFMinerLoader, {}),
    ".ppt": (UnstructuredPowerPointLoader, {}),
    ".pptx": (UnstructuredPowerPointLoader, {}),
    ".txt": (TextLoader, {"encoding": "utf8"}),
}

def load_single_document(file_path: str) -> Document:
    """
    加载单个文件
    """
    ## Find extension of the file
    ext = "." + file_path.rsplit(".", 1)[-1] 
    if ext in LOADER_MAPPING: 
        # Find the appropriate loader class and arguments
        loader_class, loader_args = LOADER_MAPPING[ext] 
        # Invoke the instance of document loader
        loader = loader_class(file_path, **loader_args) 
        ## Return the loaded document
        return loader.load()[0] 
    raise ValueError(f"Unsupported file extension '{ext}'")




def getChunks(doc:List[Document]):
    """
    文本分块
    """
     ## Split text
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    texts = text_splitter.split_documents(doc)
    print(f"Split into {len(texts)} chunks of text (max. {chunk_size} tokens each)")
    return texts


def load_documents(source_dir: str, ignored_files: List[str] = []) -> List[Document]:
    """
    Loads all documents from the source documents directory, ignoring specified files
    """
    all_files = []
    for ext in LOADER_MAPPING:
        #Find all the files within source documents which matches the extensions in Loader_Mapping file
        all_files.extend(
            glob.glob(os.path.join(source_dir, f"**/*{ext}"), recursive=True)
        )
    
    ## Filtering files from all_files if its in ignored_files
    filtered_files = [file_path for file_path in all_files if file_path not in ignored_files]
    
    ## Spinning up resource pool
    with Pool(processes=os.cpu_count()) as pool:
        results = []
        with tqdm(total=len(filtered_files), desc='Loading new documents', ncols=80) as pbar:
            # Load each document from filtered files list using load_single_document function
            for i, doc in enumerate(pool.imap_unordered(load_single_document, filtered_files)):
                results.append(doc)
                pbar.update()
    
    return results

def process_documents(source_dir: str, ignored_files: List[str] = []) -> List[Document]:
    """
    Load documents and split in chunks
    """
    print(f"Loading documents from {source_dir}")
    documents = load_documents(source_dir, ignored_files)
    if not documents:
        print("No new documents to load")
        exit(0)
    print(f"Loaded {len(documents)} new documents from {source_dir}")
    ## Load text splitter
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    ## Split text
    texts = text_splitter.split_documents(documents)
    print(f"Split into {len(texts)} chunks of text (max. {chunk_size} tokens each)")
    return texts




def embedding(document:Document):
    """
    使用本地模型处理向量信息
    """
    embeddings = s_model.encode(document.page_content, normalize_embeddings=True)
    return embeddings.tolist()


def embed_OpenAi(document:Document):
    """
    使用openai 的接口作获取向量信息
    """
    api_key = os.getenv("OPENAI_API_KEY")

    client = OpenAI(api_key=api_key)
    # Your text input
    text = document.page_content
    # Get the embedding
    response = client.embeddings.create(
        input=text,
        model="text-embedding-ada-002"  # Example model
    )
    # print("response",response)
    # The embedding vector
    embedding_vector = response.data[0].embedding
    return embedding_vector
    # You can now use this vector for further processing




def insert_vector_data(conn_str, table_name, vector_field, filename,content,vector_data):
    """
    Inserts vector data into a PostgreSQL table with a pgvector column.

    Parameters:
    conn_str (str): The connection string for the database.
    table_name (str): The name of the table to insert data into.
    vector_data (list): The vector data to insert (as a list of floats).
    """
    try:
        # Connect to the database using the connection string
        conn = psycopg2.connect(conn_str)
        cur = conn.cursor()
        from psycopg2.extensions import adapt, AsIs
        vector_data_adapted = AsIs(psycopg2.extensions.adapt(vector_data))

        # Insert the vector data
        cur.execute(f"INSERT INTO {table_name} (filename,content,{vector_field}) VALUES (%s,%s,%s);", (filename,content,vector_data_adapted))

        # Commit the transaction and close the connection
        conn.commit()
        cur.close()
        conn.close()

        return "Data inserted successfully."

    except psycopg2.Error as e:
        return f"An error occurred: {e}"



class RequestModel(BaseModel):
    ignored_files:List[str] = Field(...)
    dir:str = Field(...)
    load_dir:bool = Field(...)
    filename: str = Field(...)
    db_connection_string: str = Field(...)
    table_name: str = Field(...)
    vector_field: str = Field(...)
    content_field:str = Field(...)


def load_single_file(instance:RequestModel):
    doc = load_single_document(instance.filename)
    chunks = getChunks([doc])

     # Connect to the database using the connection string
    conn = psycopg2.connect(instance.db_connection_string)
    cur = conn.cursor()
    from psycopg2.extensions import adapt, AsIs
    
    try:
        total_documents = len(chunks)
        for i, doc in enumerate(chunks, start=1):
            start_time = time.time()  # Start time before the embedding

            emb = embedding(doc)  # Perform the embedding
            # emb = embed_OpenAi(doc)  # Perform the embedding

            end_time = time.time()  # End time after the embedding
            elapsed_time = end_time - start_time  # Calculate elapsed time

            vector_data_adapted = AsIs(adapt(emb))

            # Insert the vector data
            cur.execute(f"INSERT INTO {instance.table_name} (filename,content,{instance.vector_field}) VALUES (%s,%s,%s);", 
                        (instance.filename, doc.page_content, vector_data_adapted))
            conn.commit()
            print(f"Document {i}/{total_documents} inserted successfully. Embedding took {elapsed_time:.2f} seconds")

    except Exception as e:
        print(f"An error occurred: {e}")
    cur.close()
    conn.close()

def load_file(instance:RequestModel):
    """
    加载文件到数据库

    如果文件很大，会非常的耗时
    """
    load_single_file(instance)
    

def load_dir(instance:RequestModel):
    """
    加载一个目录下所有的文件到数据库
    """
    all_files = []
    for ext in LOADER_MAPPING:
        #Find all the files within source documents which matches the extensions in Loader_Mapping file
        all_files.extend(
            glob.glob(os.path.join(instance.dir, f"**/*{ext}"), recursive=True)
        )
    
    ## Filtering files from all_files if its in ignored_files
    filtered_files = [file_path for file_path in all_files if file_path not in instance.ignored_files]
    
    docs = []
    for file in filtered_files:
        doc = copy(instance)
        doc.filename = file
        docs.append(doc) 
        

    ## Spinning up resource pool
    # 控制并发写入使用的处理器数量
    with Pool(processes=2) as pool:
    # with Pool(processes=os.cpu_count()) as pool:
        results = []
        with tqdm(total=len(filtered_files), desc='Loading new documents', ncols=80) as pbar:
            # Load each document from filtered files list using load_single_document function
            for i, doc in enumerate(pool.imap_unordered(load_single_file, docs)):
                results.append(doc)
                pbar.update()
    