from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, RadioField, TextAreaField, SelectField, DateField, TimeField, IntegerField, SelectMultipleField
from wtforms.validators import DataRequired, Email, Length
from wtforms import widgets

class LoginForm(FlaskForm):
    nombre = StringField('Usuario', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Entrar')

class CrearUsuarioForm(FlaskForm):
    nombre = StringField('Usuario', validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=6)])
    email = StringField('Email', validators=[Email(), Length(max=120)])
    telefono = StringField('Teléfono', validators=[Length(max=20)])
    es_admin = BooleanField('Administrador')
    submit = SubmitField('Crear usuario')

class CrearClienteForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired()])
    email = StringField('Email')
    telefono = StringField('Teléfono')
    localidad = StringField('Localidad')
    observaciones = TextAreaField('Observaciones')
    tipo_cliente = SelectField('Tipo de cliente', choices=[
        ('', 'No especificado'),
        ('inversor', 'Inversor'),
        ('comprador', 'Comprador'),
        ('arrendatario', 'Arrendatario')
    ])
    interes = SelectMultipleField('Interés en', choices=[
        ('vivienda', 'Vivienda'),
        ('local comercial', 'Local comercial'),
        ('nave industrial', 'Nave industrial'),
        ('terreno', 'Terreno'),
        ('finca rustica', 'Finca rústica')
    ], option_widget=widgets.CheckboxInput(), widget=widgets.ListWidget(prefix_label=False))
    precio_min = IntegerField('Precio mínimo dispuesto a pagar')
    precio_max = IntegerField('Precio máximo dispuesto a pagar')
    temperatura = RadioField('Temperatura', choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')], default=1, coerce=int)
    estado = SelectField('Estado', choices=[('en_curso', 'En curso'), ('finalizado', 'Finalizado'), ('descartado', 'Descartado')], default='en_curso')
    comercial_id = SelectField('Comercial habitual', coerce=int, choices=[])
    inmueble_id = SelectField('Inmueble asociado', coerce=int, choices=[])
    fecha_creacion = DateField('Fecha de alta', format='%Y-%m-%d', render_kw={'readonly': True})
    submit = SubmitField('Crear cliente')

class CrearInmuebleForm(FlaskForm):
    direccion = StringField('Dirección', validators=[DataRequired()])
    descripcion = TextAreaField('Descripción')
    categoria = SelectField('Categoría', choices=[
        ('vivienda', 'Vivienda'),
        ('local comercial', 'Local comercial'),
        ('nave industrial', 'Nave industrial'),
        ('terreno', 'Terreno'),
        ('finca rustica', 'Finca rústica')
    ])
    precio_min = IntegerField('Precio mínimo')
    precio_max = IntegerField('Precio máximo')
    visto_por_ids = SelectMultipleField('Visto por', coerce=int)
    estado = SelectField('Estado', choices=[('en_venta', 'En venta'), ('vendido', 'Vendido'), ('cancelado', 'Cancelado'), ('en_alquiler', 'En alquiler')], default='en_venta')
    submit = SubmitField('Crear inmueble')

class CrearRegistroForm(FlaskForm):
    usuario_id = SelectField('Usuario', coerce=int, choices=[], validators=[DataRequired()])
    cliente_id = SelectField('Cliente', coerce=int, choices=[], validators=[DataRequired()])
    inmueble_id = SelectField('Inmueble', coerce=int, choices=[], validators=[DataRequired()])
    fecha = DateField('Fecha', validators=[DataRequired()])
    comentario = TextAreaField('Comentario')
    submit = SubmitField('Crear registro')

class CrearEventoForm(FlaskForm):
    titulo = StringField('Título', validators=[DataRequired()])
    fecha = DateField('Fecha', validators=[DataRequired()])
    hora_inicio = TimeField('Hora de inicio')
    hora_fin = TimeField('Hora de fin')
    usuario_id = SelectField('Comercial', coerce=int, choices=[])
    cliente_id = SelectField('Cliente', coerce=int, choices=[])
    inmueble_id = SelectField('Inmueble', coerce=int, choices=[])
    descripcion = TextAreaField('Descripción')
    submit = SubmitField('Crear evento') 