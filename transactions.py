import sqlite3
from datetime import datetime

DB_PATH = "data/empresa.db"

def registrar_pedido(
    cliente_codigo: str,
    producto_codigo: str,
    cantidad: int
) -> dict:

    if type(cantidad) is not int or cantidad <= 0:
        return {"error": "Cantidad no valida."}

    conn = sqlite3.connect(
        DB_PATH,
        timeout=10,
        isolation_level=None
    )

    try:
        conn.execute("PRAGMA foreign_keys = ON") #activa la comprobación de claves foráneas en esta conexión.
        conn.execute("BEGIN IMMEDIATE") #Inicia la transacción y solicita el acceso necesario para escribir.

        #Mientras dure, otras conexiones no podrán escribir simultáneamente en la base de datos.

        cliente = conn.execute(
            """
            SELECT activo
            FROM clientes
            WHERE codigo = ?
            """,
            (cliente_codigo,)
        ).fetchone()

        if cliente is None or cliente[0] != 1:
            raise ValueError(
                "El cliente no existe o esta inactivo."
            )

        producto = conn.execute(
            """
            SELECT precio, stock
            FROM productos
            WHERE codigo = ?
            """,
            (producto_codigo,)
        ).fetchone()

        if producto is None:
            raise ValueError("Producto inexistente.")

        precio, stock = producto

        if stock < cantidad:
            raise ValueError("Stock insuficiente.")

        total = round(precio * cantidad, 2)

        cursor = conn.execute(
            """
            INSERT INTO pedidos (
                cliente_codigo, fecha, total
            )
            VALUES (?, ?, ?)
            """,
            (
                cliente_codigo,
                datetime.now().isoformat(),
                total
            )
        )

        pedido_id = cursor.lastrowid #recoge el idtenficiador que SQLite ha generado para ese pedido.
        #Lo necesitamos para asociarle su línea.

        conn.execute(
            """
            INSERT INTO lineas_pedido (
                pedido_id,
                producto_codigo,
                cantidad,
                precio_unitario
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                pedido_id,
                producto_codigo,
                cantidad,
                precio
            )
        )

        cursor = conn.execute(
            """
            UPDATE productos
            SET stock = stock - ?
            WHERE codigo = ? AND stock >= ?
            """,
            (
                cantidad,
                producto_codigo,
                cantidad
            )
        )

        if cursor.rowcount != 1:
            raise ValueError("Stock insuficiente.")

        conn.commit()

        return {
            "pedido_id": pedido_id,
            "total": total,
            "estado": "registrado"
        }
    
    except Exception as error:
        conn.rollback()
        return {"error": str(error)}

    finally:
        conn.close()