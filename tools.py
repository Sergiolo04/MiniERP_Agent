#Cotiene las 4 herramientas que el agente utilizará para consultar información.
#buscar_politicas recibe una pregunta y consulta las políticas guardadas en ChromaDB
#consultar_stock recibe un codigo de producto y consulta su nombre,precio y stock en sqlite
#consultar_cliente recibe un código de cliente y consulta su nombre y el estado del cliente en sqlite
#consultar_pedido recibo un codigo de cliente y consulta sus pedidos en sqlite
#TODAS SON DE LECTURA: NINGUNA CREA PEDIDOS NI MODIFICA EL STOCK

import sqlite3 #permite consultar empresa.db
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

load_dotenv()

DB_PATH = "data/empresa.db"

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small"
)

vectorstore = Chroma(
    collection_name="politicas",
    persist_directory="./chroma_db",
    embedding_function=embeddings
)

retriever = vectorstore.as_retriever( #buscador que recuperará fragmentos de la coleccion "politicas"
    search_type="similarity",
    search_kwargs={"k": 3}
)

@tool
def buscar_politicas(query: str) -> str:
    """
    Busca informacion sobre las politicas
    y procedimientos comerciales de la empresa.
    """
    docs = retriever.invoke(query) #busca los fragmentos relacionados con la pregunta, docs contiene esos fragmentos como objetos Document

    if not docs:
        return "No se encontraron documentos."

    resultados = []

    for doc in docs:
        pagina = doc.metadata.get("page", 0) + 1
        resultados.append(
            f"Pagina {pagina}: {doc.page_content}"
        )

    return "\n\n".join(resultados)

@tool
def consultar_stock(codigo: str) -> str:
    """
    Consulta el nombre, precio y stock disponible
    de un producto identificado por su codigo.
    """
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute(
            """
            SELECT nombre, precio, stock
            FROM productos
            WHERE codigo = ?
            """,
            (codigo,)
        ).fetchone() #Recoge una fila del resultado por ejemplo ("Zapato profesional", 49.90, 40)

    if row is None:
        return "Producto no encontrado."

    nombre, precio, stock = row

    return (
        f"Producto: {nombre}\n"
        f"Precio: {precio:.2f} EUR\n"
        f"Stock: {stock}"
    )

@tool
def consultar_cliente(codigo: str) -> str:
    """
    Consulta si un cliente existe y si esta activo.
    """
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute(
            """
            SELECT nombre, activo
            FROM clientes
            WHERE codigo = ?
            """,
            (codigo,)
        ).fetchone()

    if row is None:
        return "Cliente no encontrado."

    nombre, activo = row

    return (
        f"Cliente: {nombre}\n"
        f"Activo: {bool(activo)}"
    )

@tool
def consultar_pedidos(cliente_codigo: str) -> str:
    """
    Consulta los pedidos registrados de un cliente.
    """
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(
            """
            SELECT id, fecha, total
            FROM pedidos
            WHERE cliente_codigo = ?
            ORDER BY id DESC
            """,
            (cliente_codigo,)
        ).fetchall() #Recoge todas las filas encontradas, porque un cliente puede tener varios pedidos.

    if not rows:
        return "No existen pedidos registrados."

    return "\n".join(
        f"Pedido {id_} | {fecha} | {total:.2f} EUR"
        for id_, fecha, total in rows
    )

tools = [
    buscar_politicas,
    consultar_stock,
    consultar_cliente,
    consultar_pedidos
]
