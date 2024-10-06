import os
import shutil
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import TextLoader, PyPDFLoader

openai_api_key = 'api_key'

if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set")

embeddings = OpenAIEmbeddings(api_key=openai_api_key)

def initialize_chroma(persist_directory="./my_chroma_db"):
    return Chroma(
        embedding_function=embeddings,
        collection_name="my_collection",
        persist_directory=persist_directory
    )

def delete_collection():
    try:
        if vector_db is not None:
            vector_db.delete_collection()
            print("The entire collection has been deleted.")
    except Exception as e:
        print(f"An error occurred while trying to delete the collection: {e}")

def add_document_to_chroma(file_path):
    global vector_db
    try:
        if vector_db is None:
            vector_db = initialize_chroma()

        if file_path.lower().endswith('.pdf'):
            loader = PyPDFLoader(file_path)
        elif file_path.lower().endswith('.txt'):
            loader = TextLoader(file_path, encoding='utf-8')
        else:
            print("Unsupported file format. Please provide a .txt or .pdf file.")
            return
        
        documents = loader.load()
        print(f"Loaded {len(documents)} document(s) from {file_path}.")

        text_splitter = CharacterTextSplitter(chunk_size=1500, chunk_overlap=200)
        texts = text_splitter.split_documents(documents)
        print(f"Split into {len(texts)} chunks.")

        if texts:
            vector_db.add_documents(texts)
            print(f"Added {len(texts)} text chunks from {file_path} to Chroma DB")
        else:
            print("No valid text chunks to add.")
    except UnicodeDecodeError as e:
        print(f"Error decoding the file: {e}")
    except RuntimeError as e:
        print(f"Runtime error while loading the document: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def check_all_ids():
    global vector_db
    try:
        if vector_db is None:
            vector_db = initialize_chroma()

        results = vector_db.get()
        if 'ids' in results and len(results['ids']) > 0:
            print("Documents in Chroma DB:")
            for i, doc_id in enumerate(results['ids']):
                print(f"ID {i+1}: {doc_id}")
        else:
            print("No documents found in the collection.")
    except Exception as e:
        print(f"An error occurred while trying to fetch document IDs: {e}")

def query_chroma(query_text):
    global vector_db
    try:
        if vector_db is None:
            vector_db = initialize_chroma()

        results = vector_db.query(query_texts=[query_text], n_results=2)
        print("Query Results:")
        print(results)
    except Exception as e:
        print(f"An error occurred while querying the database: {e}")

def main():
    global vector_db
    vector_db = initialize_chroma()
    while True:
        command = input("Enter 'add' to add a file, 'delete all' to delete the entire collection, 'check ids' to view all document IDs, 'query' to query the database, or 'q' to quit: ")
        if command.lower() == 'q':
            break
        elif command.lower() == 'add':
            file_path = input("Enter the path to the text or PDF file you want to add: ")
            if os.path.exists(file_path):
                add_document_to_chroma(file_path)
            else:
                print("File not found. Please enter a valid file path.")
        elif command.lower() == 'delete all':
            delete_collection()
            vector_db = None
        elif command.lower() == 'check ids':
            check_all_ids()
        elif command.lower() == 'query':
            query_text = input("Enter the text to query the database: ")
            query_chroma(query_text)
        else:
            print("Invalid command. Please enter 'add', 'delete all', 'check ids', 'query', or 'q'.")

if __name__ == "__main__":
    main()
