#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de prueba para verificar que el dashboard renderiza correctamente
"""
from app import app
from flask import render_template_string

# Simular un usuario root
class MockUser:
    nombre = 'root'
    es_admin = True
    id = 1

with app.app_context():
    # Verificar que las rutas existen
    print("Rutas disponibles:")
    for rule in app.url_map.iter_rules():
        if 'panel' in rule.rule:
            print(f"  [OK] {rule.rule}")
    
    # Verificar que el template existe
    import os
    template_path = os.path.join('templates', 'dashboard.html')
    if os.path.exists(template_path):
        print(f"\n[OK] Template encontrado: {template_path}")
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'panel_respaldo' in content:
                print("  [OK] Boton Respaldo encontrado en template")
            else:
                print("  [ERROR] Boton Respaldo NO encontrado")
            if 'panel_backup' in content:
                print("  [OK] Boton Backup encontrado en template")
            else:
                print("  [ERROR] Boton Backup NO encontrado")
            if 'current_user.nombre == \'root\'' in content:
                print("  [OK] Condicion para mostrar botones encontrada")
            else:
                print("  [ERROR] Condicion para mostrar botones NO encontrada")
    else:
        print(f"\n[ERROR] Template NO encontrado: {template_path}")

print("\n" + "="*60)
print("Si todo esta [OK], el problema puede ser:")
print("1. No estas logueado como 'root'")
print("2. La aplicacion no se recargo con los cambios")
print("3. El navegador tiene cache")
print("="*60)

