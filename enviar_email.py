import smtplib
from email.message import EmailMessage
import os

def enviar_email(destinatario, asunto, cuerpo):
    """
    Envía un email simple usando SMTP.
    - destinatario: dirección de correo destino
    - asunto: asunto del mensaje
    - cuerpo: texto del mensaje
    """
    print("Intentando enviar correo...")
    #remitente = os.environ.get('EMAIL_REMITENTE')
    #password = os.environ.get('EMAIL_PASSWORD')
    remitente = 'jmurillo@alditraex.es'
    password = 'Jm.b06422208'
    smtp_server = os.environ.get('EMAIL_SMTP_SERVER', 'smtp.ionos.es')
    smtp_port = int(os.environ.get('EMAIL_SMTP_PORT', 465))

    if not remitente or not password:
        print("Faltan remitente o password")
        raise Exception('Faltan las variables de entorno EMAIL_REMITENTE o EMAIL_PASSWORD')

    msg = EmailMessage()
    msg['From'] = remitente
    msg['To'] = destinatario
    msg['Subject'] = asunto
    msg.set_content(cuerpo)

    try:
        if smtp_port == 465:
            with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
                server.login(remitente, password)
                server.send_message(msg)
        else:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(remitente, password)
                server.send_message(msg)
        print("Correo enviado correctamente")
    except Exception as e:
        print(f"Error al enviar correo: {e}")
        raise

    return True 