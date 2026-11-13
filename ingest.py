#Prepara el pdf para que después el agente pueda buscar información dentro de él

from dotenv import load_dotenv
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

load_dotenv()

PDF_PATH = "data/politicas_empresa.pdf"
CHROMA_PATH = "./chroma_db"

if not Path(PDF_PATH).exists():
    raise FileNotFoundError(PDF_PATH)

loader = PyPDFLoader(PDF_PATH)
pages = loader.load() #pages contiene una lista de objetos llamados "Document" (contiene texto y metadatos)

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100
)

chunks = splitter.split_documents(pages) #en chunks tenemos los fragmentos con sus metadatos

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small"
)

vectorstore = Chroma(
    collection_name="politicas",
    persist_directory=CHROMA_PATH,
    embedding_function=embeddings
)
 
ids = [f"politica_chunk_{i}" for i in range(len(chunks))] #Genera una lista como esta: ["politica_chunk_0", "politica_chunk_1", "politica_chunk_2"]

vectorstore.add_documents( #se envia el texto de los fragmentos a la API de OpenAI para obtener sus embeddings
    documents=chunks,      #Se guardan en ChromaDB los textos, embedidings, metadatos e identificadores
    ids=ids
)

print(f"Paginas procesadas: {len(pages)}")
print(f"Fragmentos creados: {len(chunks)}")
print("Base vectorial preparada.")

