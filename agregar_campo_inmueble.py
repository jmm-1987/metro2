"""
Script de migración para añadir el campo 'inmueble' a la tabla Cliente
Ejecutar este script una vez para actualizar la base de datos existente
"""

from app import app, db
from sqlalchemy import text

def agregar_campo_inmueble():
    """Añade el campo inmueble a la tabla cliente si no existe"""
    with app.app_context():
        try:
            # Verificar si la columna ya existe
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('cliente')]
            
            if 'inmueble' in columns:
                print("✓ El campo 'inmueble' ya existe en la tabla cliente")
                return
            
            # Añadir la columna
            with db.engine.connect() as conn:
                conn.execute(text('ALTER TABLE cliente ADD COLUMN inmueble VARCHAR(100)'))
                conn.commit()
            
            print("✓ Campo 'inmueble' añadido correctamente a la tabla cliente")
            
        except Exception as e:
            print(f"✗ Error al añadir el campo 'inmueble': {e}")
            raise

if __name__ == '__main__':
    print("Iniciando migración de base de datos...")
    agregar_campo_inmueble()
    print("Migración completada!")

