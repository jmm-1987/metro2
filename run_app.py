#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para ejecutar la aplicación Flask en modo debug
"""
import sys
import logging
from app import app
import os

# Configurar logging para que se vea TODO
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

if __name__ == '__main__':
    # Habilitar modo debug para ver errores detallados
    app.config['DEBUG'] = True
    app.config['TESTING'] = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    
    # Usar el puerto de Render o 5000 por defecto
    port = int(os.environ.get('PORT', 5000))
    
    print("\n" + "=" * 70)
    print(" " * 20 + "INICIANDO APLICACIÓN FLASK")
    print("=" * 70)
    print(f"Puerto: {port}")
    print(f"URL: http://127.0.0.1:{port}")
    print(f"Templates auto-reload: ACTIVADO")
    print(f"Cache deshabilitado")
    print(f"Debug mode: ACTIVADO")
    print(f"Logging: ACTIVADO")
    print("=" * 70)
    print("\n>>> TODOS LOS LOGS SE MOSTRARÁN AQUÍ <<<")
    print(">>> Cuando accedas al dashboard verás información del usuario <<<")
    print("\nPresiona CTRL+C para detener el servidor\n")
    print("=" * 70 + "\n")
    
    app.run(host='0.0.0.0', port=port, debug=True, use_reloader=True, use_debugger=True)

