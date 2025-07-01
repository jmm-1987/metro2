from app import app, db
from models import Usuario, Cliente, Tarea
from werkzeug.security import generate_password_hash
from datetime import datetime, date

with app.app_context():
    # Crear admin
    if not Usuario.query.filter_by(nombre='Administrador Principal').first():
        admin = Usuario(nombre='Administrador Principal', password=generate_password_hash('admin123'), es_admin=True)
        db.session.add(admin)
        try:
            db.session.commit()
            print('Usuario administrador creado: Administrador Principal / admin123')
        except Exception as e:
            db.session.rollback()
            print('Error al crear usuario administrador:', e)
    else:
        print('El usuario Administrador Principal ya existe.')

    # Crear usuario 1 con contraseña 1 (admin)
    if not Usuario.query.filter_by(nombre='1').first():
        user1 = Usuario(nombre='1', password=generate_password_hash('1'), es_admin=True)
        db.session.add(user1)
        try:
            db.session.commit()
            print('Usuario 1 creado: 1 / 1')
        except Exception as e:
            db.session.rollback()
            print('Error al crear usuario 1:', e)
    else:
        print('El usuario 1 ya existe.')

    # Crear comerciales
    comerciales = [
        {'nombre': 'Raúl García', 'password': 'raul123'},
        {'nombre': 'Sergio López', 'password': 'sergio123'},
        {'nombre': 'Marta Ruiz', 'password': 'marta123'},
        {'nombre': 'Lucía Torres', 'password': 'lucia123'}
    ]
    comercial_objs = []
    for c in comerciales:
        user = Usuario.query.filter_by(nombre=c['nombre']).first()
        if not user:
            user = Usuario(nombre=c['nombre'], password=generate_password_hash(c['password']), es_admin=False)
            db.session.add(user)
        comercial_objs.append(user)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print('Error al crear comerciales:', e)

    # Crear clientes con todos los campos y temperaturas distintas
    clientes = [
        {
            'nombre': 'Pedro Martínez', 'email': 'pedro.martinez@example.com', 'telefono': '600000001', 'localidad': 'Madrid',
            'observaciones': 'Cliente interesado en pisos céntricos.', 'tipo_cliente': 'comprador',
            'interes': 'vivienda', 'precio_min': 100000, 'precio_max': 150000, 'estado': 'en_curso',
            'comercial_id': comercial_objs[0].id if comercial_objs[0] else None,
            'fecha_creacion': datetime(2024, 5, 1)
        },
        {
            'nombre': 'Juan García', 'email': 'juan.garcia@example.com', 'telefono': '600000002', 'localidad': 'Sevilla',
            'observaciones': 'Busca chalet con piscina.', 'tipo_cliente': 'comprador',
            'interes': 'vivienda', 'precio_min': 300000, 'precio_max': 400000, 'estado': 'en_curso',
            'comercial_id': comercial_objs[1].id if comercial_objs[1] else None,
            'fecha_creacion': datetime(2024, 5, 2)
        },
        {
            'nombre': 'Antonia Ruiz', 'email': 'antonia.ruiz@example.com', 'telefono': '600000003', 'localidad': 'Valencia',
            'observaciones': 'Quiere ático con terraza.', 'tipo_cliente': 'comprador',
            'interes': 'vivienda', 'precio_min': 180000, 'precio_max': 230000, 'estado': 'en_curso',
            'comercial_id': comercial_objs[2].id if comercial_objs[2] else None,
            'fecha_creacion': datetime(2024, 5, 3)
        },
        {
            'nombre': 'Juana Torres', 'email': 'juana.torres@example.com', 'telefono': '600000004', 'localidad': 'Barcelona',
            'observaciones': 'Busca local comercial para negocio.', 'tipo_cliente': 'inversor',
            'interes': 'local comercial', 'precio_min': 70000, 'precio_max': 100000, 'estado': 'en_curso',
            'comercial_id': comercial_objs[3].id if comercial_objs[3] else None,
            'fecha_creacion': datetime(2024, 5, 4)
        },
        {
            'nombre': 'Federica López', 'email': 'federica.lopez@example.com', 'telefono': '600000005', 'localidad': 'Bilbao',
            'observaciones': 'Interesada en nave industrial.', 'tipo_cliente': 'arrendatario',
            'interes': 'nave industrial', 'precio_min': 450000, 'precio_max': 600000, 'estado': 'en_curso',
            'comercial_id': comercial_objs[0].id if comercial_objs[0] else None,
            'fecha_creacion': datetime(2024, 5, 5)
        }
    ]
    for c in clientes:
        if not Cliente.query.filter_by(nombre=c['nombre']).first():
            cliente = Cliente(
                nombre=c['nombre'],
                email=c['email'],
                telefono=c['telefono'],
                localidad=c['localidad'],
                observaciones=c['observaciones'],
                tipo_cliente=c['tipo_cliente'],
                interes=c['interes'],
                precio_min=c['precio_min'],
                precio_max=c['precio_max'],
                estado=c['estado'],
                comercial_id=c['comercial_id'],
                fecha_creacion=c['fecha_creacion']
            )
            db.session.add(cliente)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print('Error al crear clientes:', e)

    # Crear tareas de ejemplo (relacionando clientes y comerciales)
    clientes_db = Cliente.query.all()
    usuarios_db = Usuario.query.all()
    tareas = [
        {'usuario_id': usuarios_db[1].id, 'cliente_id': clientes_db[0].id, 'fecha': date(2024, 5, 10), 'comentario': 'Primera visita.'},
        {'usuario_id': usuarios_db[2].id, 'cliente_id': clientes_db[1].id, 'fecha': date(2024, 5, 12), 'comentario': 'Segunda visita.'},
        {'usuario_id': usuarios_db[3].id, 'cliente_id': clientes_db[2].id, 'fecha': date(2024, 5, 15), 'comentario': 'Tercera visita.'},
        {'usuario_id': usuarios_db[2].id, 'cliente_id': clientes_db[3].id, 'fecha': date(2024, 5, 18), 'comentario': 'Visita especial.'},
        {'usuario_id': usuarios_db[1].id, 'cliente_id': clientes_db[4].id, 'fecha': date(2024, 5, 20), 'comentario': 'Visita final.'}
    ]
    for t in tareas:
        db.session.add(Tarea(**t))
    try:
        db.session.commit()
        print('Comerciales, clientes y tareas de ejemplo creados.')
    except Exception as e:
        db.session.rollback()
        print('Error al crear tareas:', e) 