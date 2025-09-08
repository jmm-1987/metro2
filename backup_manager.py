import csv
import io
import os
from datetime import datetime
from models import db, Usuario, Cliente, Tarea, Evento, RespuestaFormulario
from werkzeug.security import generate_password_hash

def export_database_to_csv():
    """
    Exporta toda la base de datos a archivos CSV
    Retorna un diccionario con los archivos CSV como strings
    """
    csv_data = {}
    
    # Exportar Usuarios
    usuarios_csv = io.StringIO()
    usuarios_writer = csv.writer(usuarios_csv)
    usuarios_writer.writerow(['id', 'nombre', 'password', 'es_admin', 'color', 'email', 'telefono', 
                             'activo', 'notificar_email', 'notificar_telegram', 'chat_id_telegram'])
    
    for usuario in Usuario.query.all():
        usuarios_writer.writerow([
            usuario.id,
            usuario.nombre,
            usuario.password,  # Exportamos el hash, no la contraseña original
            usuario.es_admin,
            usuario.color,
            usuario.email,
            usuario.telefono,
            usuario.activo,
            usuario.notificar_email,
            usuario.notificar_telegram,
            usuario.chat_id_telegram
        ])
    
    csv_data['usuarios'] = usuarios_csv.getvalue()
    usuarios_csv.close()
    
    # Exportar Clientes
    clientes_csv = io.StringIO()
    clientes_writer = csv.writer(clientes_csv)
    clientes_writer.writerow(['id', 'nombre', 'email', 'telefono', 'estado', 'localidad', 'observaciones',
                             'tipo_cliente', 'interes', 'zonas', 'precio_min', 'precio_max', 'encuesta_enviada',
                             'comercial_id', 'fecha_creacion', 'fecha_modificacion', 'activo', 'visto_por'])
    
    for cliente in Cliente.query.all():
        clientes_writer.writerow([
            cliente.id,
            cliente.nombre,
            cliente.email,
            cliente.telefono,
            cliente.estado,
            cliente.localidad,
            cliente.observaciones,
            cliente.tipo_cliente,
            cliente.interes,
            cliente.zonas,
            cliente.precio_min,
            cliente.precio_max,
            cliente.encuesta_enviada,
            cliente.comercial_id,
            cliente.fecha_creacion.isoformat() if cliente.fecha_creacion else '',
            cliente.fecha_modificacion.isoformat() if cliente.fecha_modificacion else '',
            cliente.activo,
            cliente.visto_por
        ])
    
    csv_data['clientes'] = clientes_csv.getvalue()
    clientes_csv.close()
    
    # Exportar Tareas
    tareas_csv = io.StringIO()
    tareas_writer = csv.writer(tareas_csv)
    tareas_writer.writerow(['id', 'usuario_id', 'cliente_id', 'fecha', 'hora', 'comentario', 
                           'resolucion', 'estado', 'google_event_id'])
    
    for tarea in Tarea.query.all():
        tareas_writer.writerow([
            tarea.id,
            tarea.usuario_id,
            tarea.cliente_id,
            tarea.fecha.isoformat() if tarea.fecha else '',
            tarea.hora.isoformat() if tarea.hora else '',
            tarea.comentario,
            tarea.resolucion,
            tarea.estado,
            tarea.google_event_id
        ])
    
    csv_data['tareas'] = tareas_csv.getvalue()
    tareas_csv.close()
    
    # Exportar Eventos
    eventos_csv = io.StringIO()
    eventos_writer = csv.writer(eventos_csv)
    eventos_writer.writerow(['id', 'titulo', 'descripcion', 'fecha', 'hora_inicio', 'hora_fin', 
                            'usuario_id', 'cliente_id'])
    
    for evento in Evento.query.all():
        eventos_writer.writerow([
            evento.id,
            evento.titulo,
            evento.descripcion,
            evento.fecha.isoformat() if evento.fecha else '',
            evento.hora_inicio.isoformat() if evento.hora_inicio else '',
            evento.hora_fin.isoformat() if evento.hora_fin else '',
            evento.usuario_id,
            evento.cliente_id
        ])
    
    csv_data['eventos'] = eventos_csv.getvalue()
    eventos_csv.close()
    
    # Exportar Respuestas de Formulario
    respuestas_csv = io.StringIO()
    respuestas_writer = csv.writer(respuestas_csv)
    respuestas_writer.writerow(['id', 'cliente_id', 'puntuacion1', 'puntuacion2', 'puntuacion_media', 
                               'sugerencias', 'fecha'])
    
    for respuesta in RespuestaFormulario.query.all():
        respuestas_writer.writerow([
            respuesta.id,
            respuesta.cliente_id,
            respuesta.puntuacion1,
            respuesta.puntuacion2,
            respuesta.puntuacion_media,
            respuesta.sugerencias,
            respuesta.fecha.isoformat() if respuesta.fecha else ''
        ])
    
    csv_data['respuestas_formulario'] = respuestas_csv.getvalue()
    respuestas_csv.close()
    
    return csv_data

