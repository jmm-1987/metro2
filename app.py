from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from forms import LoginForm, CrearUsuarioForm, CrearClienteForm, CrearInmuebleForm, CrearRegistroForm, CrearEventoForm
from wtforms import StringField, DateField, SelectField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
import datetime
import smtplib
from email.message import EmailMessage

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cambia_esto_por_un_valor_seguro'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

from models import db, Usuario, Cliente, Registro, Evento, Inmueble, RespuestaFormulario
db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

@app.route('/')
@login_required
def dashboard():
    eventos_proximos = Evento.query.filter(Evento.fecha >= datetime.date.today()).order_by(Evento.fecha.asc()).limit(5).all()
    temp_totales = {i: Cliente.query.filter_by(temperatura=i).count() for i in range(1, 6)}
    clientes_list = Cliente.query.filter_by(estado='en_curso').order_by(Cliente.temperatura.desc(), Cliente.nombre.asc()).limit(15).all()
    now = datetime.datetime.now()
    return render_template('dashboard.html', eventos_proximos=eventos_proximos, temp_totales=temp_totales, clientes_list=clientes_list, now=now)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(nombre=form.nombre.data).first()
        if usuario and check_password_hash(usuario.password, form.password.data):
            login_user(usuario)
            return redirect(url_for('dashboard'))
        flash('Usuario o contraseña incorrectos')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/clientes')
@login_required
def clientes():
    estado = request.args.get('estado')
    temperatura = request.args.get('temperatura')
    query = Cliente.query
    if estado:
        query = query.filter_by(estado=estado)
    if temperatura:
        query = query.filter_by(temperatura=int(temperatura))
    clientes = query.all()
    usuarios_dict = {u.id: u.nombre for u in Usuario.query.all()}
    inmuebles_dict = {i.id: i.direccion for i in Inmueble.query.all()}
    return render_template('clientes.html', clientes=clientes, usuarios_dict=usuarios_dict, inmuebles_dict=inmuebles_dict)

@app.route('/usuarios')
@login_required
def usuarios():
    if not current_user.es_admin:
        flash('No tienes permiso para acceder a esta página.')
        return redirect(url_for('calendario'))
    usuarios = Usuario.query.all()
    return render_template('usuarios.html', usuarios=usuarios)

@app.route('/crear_cliente', methods=['GET', 'POST'])
@login_required
def crear_cliente():
    form = CrearClienteForm()
    form.comercial_id.choices = [(0, 'Sin comercial')] + [(u.id, u.nombre) for u in Usuario.query.all()]
    form.inmueble_id.choices = [(0, 'Sin inmueble')] + [(i.id, i.direccion) for i in Inmueble.query.all()]
    if form.validate_on_submit():
        cliente = Cliente(
            nombre=form.nombre.data,
            email=form.email.data,
            telefono=form.telefono.data,
            localidad=form.localidad.data,
            observaciones=form.observaciones.data,
            tipo_cliente=form.tipo_cliente.data,
            interes=','.join(form.interes.data),
            precio_min=form.precio_min.data,
            precio_max=form.precio_max.data,
            temperatura=form.temperatura.data,
            estado=form.estado.data,
            comercial_id=form.comercial_id.data if form.comercial_id.data != 0 else None,
            inmueble_id=form.inmueble_id.data if form.inmueble_id.data != 0 else None
        )
        db.session.add(cliente)
        try:
            db.session.commit()
            flash('Cliente creado correctamente')
            return redirect(url_for('clientes'))
        except Exception as e:
            db.session.rollback()
            flash('Error al crear cliente: {}'.format(str(e)))
    return render_template('crear_cliente.html', form=form)

