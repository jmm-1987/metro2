from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, RadioField, TextAreaField, SelectField, DateField, TimeField, IntegerField, SelectMultipleField, HiddenField
from wtforms.validators import DataRequired, Email, Length, Optional
from wtforms import widgets
from datetime import time

class LoginForm(FlaskForm):
    nombre = StringField('Usuario', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Entrar')

class CrearUsuarioForm(FlaskForm):
    nombre = StringField('Usuario', validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField('Contraseña', validators=[Optional(), Length(min=6)])
    email = StringField('Email', validators=[Email(), Length(max=120)])
    telefono = StringField('Teléfono', validators=[Length(max=20)])
    es_admin = BooleanField('Administrador')
    color = StringField('Color para el calendario')
    notificar_email = BooleanField('Notificar por email')
    notificar_telegram = BooleanField('Notificar por telegram')
    chat_id_telegram = StringField('Chat ID de Telegram')
    submit = SubmitField('Crear usuario')

class CrearClienteForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired()])
    email = StringField('Email')
    telefono = StringField('Teléfono', validators=[DataRequired()])
    localidad = StringField('Localidad', validators=[DataRequired()])
    observaciones = TextAreaField('Observaciones')
    tipo_cliente = SelectField('Tipo de cliente', choices=[
        ('', 'No especificado'),
        ('inversor', 'Inversor'),
        ('comprador', 'Comprador'),
        ('arrendatario', 'Arrendatario'),
        ('arrendador', 'Arrendador'),
        ('vendedor', 'Vendedor')
    ])
    interes = SelectMultipleField('Interés en', choices=[
        ('vivienda', 'Vivienda'),
        ('local comercial', 'Local comercial'),
        ('nave industrial', 'Nave industrial'),
        ('terreno', 'Terreno'),
        ('finca rustica', 'Finca rústica')
    ], option_widget=widgets.CheckboxInput(), widget=widgets.ListWidget(prefix_label=False))
    zonas = SelectMultipleField('Zonas', choices=[
        ('abadias', 'Abadias'),
        ('abadias norte', 'Abadias Norte'),
        ('calzada', 'Calzada'),
        ('bodegones / zona sur', 'Bodegones / Zona Sur'),
        ('centro', 'Centro'),
        ('la corchera', 'La Corchera'),
        ('maria auxiliadora', 'Maria Auxiliadora'),
        ('sindicales', 'Sindicales'),
        ('montealto', 'Montealto'),
        ('nueva ciudad', 'Nueva Ciudad'),
        ('prado / ifeme', 'Prado / IFEME'),
        ('proserpina', 'Proserpina'),
        ('salesianos', 'Salesianos'),
        ('vivero', 'Vivero'),
        ('san juan / santa isabel', 'San Juan / Santa Isabel'),
        ('plantonal', 'Plantonal'),
        ('san andres', 'San Andres')
    ], option_widget=widgets.CheckboxInput(), widget=widgets.ListWidget(prefix_label=False))
    precio_min = IntegerField('Precio mínimo dispuesto a pagar', validators=[Optional()])
    precio_max = IntegerField('Precio máximo dispuesto a pagar', validators=[Optional()])
    estado = SelectField('Estado', choices=[('en_curso', 'En curso'),('pendiente', 'Standby'), ('finalizado', 'Finalizado')], default='en_curso')
    comercial_id = SelectField('Comercial habitual', coerce=int, choices=[])
    fecha_creacion = DateField('Fecha de alta', format='%Y-%m-%d', render_kw={'readonly': True})
    submit = SubmitField('Crear cliente')

class CrearTareaForm(FlaskForm):
    usuario_id = SelectField('Usuario', coerce=int, choices=[], validators=[DataRequired()])
    cliente_id = HiddenField('Cliente ID', validators=[Optional()])
    cliente_nombre = StringField('Buscar Cliente', validators=[Optional()])
    fecha = DateField('Fecha', validators=[DataRequired()])
    # Generar opciones de hora cada 15 minutos entre 07:00 y 22:45
    hora_choices = [(f'{h:02d}:{m:02d}', f'{h:02d}:{m:02d}') for h in range(7,23) for m in (0,15,30,45)]
    hora = SelectField('Hora', choices=hora_choices, validators=[DataRequired()])
    comentario = TextAreaField('Comentario')
    resolucion = TextAreaField('Resolución')
    estado = SelectField('Estado', choices=[('por_hacer', 'Por hacer')], validators=[DataRequired()])
    submit = SubmitField('Crear tarea')

class ResolverTareaForm(FlaskForm):
    usuario_id = SelectField('Usuario', coerce=int, choices=[], validators=[DataRequired()])
    cliente_id = HiddenField('Cliente ID', validators=[Optional()])
    cliente_nombre = StringField('Buscar Cliente', validators=[Optional()])
    fecha = DateField('Fecha', validators=[DataRequired()])
    comentario = TextAreaField('Comentario')
    resolucion = TextAreaField('Resolución')
    estado = SelectField('Estado', choices=[('por_hacer', 'Por hacer'), ('pendiente', 'Standby'), ('cancelado', 'Cancelado'), ('reagendada', 'Reagendada')], validators=[DataRequired()])
    submit = SubmitField('Resolver tarea')

class CrearEventoForm(FlaskForm):
    titulo = StringField('Título', validators=[DataRequired()])
    fecha = DateField('Fecha', validators=[DataRequired()])
    hora_inicio = TimeField('Hora de inicio')
    usuario_id = SelectField('Comercial', coerce=int, choices=[])
    cliente_id = SelectField('Cliente', coerce=int, choices=[])
    descripcion = TextAreaField('Descripción')
    submit = SubmitField('Crear evento') 