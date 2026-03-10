from typing import Optional, Dict, Any

import psycopg2

from .aghu_queries import get_patient_identification


def _get_connection():
    """
    Conexão direta com o banco AGHU.
    Django 5 não suporta Postgres 9, por isso usamos psycopg2 puro.
    """
    return psycopg2.connect(
        dbname="dbaghu",
        user="ugen_integra",
        password="aghuintegracao",
        host="10.206.3.112",
        port=6544,
    )


def buscar_paciente_por_prontuario(prontuario: int) -> Optional[Dict[str, Any]]:
    """
    Busca identificação do paciente no banco AGHU a partir do prontuário.
    Retorna um dicionário simples ou None se não encontrar.
    """
    sql = get_patient_identification()
    params = [prontuario, prontuario, None, None]

    conn = _get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            row = cursor.fetchone()
    finally:
        conn.close()

    if not row:
        return None

    return {
        "prontuario": row[0],
        "nome": row[1],
        "data_internacao": row[2],
        "nome_mae": row[3],
        "data_nascimento": row[4],
    }


def buscar_pacientes_por_nome(nome: str, limite: int = 10) -> list[Dict[str, Any]]:
    """
    Busca pacientes no AGHU por nome (busca parcial).
    Retorna lista de dicionários com dados básicos.
    """
    sql = """
    SELECT DISTINCT 
        aip.prf_seq prontuario,
        aip.nme_paciente nome,
        aip.dthr_internacao data_internacao,
        aip.nme_mae nome_mae,
        aip.dt_nascimento data_nascimento
    FROM aghpacientes aip
    WHERE UPPER(aip.nme_paciente) LIKE UPPER(%s)
    AND aip.ind_situacao = 'I'
    ORDER BY aip.nme_paciente
    LIMIT %s
    """
    
    conn = _get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, [f"%{nome}%", limite])
            rows = cursor.fetchall()
    finally:
        conn.close()

    return [
        {
            "prontuario": row[0],
            "nome": row[1],
            "data_internacao": row[2],
            "nome_mae": row[3],
            "data_nascimento": row[4],
        }
        for row in rows
    ]