@app.route('/editar_cliente/<int:cliente_id>', methods=['GET', 'POST'])
@login_required
def editar_cliente(cliente_id):
    cliente = Cliente.query.get_or_404(cliente_id)
    form = CrearClienteForm(obj=cliente)
    form.comercial_id.choices = [(0, 'Sin comercial')] + [(u.id, u.nombre) for u in Usuario.query.all()]
    form.inmueble_id.choices = [(0, 'Sin inmueble')] + [(i.id, i.direccion) for i in Inmueble.query.all()]
    if request.method == 'POST' and form.validate_on_submit():
        cliente.nombre = form.nombre.data
        cliente.email = form.email.data
        cliente.telefono = form.telefono.data
        cliente.localidad = form.localidad.data
        cliente.observaciones = form.observaciones.data
        cliente.tipo_cliente = form.tipo_cliente.data
        cliente.interes = ','.join(form.interes.data)
        cliente.precio_min = form.precio_min.data
        cliente.precio_max = form.precio_max.data
        cliente.temperatura = form.temperatura.data
        cliente.estado = form.estado.data
        cliente.comercial_id = form.comercial_id.data if form.comercial_id.data != 0 else None
        cliente.inmueble_id = form.inmueble_id.data if form.inmueble_id.data != 0 else None
        try:
            db.session.commit()
            flash('Cliente actualizado correctamente')
            return redirect(url_for('clientes'))
        except Exception as e:
            db.session.rollback()
            flash('Error al actualizar cliente: {}'.format(str(e)))
    
    if request.method == 'GET':
        form.comercial_id.data = cliente.comercial_id or 0
        form.inmueble_id.data = cliente.inmueble_id or 0
        form.interes.data = cliente.interes.split(',') if cliente.interes else []

    # INMUEBLES DE INTERÉS: por rango de precio y tipo
    inmuebles_interes = Inmueble.query.filter(
        Inmueble.precio_min >= (cliente.precio_min or 0),
        Inmueble.precio_max <= (cliente.precio_max or 99999999),
        Inmueble.categoria == cliente.tipo_cliente
    ).all()

    # ACTIVIDAD DEL CLIENTE: registros donde esté implicado
    registros_cliente = Registro.query.outerjoin(Inmueble, Registro.inmueble_id == Inmueble.id).add_entity(Inmueble).filter(Registro.cliente_id == cliente.id).order_by(Registro.fecha.desc()).all()

    return render_template('editar_cliente.html', form=form, cliente=cliente, inmuebles_interes=inmuebles_interes, registros_cliente=registros_cliente)

@app.route('/crear_usuario', methods=['GET', 'POST'])
@login_required
def crear_usuario():
    if not current_user.es_admin:
        flash('No tienes permiso para acceder a esta página.')
        return redirect(url_for('calendario'))
    form = CrearUsuarioForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        usuario = Usuario(nombre=form.nombre.data, password=hashed_password, es_admin=form.es_admin.data)
        db.session.add(usuario)
        try:
            db.session.commit()
            flash('Usuario creado correctamente')
            return redirect(url_for('usuarios'))
        except Exception as e:
            db.session.rollback()
            flash('Error al crear usuario: {}'.format(str(e)))
    return render_template('crear_usuario.html', form=form)

@app.route('/editar_usuario/<int:usuario_id>', methods=['GET', 'POST'])
@login_required
def editar_usuario(usuario_id):
    if not current_user.es_admin:
        flash('No tienes permiso para acceder a esta página.')
        return redirect(url_for('calendario'))
    usuario = Usuario.query.get_or_404(usuario_id)
    form = CrearUsuarioForm(obj=usuario)
    if form.validate_on_submit():
        usuario.nombre = form.nombre.data
        usuario.es_admin = form.es_admin.data
        if form.password.data:
            usuario.password = generate_password_hash(form.password.data)
        try:
            db.session.commit()
            flash('Usuario actualizado correctamente')
            return redirect(url_for('usuarios'))
        except Exception as e:
            db.session.rollback()
            flash('Error al actualizar usuario: {}'.format(str(e)))
    return render_template('editar_usuario.html', form=form, usuario=usuario)

@app.route('/registros')
@login_required
def registros():
    registros = Registro.query.outerjoin(Inmueble, Registro.inmueble_id == Inmueble.id).add_entity(Inmueble).all()
    return render_template('registros.html', registros=registros)

@app.route('/inmuebles')
@login_required
def inmuebles():
    estado = request.args.get('estado')
    if estado:
        inmuebles = Inmueble.query.filter_by(estado=estado).all()
    else:
        inmuebles = Inmueble.query.all()
    return render_template('inmuebles.html', inmuebles=inmuebles)

