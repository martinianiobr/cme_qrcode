import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cme_qrcode.settings')
django.setup()

from django.db import connection
cursor = connection.cursor()

print('=== ANÁLISE COMPLETA ===')

# Verificar estrutura atual
cursor.execute('PRAGMA table_info(materiais_checklist);')
columns = cursor.fetchall()
print('Colunas atuais:')
for col in columns:
    print(f'  {col[1]}: {col[2]}')

# Verificar registros
cursor.execute('SELECT * FROM materiais_checklist LIMIT 2;')
registros = cursor.fetchall()
print(f'\nRegistros: {len(registros)}')
for reg in registros:
    print(f'  {reg}')

cursor.close()
