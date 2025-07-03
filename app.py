from flask import Flask, render_template, redirect, url_for, request, flash, jsonify, make_response, send_file
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import joinedload
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from sqlalchemy import or_
from werkzeug.security import generate_password_hash, check_password_hash
from forms import LoginForm, CrearUsuarioForm, CrearClienteForm, CrearTareaForm, CrearEventoForm, ResolverTareaForm
from wtforms import StringField, DateField, SelectField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
import datetime
import smtplib
from email.message import EmailMessage
from models import db, Usuario, Cliente, Tarea, Evento, RespuestaFormulario

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cambia_esto_por_un_valor_seguro'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

from models import db, Usuario, Cliente, Tarea, Evento
db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

@app.route('/')
@login_required
def dashboard():
    tareas = Tarea.query.options(
        joinedload(Tarea.usuario),
        joinedload(Tarea.cliente)
    ).order_by(Tarea.fecha.asc(), Tarea.hora.asc()).all()

    tareas_por_hacer = [t for t in tareas if t.estado == 'por_hacer']
    tareas_resueltas = [t for t in tareas if t.estado in ['pendiente', 'cancelado', 'reagendada']]

    clientes_list = Cliente.query.filter_by(estado='en_curso').order_by(Cliente.nombre.asc()).limit(15).all()
    now = datetime.datetime.now()
    return render_template('dashboard.html', tareas_por_hacer=tareas_por_hacer, tareas_resueltas=tareas_resueltas, clientes_list=clientes_list, now=now, es_admin=current_user.es_admin)

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

@app.route('/buscar_clientes')
@login_required
def buscar_clientes():
    search = request.args.get('q')
    if search:
        clientes = Cliente.query.filter(
            or_(
                Cliente.nombre.like(f'%{search}%'),
                Cliente.telefono.like(f'%{search}%')
            )
        ).all()
    else:
        clientes = []
    return jsonify([{'id': c.id, 'text': f'{c.nombre} ({c.telefono})'} for c in clientes])

@app.route('/clientes')
@login_required
def clientes():
    estado = request.args.get('estado')
    tipo_cliente = request.args.get('tipo_cliente')
    interes = request.args.get('interes')
    mostrar_inactivos = request.args.get('inactivos') == '1'
    query = Cliente.query
    if not mostrar_inactivos:
        query = query.filter_by(activo=True)
    if estado:
        query = query.filter_by(estado=estado)
    if tipo_cliente:
        query = query.filter_by(tipo_cliente=tipo_cliente)
    if interes:
        query = query.filter(Cliente.interes != None).filter(Cliente.interes.like(f"%{interes}%"))
    clientes = query.all()
    # Ordenar por fecha y hora de la última tarea (más reciente primero)
    from datetime import datetime, time
    def fecha_hora_ultima_tarea(cliente):
        if cliente.tareas:
            return max((datetime.combine(t.fecha, t.hora or time.min) for t in cliente.tareas if t.fecha), default=None)
        return None
    clientes.sort(key=lambda c: fecha_hora_ultima_tarea(c) or datetime.min, reverse=True)
    usuarios_dict = {u.id: u.nombre for u in Usuario.query.all()}
    return render_template('clientes.html', clientes=clientes, usuarios_dict=usuarios_dict)

@app.route('/usuarios')
@login_required
def usuarios():
    if not current_user.es_admin:
        flash('No tienes permiso para acceder a esta página.')
        return redirect(url_for('calendario'))
    mostrar_inactivos = request.args.get('inactivos') == '1'
    query = Usuario.query
    if not mostrar_inactivos:
        query = query.filter_by(activo=True)
    usuarios = query.all()
    return render_template('usuarios.html', usuarios=usuarios)

