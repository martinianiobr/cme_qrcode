import os
import django
from django.conf import settings
from django.db import connection

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cme_qrcode.settings')
django.setup()

def limpar_banco():
    """Limpa registros problemáticos do banco na ordem correta"""
    cursor = connection.cursor()
    
    try:
        # 1. Apagar leituras QR (dependem de checklist)
        cursor.execute('DELETE FROM materiais_leituraqr;')
        print('✅ Leituras QR apagadas')
        
        # 2. Apagar itens de checklist (dependem de checklist)
        cursor.execute('DELETE FROM materiais_checklistitem;')
        print('✅ Itens de checklist apagados')
        
        # 3. Apagar registros antigos da checklist
        cursor.execute('DELETE FROM materiais_checklist;')
        print('✅ Registros antigos de checklist apagados')
        
        # 4. Apagar migrações problemáticas
        cursor.execute("DELETE FROM django_migrations WHERE app = 'materiais' AND name LIKE '%paciente%';")
        print('✅ Migrações problemáticas apagadas')
        
        # 5. Confirmar limpeza
        cursor.execute('SELECT COUNT(*) FROM materiais_checklist;')
        count = cursor.fetchone()[0]
        print(f'📊 Registros restantes em checklist: {count}')
        
        cursor.close()
        print('🎉 Limpeza concluída com sucesso!')
        
    except Exception as e:
        print(f'❌ Erro: {e}')
        cursor.close()

if __name__ == '__main__':
    limpar_banco()
