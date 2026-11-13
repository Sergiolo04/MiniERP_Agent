from agent import agent
from langchain_core.messages import HumanMessage

while True:
    pregunta = input("\nTú: ")

    if pregunta.lower() == "salir":
        break

    resultado = agent.invoke(
        {"messages": [HumanMessage(content=pregunta)]},
        config={"recursion_limit": 12}
    )

    print("\nAgente:", resultado["messages"][-1].content)