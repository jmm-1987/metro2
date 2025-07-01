from app import app, db
from models import Usuario, Cliente
from werkzeug.security import generate_password_hash
from datetime import datetime

with app.app_context():
    # Crear usuario root
    if not Usuario.query.filter_by(nombre='root').first():
        root = Usuario(nombre='root', password=generate_password_hash('7GMZ%elA'), es_admin=True, activo=True)
        db.session.add(root)
        try:
            db.session.commit()
            print('Usuario root creado: root / 7GMZ%elA')
        except Exception as e:
            db.session.rollback()
            print('Error al crear usuario root:', e)
    else:
        print('El usuario root ya existe.')

    # Crear dos clientes de prueba con todos los campos
    clientes = [
        {
            'nombre': 'Ana López', 'email': 'ana.lopez@example.com', 'telefono': '600000010', 'localidad': 'Madrid',
            'observaciones': 'Busca piso céntrico con terraza.', 'tipo_cliente': 'comprador',
            'interes': 'vivienda,local comercial', 'zonas': 'centro,norte', 'precio_min': 120000, 'precio_max': 200000, 'estado': 'en_curso',
            'comercial_id': None, 'fecha_creacion': datetime(2024, 6, 1), 'encuesta_enviada': True, 'activo': True
        },
        {
            'nombre': 'Carlos Pérez', 'email': 'carlos.perez@example.com', 'telefono': '600000011', 'localidad': 'Valencia',
            'observaciones': 'Interesado en nave industrial y terreno.', 'tipo_cliente': 'inversor',
            'interes': 'nave industrial,terreno', 'zonas': 'sur,este', 'precio_min': 300000, 'precio_max': 500000, 'estado': 'en_curso',
            'comercial_id': None, 'fecha_creacion': datetime(2024, 6, 2), 'encuesta_enviada': False, 'activo': True
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
                zonas=c['zonas'],
                precio_min=c['precio_min'],
                precio_max=c['precio_max'],
                estado=c['estado'],
                comercial_id=c['comercial_id'],
                fecha_creacion=c['fecha_creacion'],
                encuesta_enviada=c['encuesta_enviada'],
                activo=c['activo']
            )
            db.session.add(cliente)
    try:
        db.session.commit()
        print('Clientes de ejemplo creados.')
    except Exception as e:
        db.session.rollback()
        print('Error al crear clientes:', e) 