@app.route('/crear_cliente', methods=['GET', 'POST'])
@login_required
def crear_cliente():
    form = CrearClienteForm()
    form.comercial_id.choices = [(0, 'Sin comercial')] + [(u.id, u.nombre) for u in Usuario.query.all()]
    if request.method == 'GET' and not form.fecha_creacion.data:
        form.fecha_creacion.data = datetime.date.today()
    if form.validate_on_submit():
        cliente = Cliente(
            nombre=form.nombre.data,
            email=form.email.data or None,
            telefono=form.telefono.data,
            localidad=form.localidad.data,
            observaciones=form.observaciones.data or None,
            tipo_cliente=form.tipo_cliente.data or None,
            interes=','.join(form.interes.data) if form.interes.data else None,
            zonas=','.join(form.zonas.data) if form.zonas.data else None,
            precio_min=form.precio_min.data if form.precio_min.data else None,
            precio_max=form.precio_max.data if form.precio_max.data else None,
            estado=form.estado.data,
            comercial_id=form.comercial_id.data if form.comercial_id.data != 0 else None,
            fecha_creacion=form.fecha_creacion.data or datetime.date.today()
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
    if request.method == 'GET':
        form.comercial_id.data = cliente.comercial_id or 0
        form.interes.data = cliente.interes.split(',') if cliente.interes else []
        form.zonas.data = cliente.zonas.split(',') if cliente.zonas else []
    tareas_cliente = cliente.tareas if hasattr(cliente, 'tareas') else []
    if form.validate_on_submit():
        cliente.nombre = form.nombre.data
        cliente.email = form.email.data or None
        cliente.telefono = form.telefono.data
        cliente.localidad = form.localidad.data
        cliente.observaciones = form.observaciones.data or None
        cliente.tipo_cliente = form.tipo_cliente.data or None
        cliente.interes = ','.join(form.interes.data) if form.interes.data else None
        cliente.zonas = ','.join(form.zonas.data) if form.zonas.data else None
        cliente.precio_min = form.precio_min.data if form.precio_min.data else None
        cliente.precio_max = form.precio_max.data if form.precio_max.data else None
        cliente.estado = form.estado.data
        cliente.comercial_id = form.comercial_id.data if form.comercial_id.data != 0 else None
        try:
            db.session.commit()
            flash('Cliente actualizado correctamente')
            return redirect(url_for('clientes'))
        except Exception as e:
            db.session.rollback()
            flash('Error al actualizar cliente: {}'.format(str(e)))
    return render_template('editar_cliente.html', form=form, cliente=cliente, tareas_cliente=tareas_cliente)

@app.route('/crear_usuario', methods=['GET', 'POST'])
@login_required
def crear_usuario():
    if not current_user.es_admin:
        flash('No tienes permiso para acceder a esta página.')
        return redirect(url_for('calendario'))
    form = CrearUsuarioForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        usuario = Usuario(nombre=form.nombre.data, password=hashed_password, es_admin=form.es_admin.data, color=form.color.data)
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
    usuario = Usuario.query.get_or_404(usuario_id)
    # Solo el propio root puede editarse
    if usuario.nombre == 'root' and current_user.nombre != 'root':
        flash('Solo el usuario root puede editarse a sí mismo.')
        return redirect(url_for('usuarios'))
    if not current_user.es_admin:
        flash('No tienes permiso para acceder a esta página.')
        return redirect(url_for('calendario'))
    usuario.email = usuario.email or ""
    usuario.telefono = usuario.telefono or ""
    form = CrearUsuarioForm(obj=usuario)
    if form.validate_on_submit():
        usuario.nombre = form.nombre.data
        usuario.es_admin = form.es_admin.data
        usuario.color = form.color.data
        usuario.email = form.email.data
        usuario.telefono = form.telefono.data
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
    registros = Tarea.query.all()
    return render_template('registros.html', registros=registros)

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

@app.route('/crear_tarea', methods=['GET', 'POST'])
@login_required
def crear_tarea():
    form = CrearTareaForm()
    form.usuario_id.choices = [(u.id, u.nombre) for u in Usuario.query.all()]
    if request.method == 'GET':
        usuario_id = request.args.get('usuario_id', type=int)
        cliente_id = request.args.get('cliente_id', type=int)
        if current_user.nombre == 'Nazaret':
            raul = Usuario.query.filter_by(nombre='Raul').first()
            form.usuario_id.data = raul.id if raul else current_user.id
        else:
            form.usuario_id.data = usuario_id if usuario_id else current_user.id
        if cliente_id:
            cliente = Cliente.query.get(cliente_id)
            if cliente:
                form.cliente_id.data = cliente.id
                form.cliente_nombre.data = f"{cliente.nombre} ({cliente.telefono})"
    if form.validate_on_submit():
        # Convertir la hora de string a objeto time
        hora_obj = datetime.datetime.strptime(form.hora.data, "%H:%M").time()
        tarea = Tarea(
            usuario_id=form.usuario_id.data,
            cliente_id=form.cliente_id.data if form.cliente_id.data else None,
            fecha=form.fecha.data,
            hora=hora_obj,
            comentario=form.comentario.data,
            resolucion=form.resolucion.data,
            estado=form.estado.data
        )
        db.session.add(tarea)
        try:
            db.session.commit()
            flash('Tarea creada correctamente')
            return redirect(url_for('dashboard'))
        except Exception as e:
            db.session.rollback()
            flash('Error al crear tarea: {}'.format(str(e)))
    return render_template('crear_tarea.html', form=form)

@app.route('/editar_tarea/<int:tarea_id>', methods=['GET', 'POST'])
@login_required
def editar_tarea(tarea_id):
    tarea = Tarea.query.get_or_404(tarea_id)
    form = ResolverTareaForm(obj=tarea)
    form.usuario_id.choices = [(u.id, u.nombre) for u in Usuario.query.all()]

    if request.method == 'GET':
        # Populate form with existing data
        form.usuario_id.data = tarea.usuario_id
        if tarea.cliente:
            form.cliente_nombre.data = f"{tarea.cliente.nombre} ({tarea.cliente.telefono})"
            form.cliente_id.data = tarea.cliente_id
            form.estado.data = tarea.estado

    # Ocultar el select de estado en el template (solo usarlo para POST)
    form.estado.render_kw = {'style': 'display:none;'}

    if form.validate_on_submit():
        tarea.resolucion = form.resolucion.data
        # Si el usuario ha pulsado un botón de estado, usar ese valor
        estado_post = request.form.get('estado')
        if estado_post:
            tarea.estado = estado_post
        else:
            tarea.estado = form.estado.data

        # Modificar el estado del cliente según la acción
        if tarea.cliente:
            if tarea.estado == 'reagendada':
                tarea.cliente.estado = 'en_curso'
            elif tarea.estado == 'pendiente':
                tarea.cliente.estado = 'pendiente'
            elif tarea.estado == 'cancelado':
                tarea.cliente.estado = 'finalizado'
                tarea.cliente.activo = False

        try:
            db.session.commit()
            # Solo redirigir a crear_tarea si es reagendada y reagendar=1
            if tarea.estado == 'reagendada' and request.args.get('reagendar') == '1':
                return redirect(url_for('crear_tarea', cliente_id=tarea.cliente_id, usuario_id=tarea.usuario_id))
            # Para otros estados, simplemente redirigir al dashboard
            flash('Resolución de la tarea actualizada correctamente.')
            return redirect(url_for('dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar la tarea: {e}')
    return render_template('editar_tarea.html', form=form, tarea=tarea)

@app.route('/api/events')
@login_required
def api_events():
    start_str = request.args.get('start')
    end_str = request.args.get('end')
    mostrar_resueltas = request.args.get('mostrar_resueltas') == '1'

    start_date = datetime.datetime.fromisoformat(start_str.split('T')[0]).date()
    end_date = datetime.datetime.fromisoformat(end_str.split('T')[0]).date()

    events = []

    # Encabezado para la vista diaria
    if (end_date - start_date).days <= 1:
        events.append({
            'id': 'header',
            'title': 'ENCABEZADO',
            'start': datetime.datetime.combine(start_date, datetime.time.min).isoformat(),
            'backgroundColor': '#f8f9fa',
            'borderColor': '#dee2e6',
            'editable': False,
            'allDay': True,
            'extendedProps': {
                'isHeader': True
            }
        })

    # Get Tareas
    tareas = Tarea.query.filter(Tarea.fecha >= start_date, Tarea.fecha < end_date).all()
    tareas_por_hacer = [t for t in tareas if t.estado == 'por_hacer']
    tareas_resueltas = [t for t in tareas if t.estado in ['pendiente', 'cancelado', 'reagendada']]

    # Mostrar primero las por hacer
    for tarea in tareas_por_hacer:
        event_start = datetime.datetime.combine(tarea.fecha, tarea.hora if tarea.hora else datetime.time.min)
        events.append({
            'title': tarea.comentario or 'Sin descripción',
            'start': event_start.isoformat(),
            'url': url_for('editar_tarea', tarea_id=tarea.id),
            'backgroundColor': tarea.usuario.color if tarea.usuario else '#6c757d',
            'borderColor': tarea.usuario.color if tarea.usuario else '#6c757d',
            'extendedProps': {
                'comercial': tarea.usuario.nombre if tarea.usuario else '',
                'cliente': tarea.cliente.nombre if tarea.cliente else '',
                'telefono': tarea.cliente.telefono if tarea.cliente and tarea.cliente.telefono else '',
                'estado': 'Por hacer',
                'isHeader': False
            }
        })

    # Si se piden resueltas, añadir separador y luego las resueltas
    if mostrar_resueltas and tareas_resueltas:
        for tarea in tareas_resueltas:
            event_start = datetime.datetime.combine(tarea.fecha, tarea.hora if tarea.hora else datetime.time.min)
            events.append({
                'title': tarea.comentario or 'Sin descripción',
                'start': event_start.isoformat(),
                'url': url_for('editar_tarea', tarea_id=tarea.id),
                'backgroundColor': tarea.usuario.color if tarea.usuario else '#6c757d',
                'borderColor': tarea.usuario.color if tarea.usuario else '#6c757d',
                'extendedProps': {
                    'comercial': tarea.usuario.nombre if tarea.usuario else '',
                    'cliente': tarea.cliente.nombre if tarea.cliente else '',
                    'telefono': tarea.cliente.telefono if tarea.cliente and tarea.cliente.telefono else '',
                    'estado': 'Ha comprado' if tarea.estado == 'ha_comprado' else (
                        'Ha alquilado' if tarea.estado == 'ha_alquilado' else (
                        'Cancelado' if tarea.estado == 'cancelado' else tarea.estado)),
                    'isHeader': False
                }
            })

    # Get Eventos
    eventos_db = Evento.query.filter(Evento.fecha >= start_date, Evento.fecha < end_date).all()
    for evento in eventos_db:
        start_time = evento.hora_inicio or datetime.time.min
        end_time = evento.hora_fin or datetime.time.max
        
        event_start = datetime.datetime.combine(evento.fecha, start_time)
        event_end = datetime.datetime.combine(evento.fecha, end_time)

        events.append({
            'title': evento.titulo,
            'start': event_start.isoformat(),
            'end': event_end.isoformat(),
            'url': url_for('editar_evento', evento_id=evento.id),
            'backgroundColor': evento.usuario.color if evento.usuario else '#6c757d',
            'borderColor': evento.usuario.color if evento.usuario else '#6c757d',
            'extendedProps': {
                'comercial': evento.usuario.nombre if evento.usuario else '',
                'cliente': evento.cliente.nombre if evento.cliente else ''
            }
        })
        
    return jsonify(events)

@app.route('/editar_evento/<int:evento_id>', methods=['GET', 'POST'])
@login_required
def editar_evento(evento_id):
    evento = Evento.query.get_or_404(evento_id)
    form = CrearEventoForm(obj=evento)
    form.usuario_id.choices = [(u.id, u.nombre) for u in Usuario.query.all()]
    form.cliente_id.choices = [(c.id, c.nombre) for c in Cliente.query.all()]
    if form.validate_on_submit():
        evento.titulo = form.titulo.data
        evento.fecha = form.fecha.data
        evento.hora_inicio = form.hora_inicio.data
        evento.hora_fin = form.hora_fin.data
        evento.descripcion = form.descripcion.data
        evento.usuario_id = form.usuario_id.data
        evento.cliente_id = form.cliente_id.data
        try:
            db.session.commit()
            flash('Evento actualizado correctamente')
            return redirect(url_for('eventos'))
        except Exception as e:
            db.session.rollback()
            flash('Error al actualizar evento: {}'.format(str(e)))

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
    # Mostrar todos los clientes en curso o standby, sin importar tipo_cliente
    clientes = Cliente.query.filter(Cliente.estado.in_(['en_curso', 'pendiente'])).all()
    usuarios_dict = {u.id: u.nombre for u in Usuario.query.all()}
    return render_template('inversores.html', clientes=clientes, usuarios_dict=usuarios_dict)

@app.route('/eliminar_tarea/<int:tarea_id>', methods=['POST'])
@login_required
def eliminar_tarea(tarea_id):
    tarea = Tarea.query.get_or_404(tarea_id)
    try:
        db.session.delete(tarea)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/crear_cliente_rapido', methods=['POST'])
@login_required
def crear_cliente_rapido():
    data = request.get_json()
    nombre = data.get('nombre', '').strip()
    localidad = data.get('localidad', '').strip()
    telefono = data.get('telefono', '').strip()
    if not nombre or not localidad or not telefono:
        return jsonify({'success': False, 'error': 'Todos los campos son obligatorios'}), 400
    # Comprobar si el teléfono ya existe
    if Cliente.query.filter_by(telefono=telefono).first():
        return jsonify({'success': False, 'error': 'Ya existe un cliente con ese teléfono'}), 400
    cliente = Cliente(nombre=nombre, localidad=localidad, telefono=telefono)
    db.session.add(cliente)
    try:
        db.session.commit()
        return jsonify({'success': True, 'cliente_id': cliente.id, 'cliente_texto': f"{cliente.nombre} ({cliente.telefono})"})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/toggle_usuario/<int:usuario_id>', methods=['POST'])
@login_required
def toggle_usuario(usuario_id):
    usuario = Usuario.query.get_or_404(usuario_id)
    # Solo el propio root puede desactivarse
    if usuario.nombre == 'root' and current_user.nombre != 'root':
        flash('Solo el usuario root puede desactivarse a sí mismo.')
        return redirect(url_for('usuarios'))
    if not current_user.es_admin:
        flash('No tienes permiso para realizar esta acción.')
        return redirect(url_for('usuarios'))
    usuario.activo = not usuario.activo
    try:
        db.session.commit()
        flash(f"Usuario {'activado' if usuario.activo else 'desactivado'} correctamente.")
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar usuario: {e}')
    return redirect(url_for('usuarios'))

@app.route('/toggle_cliente/<int:cliente_id>', methods=['POST'])
@login_required
def toggle_cliente(cliente_id):
    cliente = Cliente.query.get_or_404(cliente_id)
    cliente.activo = not cliente.activo
    try:
        db.session.commit()
        flash(f"Cliente {'activado' if cliente.activo else 'desactivado'} correctamente.")
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar cliente: {e}')
    return redirect(url_for('clientes'))

@app.route('/descargar_db')
@login_required
def descargar_db():
    if not current_user.es_admin:
        flash('No tienes permiso para descargar la base de datos.')
        return redirect(url_for('dashboard'))
    return send_file(
        'instance/database.db',
        as_attachment=True,
        download_name='metro2.db'
    )

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 