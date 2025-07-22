import requests
import os

def enviar_telegram(mensaje, chat_id, token):
    """
    Envía un mensaje de Telegram usando un bot.
    Args:
        mensaje (str): El texto a enviar.
        chat_id (int o str): El chat_id del usuario o grupo.
        token (str): El token del bot de Telegram.
    Returns:
        bool: True si el mensaje se envió correctamente, False si hubo error.
    """
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    data = {
        'chat_id': chat_id,
        'text': mensaje
    }
    try:
        response = requests.post(url, data=data, timeout=10)
        return response.ok
    except Exception as e:
        print(f"Error enviando mensaje de Telegram: {e}")
        return False 

TOKEN_TELEGRAM = os.environ.get('TELEGRAM_BOT_TOKEN') 