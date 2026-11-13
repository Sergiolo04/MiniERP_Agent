import sqlite3
from pathlib import Path


DB_PATH = Path("data/empresa.db")
DB_PATH.parent.mkdir(exist_ok=True)

conn = sqlite3.connect(DB_PATH)
conn.execute("PRAGMA foreign_keys = ON")

cursor = conn.cursor()

cursor.executescript("""
CREATE TABLE IF NOT EXISTS productos (
    codigo TEXT PRIMARY KEY,
    nombre TEXT NOT NULL,
    precio REAL NOT NULL CHECK(precio >= 0),
    stock INTEGER NOT NULL CHECK(stock>= 0)
);

CREATE TABLE IF NOT EXISTS clientes(
    codigo TEXT PRIMARY KEY,
    nombre TEXT NOT NULL,
    activo INTEGER NOT NULL CHECK(activo IN (0,1) )
);

CREATE TABLE IF NOT EXISTS pedidos(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_codigo TEXT NOT NULL,
    fecha TEXT NOT NULL,
    total REAL NOT NULL,
    FOREIGN KEY(cliente_codigo)
        REFERENCES clientes(codigo)
);

CREATE TABLE IF NOT EXISTS lineas_pedido (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pedido_id INTEGER NOT NULL,
    producto_codigo TEXT NOT NULL,
    cantidad INTEGER NOT NULL CHECK(cantidad > 0),
    precio_unitario REAL NOT NULL,
    FOREIGN KEY(pedido_id) REFERENCES pedidos(id),
    FOREIGN KEY(producto_codigo)
        REFERENCES productos(codigo)
);

""")

productos = [
    ("ZAP-001", "Zapato profesional", 49.90, 40),
    ("ZAP-002", "Zueco sanitario", 39.90, 25),
    ("ACC-001", "Plantilla ergonomica", 12.50, 100)
]
clientes = [
    ("CLI-001", "Clinica Mediterraneo", 1),
    ("CLI-002", "Farmacia Central", 1),
    ("CLI-003", "Cliente inactivo", 0)
]

cursor.executemany(
    "INSERT OR IGNORE INTO productos VALUES (?, ?, ?, ?)",
    productos
)

cursor.executemany(
    "INSERT OR IGNORE INTO clientes VALUES (?, ?, ?)",
    clientes
)

conn.commit()
conn.close()

print("Base de datos creada correctamente.")