def import_database_from_csv(csv_files):
    """
    Importa datos desde archivos CSV a la base de datos
    csv_files: diccionario con los datos CSV
    """
    try:
        # Limpiar tablas existentes (en orden correcto por las foreign keys)
        RespuestaFormulario.query.delete()
        Tarea.query.delete()
        Evento.query.delete()
        Cliente.query.delete()
        Usuario.query.delete()
        
        # Importar Usuarios
        if 'usuarios' in csv_files:
            usuarios_reader = csv.DictReader(io.StringIO(csv_files['usuarios']))
            for row in usuarios_reader:
                usuario = Usuario(
                    id=int(row['id']) if row['id'] else None,
                    nombre=row['nombre'],
                    password=row['password'],  # Mantenemos el hash
                    es_admin=row['es_admin'].lower() == 'true',
                    color=row['color'],
                    email=row['email'] if row['email'] else None,
                    telefono=row['telefono'] if row['telefono'] else None,
                    activo=row['activo'].lower() == 'true',
                    notificar_email=row['notificar_email'].lower() == 'true',
                    notificar_telegram=row['notificar_telegram'].lower() == 'true',
                    chat_id_telegram=row['chat_id_telegram'] if row['chat_id_telegram'] else None
                )
                db.session.add(usuario)
        
        # Importar Clientes
        if 'clientes' in csv_files:
            clientes_reader = csv.DictReader(io.StringIO(csv_files['clientes']))
            for row in clientes_reader:
                cliente = Cliente(
                    id=int(row['id']) if row['id'] else None,
                    nombre=row['nombre'],
                    email=row['email'] if row['email'] else None,
                    telefono=row['telefono'],
                    estado=row['estado'],
                    localidad=row['localidad'],
                    observaciones=row['observaciones'] if row['observaciones'] else None,
                    tipo_cliente=row['tipo_cliente'] if row['tipo_cliente'] else None,
                    interes=row['interes'] if row['interes'] else None,
                    zonas=row['zonas'] if row['zonas'] else None,
                    precio_min=int(row['precio_min']) if row['precio_min'] else None,
                    precio_max=int(row['precio_max']) if row['precio_max'] else None,
                    encuesta_enviada=row['encuesta_enviada'],
                    comercial_id=int(row['comercial_id']) if row['comercial_id'] else None,
                    fecha_creacion=datetime.fromisoformat(row['fecha_creacion']) if row['fecha_creacion'] else None,
                    fecha_modificacion=datetime.fromisoformat(row['fecha_modificacion']) if row['fecha_modificacion'] else None,
                    activo=row['activo'].lower() == 'true',
                    visto_por=int(row['visto_por']) if row['visto_por'] else None
                )
                db.session.add(cliente)
        
        # Importar Tareas
        if 'tareas' in csv_files:
            tareas_reader = csv.DictReader(io.StringIO(csv_files['tareas']))
            for row in tareas_reader:
                from datetime import date, time
                tarea = Tarea(
                    id=int(row['id']) if row['id'] else None,
                    usuario_id=int(row['usuario_id']),
                    cliente_id=int(row['cliente_id']) if row['cliente_id'] else None,
                    fecha=date.fromisoformat(row['fecha']) if row['fecha'] else None,
                    hora=time.fromisoformat(row['hora']) if row['hora'] else None,
                    comentario=row['comentario'],
                    resolucion=row['resolucion'],
                    estado=row['estado'],
                    google_event_id=row['google_event_id'] if row['google_event_id'] else None
                )
                db.session.add(tarea)
        
        # Importar Eventos
        if 'eventos' in csv_files:
            eventos_reader = csv.DictReader(io.StringIO(csv_files['eventos']))
            for row in eventos_reader:
                from datetime import date, time
                evento = Evento(
                    id=int(row['id']) if row['id'] else None,
                    titulo=row['titulo'],
                    descripcion=row['descripcion'],
                    fecha=date.fromisoformat(row['fecha']) if row['fecha'] else None,
                    hora_inicio=time.fromisoformat(row['hora_inicio']) if row['hora_inicio'] else None,
                    hora_fin=time.fromisoformat(row['hora_fin']) if row['hora_fin'] else None,
                    usuario_id=int(row['usuario_id']) if row['usuario_id'] else None,
                    cliente_id=int(row['cliente_id']) if row['cliente_id'] else None
                )
                db.session.add(evento)
        
        # Importar Respuestas de Formulario
        if 'respuestas_formulario' in csv_files:
            respuestas_reader = csv.DictReader(io.StringIO(csv_files['respuestas_formulario']))
            for row in respuestas_reader:
                respuesta = RespuestaFormulario(
                    id=int(row['id']) if row['id'] else None,
                    cliente_id=int(row['cliente_id']),
                    puntuacion1=int(row['puntuacion1']),
                    puntuacion2=int(row['puntuacion2']) if row['puntuacion2'] else None,
                    puntuacion_media=float(row['puntuacion_media']),
                    sugerencias=row['sugerencias'] if row['sugerencias'] else None,
                    fecha=datetime.fromisoformat(row['fecha']) if row['fecha'] else None
                )
                db.session.add(respuesta)
        
        db.session.commit()
        return True, "Base de datos importada correctamente"
        
    except Exception as e:
        db.session.rollback()
        return False, f"Error al importar: {str(e)}"

def create_backup_zip():
    """
    Crea un archivo ZIP con todos los CSV de la base de datos
    """
    import zipfile
    from io import BytesIO
    
    csv_data = export_database_to_csv()
    
    # Crear ZIP en memoria
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for table_name, csv_content in csv_data.items():
            zip_file.writestr(f"{table_name}.csv", csv_content)
        
        # Agregar archivo de información
        info_content = f"""Respaldo de Base de Datos - Metro2
Fecha de creación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Archivos incluidos:
- usuarios.csv: Datos de usuarios del sistema
- clientes.csv: Base de datos de clientes
- tareas.csv: Tareas y actividades
- eventos.csv: Eventos del calendario
- respuestas_formulario.csv: Respuestas de encuestas

Para restaurar:
1. Usar la función de importar en el panel de administración
2. O importar manualmente cada CSV en el orden correcto
"""
        zip_file.writestr("README.txt", info_content)
    
    zip_buffer.seek(0)
    return zip_buffer
