from langchain_core.messages import HumanMessage
from agent import agent
from transactions import registrar_pedido
from tools import consultar_stock, consultar_cliente


def consultar_agente():
    pregunta = input("Pregunta: ")

    resultado = agent.invoke(
        {
            "messages": [
                HumanMessage(content=pregunta)
            ]
        },
        config={"recursion_limit": 12}
    )

    print("\nRESPUESTA:")
    print(resultado["messages"][-1].content)


def preparar_pedido():
    cliente = input("Codigo cliente: ").strip()
    producto = input("Codigo producto: ").strip()

    try:
        cantidad = int(input("Cantidad: "))
    except ValueError:
        print("Cantidad no valida.")
        return

    if cantidad <= 0:
        print("La cantidad debe ser positiva.")
        return

    print("\nCLIENTE:")
    print(consultar_cliente.invoke({"codigo": cliente}))

    print("\nPRODUCTO:")
    print(consultar_stock.invoke({"codigo": producto}))

    print("\nRESUMEN DE SOLICITUD")
    print(f"Cliente: {cliente}")
    print(f"Producto: {producto}")
    print(f"Cantidad: {cantidad}")

    print(
        "\nLa operacion modificara los pedidos "
        "y el stock de la base de datos."
    )

    confirmacion = input(
        "Escribe CONFIRMAR para registrar: "
    ).strip()

    if confirmacion != "CONFIRMAR":
        print("Operacion cancelada.")
        return

    resultado = registrar_pedido(
        cliente_codigo=cliente,
        producto_codigo=producto,
        cantidad=cantidad
    )

    print("\nRESULTADO:")
    print(resultado)


def main():
    while True:
        print("\n=== MINI ERP AGENT ===")
        print("1. Preguntar al agente")
        print("2. Preparar y registrar pedido")
        print("3. Salir")

        opcion = input("Selecciona una opcion: ")

        if opcion == "1":
            consultar_agente()
        elif opcion == "2":
            preparar_pedido()
        elif opcion == "3":
            break
        else:
            print("Opcion no valida.")


if __name__ == "__main__":
    main()