@app.route('/crear_inmueble', methods=['GET', 'POST'])
@login_required
def crear_inmueble():
    form = CrearInmuebleForm()
    form.visto_por_ids.choices = [(c.id, c.nombre) for c in Cliente.query.all()]
    if form.validate_on_submit():
        inmueble = Inmueble(
            direccion=form.direccion.data,
            descripcion=form.descripcion.data,
            categoria=form.categoria.data,
            precio_min=form.precio_min.data,
            precio_max=form.precio_max.data,
            estado=form.estado.data
        )
        inmueble.visto_por_clientes = Cliente.query.filter(Cliente.id.in_(form.visto_por_ids.data)).all() if form.visto_por_ids.data else []
        db.session.add(inmueble)
        try:
            db.session.commit()
            flash('Inmueble creado correctamente')
            return redirect(url_for('inmuebles'))
        except Exception as e:
            db.session.rollback()
            flash('Error al crear inmueble: {}'.format(str(e)))
    return render_template('crear_inmueble.html', form=form)

@app.route('/editar_inmueble/<int:inmueble_id>', methods=['GET', 'POST'])
@login_required
def editar_inmueble(inmueble_id):
    inmueble = Inmueble.query.get_or_404(inmueble_id)
    form = CrearInmuebleForm(obj=inmueble)
    form.visto_por_ids.choices = [(c.id, c.nombre) for c in Cliente.query.all()]
    if form.validate_on_submit():
        inmueble.direccion = form.direccion.data
        inmueble.descripcion = form.descripcion.data
        inmueble.categoria = form.categoria.data
        inmueble.precio_min = form.precio_min.data
        inmueble.precio_max = form.precio_max.data
        inmueble.estado = form.estado.data
        inmueble.visto_por_clientes = Cliente.query.filter(Cliente.id.in_(form.visto_por_ids.data)).all() if form.visto_por_ids.data else []
        try:
            db.session.commit()
            flash('Inmueble actualizado correctamente')
            return redirect(url_for('inmuebles'))
        except Exception as e:
            db.session.rollback()
            flash('Error al actualizar inmueble: {}'.format(str(e)))
    if request.method == 'GET':
        form.visto_por_ids.data = [c.id for c in inmueble.visto_por_clientes]
    return render_template('editar_inmueble.html', form=form, inmueble=inmueble)

@app.route('/crear_registro', methods=['GET', 'POST'])
@login_required
def crear_registro():
    form = CrearRegistroForm()
    form.usuario_id.choices = [(u.id, u.nombre) for u in Usuario.query.all()]
    form.cliente_id.choices = [(c.id, c.nombre) for c in Cliente.query.all()]
    form.inmueble_id.choices = [(0, 'Sin inmueble')] + [(i.id, i.direccion) for i in Inmueble.query.all()]
    if form.validate_on_submit():
        registro = Registro(
            usuario_id=form.usuario_id.data,
            cliente_id=form.cliente_id.data,
            inmueble_id=form.inmueble_id.data if form.inmueble_id.data != 0 else None,
            fecha=form.fecha.data,
            comentario=form.comentario.data
        )
        db.session.add(registro)
        try:
            db.session.commit()
            flash('Registro creado correctamente')
            return redirect(url_for('registros'))
        except Exception as e:
            db.session.rollback()
            flash('Error al crear registro: {}'.format(str(e)))
    return render_template('crear_registro.html', form=form)

@app.route('/editar_registro/<int:registro_id>', methods=['GET', 'POST'])
@login_required
def editar_registro(registro_id):
    registro = Registro.query.get_or_404(registro_id)
    form = CrearRegistroForm(obj=registro)
    form.usuario_id.choices = [(u.id, u.nombre) for u in Usuario.query.all()]
    form.cliente_id.choices = [(c.id, c.nombre) for c in Cliente.query.all()]
    form.inmueble_id.choices = [(0, 'Sin inmueble')] + [(i.id, i.direccion) for i in Inmueble.query.all()]
    if form.validate_on_submit():
        registro.usuario_id = form.usuario_id.data
        registro.cliente_id = form.cliente_id.data
        registro.inmueble_id = form.inmueble_id.data if form.inmueble_id.data != 0 else None
        registro.fecha = form.fecha.data
        registro.comentario = form.comentario.data
        try:
            db.session.commit()
            flash('Registro actualizado correctamente')
            return redirect(url_for('registros'))
        except Exception as e:
            db.session.rollback()
            flash('Error al actualizar registro: {}'.format(str(e)))
    
    if request.method == 'GET':
        form.inmueble_id.data = registro.inmueble_id or 0

    return render_template('editar_registro.html', form=form, registro=registro)

