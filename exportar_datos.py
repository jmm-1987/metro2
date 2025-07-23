import os
import pandas as pd
from models import db, Usuario, Cliente, Tarea, Evento, RespuestaFormulario
from app import app

EXPORT_DIR = "export_csv"
os.makedirs(EXPORT_DIR, exist_ok=True)

# Columnas para usuario
usuario_columns = [
    "id", "nombre", "password", "es_admin", "color", "email", "telefono",
    "activo", "notificar_email", "notificar_telegram", "chat_id_telegram"
]

# Columnas para cliente
cliente_columns = [
    "id", "nombre", "email", "telefono", "estado", "localidad", "observaciones",
    "tipo_cliente", "interes", "zonas", "precio_min", "precio_max",
    "encuesta_enviada", "comercial_id", "fecha_creacion", "activo", "visto_por"
]

# Columnas para tarea
tarea_columns = [
    "id", "usuario_id", "cliente_id", "fecha", "hora", "comentario",
    "resolucion", "estado"
]

# Columnas para evento
evento_columns = [
    "id", "titulo", "descripcion", "fecha", "hora_inicio", "usuario_id", "cliente_id"
]

# Columnas para respuesta_formulario
respuesta_formulario_columns = [
    "id", "cliente_id", "puntuacion1", "puntuacion2", "puntuacion_media",
    "sugerencias", "fecha"
]

def export_usuarios():
    with app.app_context():
        data = Usuario.query.all()
        rows = [row.__dict__.copy() for row in data]
        for row in rows:
            row.pop('_sa_instance_state', None)
        df = pd.DataFrame(rows)
        for col in ["id"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')
        df = df.reindex(columns=usuario_columns)
        df.to_csv(f"{EXPORT_DIR}/usuarios.csv", index=False)

def export_clientes():
    with app.app_context():
        data = Cliente.query.all()
        rows = [row.__dict__.copy() for row in data]
        for row in rows:
            row.pop('_sa_instance_state', None)
        df = pd.DataFrame(rows)
        for col in ["id", "comercial_id", "precio_min", "precio_max", "visto_por"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')
        df = df.reindex(columns=cliente_columns)
        df.to_csv(f"{EXPORT_DIR}/clientes.csv", index=False)

def export_tareas():
    with app.app_context():
        data = Tarea.query.all()
        rows = [row.__dict__.copy() for row in data]
        for row in rows:
            row.pop('_sa_instance_state', None)
        df = pd.DataFrame(rows)
        for col in ["id", "usuario_id", "cliente_id"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')
        df = df.reindex(columns=tarea_columns)
        df.to_csv(f"{EXPORT_DIR}/tareas.csv", index=False)

def export_eventos():
    with app.app_context():
        data = Evento.query.all()
        rows = [row.__dict__.copy() for row in data]
        for row in rows:
            row.pop('_sa_instance_state', None)
        df = pd.DataFrame(rows)
        for col in ["id", "usuario_id", "cliente_id"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')
        df = df.reindex(columns=evento_columns)
        df.to_csv(f"{EXPORT_DIR}/eventos.csv", index=False)

def export_respuestas_formulario():
    with app.app_context():
        data = RespuestaFormulario.query.all()
        rows = [row.__dict__.copy() for row in data]
        for row in rows:
            row.pop('_sa_instance_state', None)
        df = pd.DataFrame(rows)
        for col in ["id", "cliente_id", "puntuacion1", "puntuacion2"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')
        df = df.reindex(columns=respuesta_formulario_columns)
        df.to_csv(f"{EXPORT_DIR}/respuestas_formulario.csv", index=False)

if __name__ == "__main__":
    export_usuarios()
    export_clientes()
    export_tareas()
    export_eventos()
    export_respuestas_formulario() 