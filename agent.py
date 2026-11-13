from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END, MessagesState #MessageState define un estado que contiene una lista de mensajes.
from langgraph.prebuilt import ToolNode, tools_condition #tools_condition comprueba si el modelo ha solicitado herramientas.
from langchain_core.messages import SystemMessage

from tools import tools #importamos la lista de las 4 herramientas desde tools.py (así quedan disponibles para cuando hagan falta)

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)

llm_with_tools = llm.bind_tools(tools) #informamos al modelo de las herramientas disponibles

SYSTEM_PROMPT = """
Eres un asistente de gestion empresarial.

Puedes consultar:
- Politicas comerciales mediante RAG.
- Stock de productos.
- Informacion de clientes.
- Pedidos existentes.

Utiliza herramientas cuando necesites consultar datos.
No inventes stock, precios, clientes ni politicas.

Cuando uses documentos, cita la pagina disponible.

No afirmes que has creado, modificado o cancelado
un pedido. No tienes permiso de escritura.

Si un dato no aparece en las fuentes,
indica que no dispones de esa informacion.
"""

def call_llm(state: MessagesState):
    messages = [
        SystemMessage(content=SYSTEM_PROMPT)
    ] + state["messages"] #contiene los mensajes acumulados durante la ejecución

    response = llm_with_tools.invoke(messages) #enviamos los mensajes al modelo, ejeucta la petición y devuelve su respuesta

    return {"messages": [response]} #MessageState incorpora los mensaves nuevos al historial, por lo que no necesito devolver toda la conversación en cada paso

graph = StateGraph(MessagesState)

graph.add_node("assistant", call_llm)
graph.add_node("tools", ToolNode(tools))

graph.set_entry_point("assistant")

graph.add_conditional_edges(#La respuesta del modelo incluye llamadas a herramientas?
    "assistant",
    tools_condition, #FUNCION QUE COMPRUEBA SI HAY LLAMADAS A HERRAMIENTAS EN EL ÚLITMO MENSAJE DEL MODELO
    {
        "tools": "tools", #si detecta llamadas, continúa hacia el nodo "tools"
        "__end__": END #si no hay llamadas, termina
    }
)

graph.add_edge("tools", "assistant") #cuando terminen las herramientas, vuelve al modelo

agent = graph.compile()




