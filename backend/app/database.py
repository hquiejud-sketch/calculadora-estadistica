"""Base de datos SQLite (viene incluida con Python, no hay que instalar nada).

Tablas:
  - analisis:   cada cálculo guardado con su entrada, opciones y resultado completo
  - historial:  bitácora de acciones (ANALIZAR, GUARDAR, ELIMINAR, IA_INTERPRETAR, IA_CHAT, IMPORTAR)
  - mensajes:   conversación con el tutor de IA, ligada a un análisis guardado
"""

import json
import sqlite3
from contextlib import contextmanager

from .config import DB_PATH

ESQUEMA = """
CREATE TABLE IF NOT EXISTS analisis (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    creado_en   TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    titulo      TEXT NOT NULL,
    tipo        TEXT NOT NULL,
    n           INTEGER NOT NULL,
    media       REAL,
    mediana     REAL,
    desviacion  REAL,
    cv          REAL,
    entrada     TEXT NOT NULL,
    opciones    TEXT NOT NULL,
    resultado   TEXT NOT NULL,
    interpretacion TEXT
);
CREATE TABLE IF NOT EXISTS historial (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha    TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    accion   TEXT NOT NULL,
    detalle  TEXT
);
CREATE TABLE IF NOT EXISTS mensajes (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    analisis_id  INTEGER REFERENCES analisis(id) ON DELETE CASCADE,
    fecha        TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    rol          TEXT NOT NULL,
    contenido    TEXT NOT NULL
);
"""


@contextmanager
def conexion():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    try:
        yield con
        con.commit()
    finally:
        con.close()


def iniciar_db():
    with conexion() as con:
        con.executescript(ESQUEMA)


# ----------------------------- historial -----------------------------

def registrar(accion: str, detalle: str = ""):
    with conexion() as con:
        con.execute("INSERT INTO historial (accion, detalle) VALUES (?, ?)", (accion, detalle))


def listar_historial(limite: int = 100):
    with conexion() as con:
        filas = con.execute("SELECT * FROM historial ORDER BY id DESC LIMIT ?", (limite,)).fetchall()
    return [dict(f) for f in filas]


def borrar_historial():
    with conexion() as con:
        con.execute("DELETE FROM historial")


# ----------------------------- análisis -----------------------------

def guardar_analisis(titulo, tipo, entrada, opciones, resultado, interpretacion=None):
    tc = resultado["tendencia_central"]
    disp = resultado["dispersion"]
    n = resultado["resumen"]["n"] if tipo == "no_agrupados" else resultado["parametros"]["n"]
    with conexion() as con:
        cur = con.execute(
            """INSERT INTO analisis (titulo, tipo, n, media, mediana, desviacion, cv,
                                     entrada, opciones, resultado, interpretacion)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (titulo, tipo, n, tc["media"]["valor"], tc["mediana"]["valor"], disp["desviacion"]["valor"],
             disp["coeficiente_variacion"]["valor"], json.dumps(entrada), json.dumps(opciones),
             json.dumps(resultado), interpretacion),
        )
        return cur.lastrowid


def listar_analisis():
    with conexion() as con:
        filas = con.execute(
            "SELECT id, creado_en, titulo, tipo, n, media, mediana, desviacion, cv FROM analisis ORDER BY id DESC"
        ).fetchall()
    return [dict(f) for f in filas]


def obtener_analisis(analisis_id: int):
    with conexion() as con:
        fila = con.execute("SELECT * FROM analisis WHERE id = ?", (analisis_id,)).fetchone()
        if not fila:
            return None
        mensajes = con.execute(
            "SELECT rol, contenido, fecha FROM mensajes WHERE analisis_id = ? ORDER BY id", (analisis_id,)
        ).fetchall()
    d = dict(fila)
    for campo in ("entrada", "opciones", "resultado"):
        d[campo] = json.loads(d[campo])
    d["mensajes"] = [dict(m) for m in mensajes]
    return d


def actualizar_interpretacion(analisis_id: int, texto: str):
    with conexion() as con:
        con.execute("UPDATE analisis SET interpretacion = ? WHERE id = ?", (texto, analisis_id))


def eliminar_analisis(analisis_id: int) -> bool:
    with conexion() as con:
        cur = con.execute("DELETE FROM analisis WHERE id = ?", (analisis_id,))
        return cur.rowcount > 0


def guardar_mensaje(analisis_id, rol, contenido):
    if not analisis_id:
        return
    with conexion() as con:
        con.execute("INSERT INTO mensajes (analisis_id, rol, contenido) VALUES (?, ?, ?)",
                    (analisis_id, rol, contenido))
