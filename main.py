from agent import agent
from langchain_core.messages import HumanMessage
from tools import consultar_cliente, consultar_stock
from transactions import registrar_pedido


def preguntar():
    pregunta = input("\nTú: ")

    resultado = agent.invoke(
        {"messages": [HumanMessage(content=pregunta)]},
        config={"recursion_limit": 12}
    )

    print("\nAgente:", resultado["messages"][-1].content)


def preparar_pedido():
    cliente = input("Código del cliente: ").strip()
    producto = input("Código del producto: ").strip()

    try:
        cantidad = int(input("Cantidad: "))
    except ValueError:
        print("La cantidad debe ser un número entero.")
        return

    if cantidad <= 0:
        print("La cantidad debe ser mayor que cero.")
        return

    print("\nCLIENTE:")
    print(consultar_cliente.invoke({"codigo": cliente}))

    print("\nPRODUCTO:")
    print(consultar_stock.invoke({"codigo": producto}))

    print("\nSOLICITUD:")
    print(f"Cliente: {cliente}")
    print(f"Producto: {producto}")
    print(f"Cantidad: {cantidad}")

    print("\nEsta operación registrará un pedido y descontará stock.")
    confirmacion = input("Escribe CONFIRMAR para continuar: ").strip()

    if confirmacion != "CONFIRMAR":
        print("Operación cancelada.")
        return

    resultado = registrar_pedido(
        cliente_codigo=cliente,
        producto_codigo=producto,
        cantidad=cantidad
    )

    if "error" in resultado:
        print("\nError:", resultado["error"])
    else:
        print("\nPedido registrado:", resultado["pedido_id"])
        print(f"Total: {resultado['total']:.2f} EUR")


def main():
    while True:
        print("\n=== MINI ERP AGENT ===")
        print("1. Preguntar al agente")
        print("2. Registrar pedido")
        print("3. Salir")

        opcion = input("Elige una opción: ").strip()

        if opcion == "1":
            preguntar()
        elif opcion == "2":
            preparar_pedido()
        elif opcion == "3":
            break
        else:
            print("Opción no válida.")


if __name__ == "__main__":
    main()