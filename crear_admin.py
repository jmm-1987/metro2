from app import app, db
from models import Usuario, Cliente, Inmueble, Registro
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

    # Crear inmuebles
    inmuebles = [
        {'direccion': 'Calle Mayor 1', 'descripcion': 'Piso céntrico, reformado, 3 habitaciones', 'categoria': 'vivienda', 'precio_min': 120000, 'precio_max': 130000, 'estado': 'en_venta'},
        {'direccion': 'Avenida del Sol 23', 'descripcion': 'Chalet con jardín y piscina', 'categoria': 'vivienda', 'precio_min': 350000, 'precio_max': 370000, 'estado': 'en_venta'},
        {'direccion': 'Plaza España 5', 'descripcion': 'Ático con terraza y vistas', 'categoria': 'vivienda', 'precio_min': 200000, 'precio_max': 220000, 'estado': 'en_venta'},
        {'direccion': 'Calle Comercio 10', 'descripcion': 'Local comercial en zona céntrica', 'categoria': 'local comercial', 'precio_min': 80000, 'precio_max': 95000, 'estado': 'en_venta'},
        {'direccion': 'Polígono Norte, Parcela 7', 'descripcion': 'Nave industrial con oficinas', 'categoria': 'nave industrial', 'precio_min': 500000, 'precio_max': 550000, 'estado': 'en_venta'}
    ]
    inmueble_objs = []
    for i in inmuebles:
        inmueble = Inmueble.query.filter_by(direccion=i['direccion']).first()
        if not inmueble:
            inmueble = Inmueble(
                direccion=i['direccion'],
                descripcion=i['descripcion'],
                categoria=i['categoria'],
                precio_min=i['precio_min'],
                precio_max=i['precio_max'],
                estado=i['estado']
            )
            db.session.add(inmueble)
        inmueble_objs.append(inmueble)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print('Error al crear inmuebles:', e)

    # Crear clientes con todos los campos y temperaturas distintas
    clientes = [
        {
            'nombre': 'Pedro Martínez', 'email': 'pedro.martinez@example.com', 'telefono': '600000001', 'localidad': 'Madrid',
            'observaciones': 'Cliente interesado en pisos céntricos.', 'tipo_cliente': 'comprador',
            'interes': 'vivienda', 'precio_min': 100000, 'precio_max': 150000, 'temperatura': 1, 'estado': 'en_curso',
            'comercial_id': comercial_objs[0].id if comercial_objs[0] else None, 'inmueble_id': inmueble_objs[0].id if inmueble_objs[0] else None,
            'fecha_creacion': datetime(2024, 5, 1)
        },
        {
            'nombre': 'Juan García', 'email': 'juan.garcia@example.com', 'telefono': '600000002', 'localidad': 'Sevilla',
            'observaciones': 'Busca chalet con piscina.', 'tipo_cliente': 'comprador',
            'interes': 'vivienda', 'precio_min': 300000, 'precio_max': 400000, 'temperatura': 2, 'estado': 'en_curso',
            'comercial_id': comercial_objs[1].id if comercial_objs[1] else None, 'inmueble_id': inmueble_objs[1].id if inmueble_objs[1] else None,
            'fecha_creacion': datetime(2024, 5, 2)
        },
        {
            'nombre': 'Antonia Ruiz', 'email': 'antonia.ruiz@example.com', 'telefono': '600000003', 'localidad': 'Valencia',
            'observaciones': 'Quiere ático con terraza.', 'tipo_cliente': 'comprador',
            'interes': 'vivienda', 'precio_min': 180000, 'precio_max': 230000, 'temperatura': 3, 'estado': 'en_curso',
            'comercial_id': comercial_objs[2].id if comercial_objs[2] else None, 'inmueble_id': inmueble_objs[2].id if inmueble_objs[2] else None,
            'fecha_creacion': datetime(2024, 5, 3)
        },
        {
            'nombre': 'Juana Torres', 'email': 'juana.torres@example.com', 'telefono': '600000004', 'localidad': 'Barcelona',
            'observaciones': 'Busca local comercial para negocio.', 'tipo_cliente': 'inversor',
            'interes': 'local comercial', 'precio_min': 70000, 'precio_max': 100000, 'temperatura': 4, 'estado': 'en_curso',
            'comercial_id': comercial_objs[3].id if comercial_objs[3] else None, 'inmueble_id': inmueble_objs[3].id if inmueble_objs[3] else None,
            'fecha_creacion': datetime(2024, 5, 4)
        },
        {
            'nombre': 'Federica López', 'email': 'federica.lopez@example.com', 'telefono': '600000005', 'localidad': 'Bilbao',
            'observaciones': 'Interesada en nave industrial.', 'tipo_cliente': 'arrendatario',
            'interes': 'nave industrial', 'precio_min': 450000, 'precio_max': 600000, 'temperatura': 5, 'estado': 'en_curso',
            'comercial_id': comercial_objs[0].id if comercial_objs[0] else None, 'inmueble_id': inmueble_objs[4].id if inmueble_objs[4] else None,
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
                temperatura=c['temperatura'],
                estado=c['estado'],
                comercial_id=c['comercial_id'],
                inmueble_id=c['inmueble_id'],
                fecha_creacion=c['fecha_creacion']
            )
            db.session.add(cliente)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print('Error al crear clientes:', e)

    # Crear registros de ejemplo (relacionando clientes, inmuebles y comerciales)
    clientes_db = Cliente.query.all()
    inmuebles_db = Inmueble.query.all()
    usuarios_db = Usuario.query.all()
    registros = [
        {'usuario_id': usuarios_db[1].id, 'cliente_id': clientes_db[0].id, 'inmueble_id': inmuebles_db[0].id, 'fecha': date(2024, 5, 10), 'comentario': 'Primera visita al piso céntrico.'},
        {'usuario_id': usuarios_db[2].id, 'cliente_id': clientes_db[1].id, 'inmueble_id': inmuebles_db[1].id, 'fecha': date(2024, 5, 12), 'comentario': 'Visita al chalet con piscina.'},
        {'usuario_id': usuarios_db[3].id, 'cliente_id': clientes_db[2].id, 'inmueble_id': inmuebles_db[2].id, 'fecha': date(2024, 5, 15), 'comentario': 'Visita al ático con terraza.'},
        {'usuario_id': usuarios_db[2].id, 'cliente_id': clientes_db[3].id, 'inmueble_id': inmuebles_db[3].id, 'fecha': date(2024, 5, 18), 'comentario': 'Visita al local comercial.'},
        {'usuario_id': usuarios_db[1].id, 'cliente_id': clientes_db[4].id, 'inmueble_id': inmuebles_db[4].id, 'fecha': date(2024, 5, 20), 'comentario': 'Visita a la nave industrial.'}
    ]
    for r in registros:
        db.session.add(Registro(**r))
    try:
        db.session.commit()
        print('Comerciales, clientes, inmuebles y registros de ejemplo creados.')
    except Exception as e:
        db.session.rollback()
        print('Error al crear registros:', e) 