@app.route('/calendario')
@login_required
def calendario():
    hoy = datetime.date.today()
    dos_semanas = hoy + datetime.timedelta(days=13)
    eventos = Evento.query.filter(Evento.fecha >= hoy, Evento.fecha <= dos_semanas).all()
    return render_template('calendario.html', eventos=eventos, hoy=hoy, dos_semanas=dos_semanas)

@app.route('/eventos')
@login_required
def eventos():
    eventos = Evento.query.order_by(Evento.fecha.asc()).all()
    return render_template('eventos.html', eventos=eventos)

@app.route('/crear_evento', methods=['GET', 'POST'])
@login_required
def crear_evento():
    form = CrearEventoForm()
    form.usuario_id.choices = [(u.id, u.nombre) for u in Usuario.query.all()]
    form.cliente_id.choices = [(c.id, c.nombre) for c in Cliente.query.all()]
    form.inmueble_id.choices = [(0, 'Sin inmueble')] + [(i.id, i.direccion) for i in Inmueble.query.all()]
    if form.validate_on_submit():
        evento = Evento(
            titulo=form.titulo.data,
            fecha=form.fecha.data,
            hora_inicio=form.hora_inicio.data,
            hora_fin=form.hora_fin.data,
            descripcion=form.descripcion.data,
            usuario_id=form.usuario_id.data,
            cliente_id=form.cliente_id.data,
            inmueble_id=form.inmueble_id.data if form.inmueble_id.data != 0 else None
        )
        db.session.add(evento)
        try:
            db.session.commit()
            flash('Evento creado correctamente')
            return redirect(url_for('eventos'))
        except Exception as e:
            db.session.rollback()
            flash('Error al crear evento: {}'.format(str(e)))
    return render_template('crear_evento.html', form=form)

@app.route('/editar_evento/<int:evento_id>', methods=['GET', 'POST'])
@login_required
def editar_evento(evento_id):
    evento = Evento.query.get_or_404(evento_id)
    form = CrearEventoForm(obj=evento)
    form.usuario_id.choices = [(u.id, u.nombre) for u in Usuario.query.all()]
    form.cliente_id.choices = [(c.id, c.nombre) for c in Cliente.query.all()]
    form.inmueble_id.choices = [(0, 'Sin inmueble')] + [(i.id, i.direccion) for i in Inmueble.query.all()]
    if form.validate_on_submit():
        evento.titulo = form.titulo.data
        evento.fecha = form.fecha.data
        evento.hora_inicio = form.hora_inicio.data
        evento.hora_fin = form.hora_fin.data
        evento.descripcion = form.descripcion.data
        evento.usuario_id = form.usuario_id.data
        evento.cliente_id = form.cliente_id.data
        evento.inmueble_id = form.inmueble_id.data if form.inmueble_id.data != 0 else None
        try:
            db.session.commit()
            flash('Evento actualizado correctamente')
            return redirect(url_for('eventos'))
        except Exception as e:
            db.session.rollback()
            flash('Error al actualizar evento: {}'.format(str(e)))

    if request.method == 'GET':
        form.inmueble_id.data = evento.inmueble_id or 0
        
    return render_template('editar_evento.html', form=form, evento=evento)

@app.route('/respuestas_formulario')
@login_required
def respuestas_formulario():
    respuestas = RespuestaFormulario.query.order_by(RespuestaFormulario.fecha.desc()).all()
    clientes_dict = {c.id: c.nombre for c in Cliente.query.all()}
    return render_template('respuestas_formulario.html', respuestas=respuestas, clientes_dict=clientes_dict)

@app.route('/formulario')
def formulario():
    return render_template('formulario.html')

@app.route('/inversores')
@login_required
def inversores():
    estado = request.args.get('estado')
    temperatura = request.args.get('temperatura')
    localidad = request.args.get('localidad')
    query = Cliente.query.filter_by(tipo_cliente='inversor')
    if estado:
        query = query.filter_by(estado=estado)
    if temperatura:
        query = query.filter_by(temperatura=int(temperatura))
    if localidad:
        query = query.filter_by(localidad=localidad)
    clientes = query.all()
    usuarios_dict = {u.id: u.nombre for u in Usuario.query.all()}
    inmuebles_dict = {i.id: i.direccion for i in Inmueble.query.all()}
    return render_template('inversores.html', clientes=clientes, usuarios_dict=usuarios_dict, inmuebles_dict=inmuebles_dict)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 