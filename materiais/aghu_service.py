from typing import Optional, Dict, Any

import psycopg2

from .aghu_queries import PacienteQuery


def _get_connection():
    """
    Conexão direta com o banco AGHU.
    As configurações são lidas de settings.py para evitar hard‑coding.
    Django 5 não suporta Postgres 9, por isso usamos psycopg2 puro.
    Um timeout opcional pode ser fornecido via `AGHU_TIMEOUT`.
    """
    from django.conf import settings
    import logging

    params = dict(
        dbname=getattr(settings, 'AGHU_DB_NAME', 'dbaghu'),
        user=getattr(settings, 'AGHU_DB_USER', 'ugen_integra'),
        password=getattr(settings, 'AGHU_DB_PASSWORD', 'aghuintegracao'),
        host=getattr(settings, 'AGHU_DB_HOST', '10.206.3.112'),
        port=getattr(settings, 'AGHU_DB_PORT', '6544'),
    )
    timeout = getattr(settings, 'AGHU_TIMEOUT', None)
    if timeout:
        params['connect_timeout'] = timeout

    try:
        return psycopg2.connect(**params)
    except Exception as e:
        logging.getLogger(__name__).exception('Erro ao conectar ao banco AGHU')
        raise


def buscar_paciente_por_prontuario(prontuario: int) -> Optional[Dict[str, Any]]:
    """
    Busca identificação do paciente no banco AGHU a partir do prontuário.
    Retorna um dicionário simples ou None se não encontrar.
    """
    sql = PacienteQuery.detalhes_por_prontuario()

    conn = _get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, [prontuario])
            row = cursor.fetchone()
            columns = [col[0] for col in cursor.description] if cursor.description else []
    finally:
        conn.close()

    if not row:
        return None

    return dict(zip(columns, row))


def buscar_pacientes_por_nome(nome: str, limite: int = 10) -> list[Dict[str, Any]]:
    """
    Busca pacientes no AGHU por nome (busca parcial).
    Retorna lista de dicionários com dados básicos.
    """
    sql = PacienteQuery.buscar_por_nome_ou_prontuario()
    
    nome = (nome or '').strip()
    prontuario_param = int(nome) if nome.isdigit() else None

    conn = _get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, [prontuario_param, prontuario_param, f"%{nome}%", f"%{nome}%", limite])
            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description] if cursor.description else []
    finally:
        conn.close()

    return [dict(zip(columns, row)) for row in rows]

