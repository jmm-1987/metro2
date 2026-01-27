#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de inicialización de la base de datos SQLite
Se ejecuta automáticamente al iniciar la aplicación
"""
from app import app, db
from models import Usuario, Cliente, Tarea, Evento, RespuestaFormulario
import os

def init_database():
    """Inicializar la base de datos SQLite"""
    with app.app_context():
        # Crear todas las tablas si no existen
        db.create_all()
        print("✓ Base de datos SQLite inicializada correctamente")
        
        # Verificar que el archivo existe
        instance_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
        db_path = os.path.join(instance_path, 'database.db')
        
        if os.path.exists(db_path):
            size = os.path.getsize(db_path)
            print(f"✓ Archivo de base de datos: {db_path} ({size} bytes)")
        else:
            print(f"⚠ Archivo de base de datos no encontrado: {db_path}")

if __name__ == '__main__':
    init_database()

