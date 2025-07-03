import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta

def crear_evento_google_calendar(titulo, descripcion, fecha, hora, duracion_min=30):
    """
    Crea un evento en Google Calendar usando una cuenta de servicio.
    - titulo: Título del evento
    - descripcion: Descripción del evento
    - fecha: string en formato 'YYYY-MM-DD'
    - hora: string en formato 'HH:MM'
    - duracion_min: duración en minutos (por defecto 30)
    """
    creds_json = os.environ.get('GOOGLE_CREDENTIALS_JSON')
    if not creds_json:
        raise Exception("No se encontró la variable de entorno GOOGLE_CREDENTIALS_JSON")
    creds_dict = json.loads(creds_json)
    creds = service_account.Credentials.from_service_account_info(
        creds_dict,
        scopes=['https://www.googleapis.com/auth/calendar']
    )
    service = build('calendar', 'v3', credentials=creds)

    calendar_id = os.environ.get('GOOGLE_CALENDAR_ID')
    if not calendar_id:
        raise Exception("No se encontró la variable de entorno GOOGLE_CALENDAR_ID")

    start_datetime = f"{fecha}T{hora}:00"
    start_dt = datetime.strptime(start_datetime, "%Y-%m-%dT%H:%M:%S")
    end_dt = start_dt + timedelta(minutes=duracion_min)
    event = {
        'summary': titulo,
        'description': descripcion,
        'start': {
            'dateTime': start_dt.isoformat(),
            'timeZone': 'Europe/Madrid',  # Cambia a tu zona horaria si es necesario
        },
        'end': {
            'dateTime': end_dt.isoformat(),
            'timeZone': 'Europe/Madrid',
        },
    }
    evento = service.events().insert(calendarId=calendar_id, body=event).execute()
    return evento.get('id')

def crear_evento_google_calendar_desde_tarea(tarea):
    """
    Crea un evento en Google Calendar usando una instancia de Tarea.
    """
    creds_json = os.environ.get('GOOGLE_CREDENTIALS_JSON')
    if not creds_json:
        raise Exception("No se encontró la variable de entorno GOOGLE_CREDENTIALS_JSON")
    creds_dict = json.loads(creds_json)
    creds = service_account.Credentials.from_service_account_info(
        creds_dict,
        scopes=['https://www.googleapis.com/auth/calendar']
    )
    service = build('calendar', 'v3', credentials=creds)

    calendar_id = os.environ.get('GOOGLE_CALENDAR_ID')
    if not calendar_id:
        raise Exception("No se encontró la variable de entorno GOOGLE_CALENDAR_ID")

    # Extraer datos de la tarea
    titulo = f"Tarea: {tarea.comentario}"
    cliente_nombre = tarea.cliente.nombre if tarea.cliente else ''
    cliente_telefono = tarea.cliente.telefono if tarea.cliente else ''
    descripcion = f"Cliente: {cliente_nombre} ({cliente_telefono})\nResolución: {tarea.resolucion or ''}"
    fecha = str(tarea.fecha)
    hora = str(tarea.hora)[:5]  # formato HH:MM
    duracion_min = 30

    start_datetime = f"{fecha}T{hora}:00"
    start_dt = datetime.strptime(start_datetime, "%Y-%m-%dT%H:%M:%S")
    end_dt = start_dt + timedelta(minutes=duracion_min)
    event = {
        'summary': titulo,
        'description': descripcion,
        'start': {
            'dateTime': start_dt.isoformat(),
            'timeZone': 'Europe/Madrid',  # Cambia a tu zona horaria si es necesario
        },
        'end': {
            'dateTime': end_dt.isoformat(),
            'timeZone': 'Europe/Madrid',
        },
    }
    evento = service.events().insert(calendarId=calendar_id, body=event).execute()
    return evento.get('id') 