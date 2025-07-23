from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy import Time
from datetime import datetime

db = SQLAlchemy()

class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    es_admin = db.Column(db.Boolean, default=False)
    color = db.Column(db.String(7), nullable=True, default='#3788d8') # Color en formato hex, e.g., #RRGGBB
    email = db.Column(db.String(120), unique=True, nullable=True)
    telefono = db.Column(db.String(20), unique=True, nullable=True)
    activo = db.Column(db.Boolean, default=True)  # Nuevo campo para desactivar usuario
    notificar_email = db.Column(db.Boolean, default=True)
    notificar_telegram = db.Column(db.Boolean, default=False)
    chat_id_telegram = db.Column(db.String(32), nullable=True)
    # Relación con Evento - backref crea 'usuario' en Evento
    eventos = db.relationship('Evento', backref='usuario', lazy=True)
    tareas = db.relationship('Tarea', back_populates='usuario')

class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    telefono = db.Column(db.String(20), unique=True)
    estado = db.Column(db.String(20), nullable=False, default='en_curso') # en_curso, ha_comprado, cancelado
    localidad = db.Column(db.String(120), nullable=True)
    observaciones = db.Column(db.Text, nullable=True)
    tipo_cliente = db.Column(db.String(50), nullable=True)
    interes = db.Column(db.Text, nullable=True)
    zonas = db.Column(db.Text, nullable=True)
    precio_min = db.Column(db.Integer, nullable=True)
    precio_max = db.Column(db.Integer, nullable=True)
    encuesta_enviada = db.Column(db.String(20), default="sin_enviar")
    comercial_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    activo = db.Column(db.Boolean, default=True)  # Nuevo campo para desactivar cliente
    eventos = db.relationship('Evento', backref='cliente', lazy=True)
    tareas = db.relationship('Tarea', back_populates='cliente')
    visto_por = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=True)

class Tarea(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'))
    fecha = db.Column(db.Date, nullable=False)
    hora = db.Column(db.Time, nullable=True)
    comentario = db.Column(db.Text)
    resolucion = db.Column(db.Text)
    estado = db.Column(db.String(20), nullable=False, default='por_hacer')  # por_hacer, ha_comprado, ha_alquilado, cancelado
    cliente = db.relationship('Cliente', back_populates='tareas')
    usuario = db.relationship('Usuario', back_populates='tareas')

class Evento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(120), nullable=False)
    descripcion = db.Column(db.Text)
    fecha = db.Column(db.Date, nullable=False)
    hora_inicio = db.Column(Time, nullable=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'))

class RespuestaFormulario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    puntuacion1 = db.Column(db.Integer, nullable=False)
    puntuacion2 = db.Column(db.Integer, nullable=True) # Hacer opcional
    puntuacion_media = db.Column(db.Float, nullable=False)
    sugerencias = db.Column(db.Text, nullable=True)
    fecha = db.Column(db.DateTime, nullable=False, default=datetime.utcnow) 