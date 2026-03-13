class PacienteQuery:
    @staticmethod
    def buscar_por_nome_ou_prontuario():
        return """
            SELECT
                pac.prontuario,
                CASE
                    WHEN char_length(COALESCE(pac.nome_social, '')) >= 3 THEN pac.nome_social
                    ELSE pac.nome
                END AS nome,
                pac.nome_mae,
                pac.dt_nascimento AS data_nascimento,
                pac.cpf,
                CONCAT_WS(' ',
                    NULLIF('(' || COALESCE(pac.ddd_fone_residencial::text, '') || ')', '()'),
                    NULLIF(COALESCE(pac.fone_residencial::text, ''), '')
                ) AS telefone
            FROM agh.aip_pacientes pac
            WHERE
                (
                    %s IS NOT NULL
                    AND pac.prontuario = %s
                )
                OR
                (
                    (char_length(COALESCE(pac.nome_social, '')) >= 3 AND pac.nome_social ILIKE %s)
                    OR
                    (char_length(COALESCE(pac.nome_social, '')) < 3 AND pac.nome ILIKE %s)
                )
            ORDER BY nome
            LIMIT %s
        """

    @staticmethod
    def detalhes_por_prontuario():
        return """
            SELECT
                pac.prontuario,
                CASE
                    WHEN char_length(COALESCE(pac.nome_social, '')) >= 3 THEN pac.nome_social
                    ELSE pac.nome
                END AS nome,
                pac.nome_social,
                pac.nome_mae,
                pac.dt_nascimento AS data_nascimento,
                CAST(EXTRACT(YEAR FROM AGE(CURRENT_DATE, pac.dt_nascimento)) AS INTEGER) AS idade,
                pac.uf_sigla AS uf,
                pac.cor,
                pac.sexo,
                pac.nome_pai,
                pac.naturalidade,
                CONCAT_WS(' ',
                    NULLIF('(' || COALESCE(pac.ddd_fone_residencial::text, '') || ')', '()'),
                    NULLIF(COALESCE(pac.fone_residencial::text, ''), '')
                ) AS telefone,
                pac.estado_civil,
                pac.cpf,
                pac.rg,
                pac.nro_cartao_saude AS cns,
                pac.sexo_biologico,
                intern.dthr_internacao AS data_internacao,
                leito.lto_id AS leito,
                unidade.descricao AS unidade_internacao
            FROM agh.aip_pacientes pac
            LEFT JOIN agh.ain_internacoes intern ON intern.pac_codigo = pac.codigo
            LEFT JOIN agh.ain_leitos leito ON intern.lto_lto_id = leito.lto_id
            LEFT JOIN agh.agh_unidades_funcionais unidade ON intern.unf_seq = unidade.seq
            WHERE pac.prontuario = %s
            ORDER BY intern.dthr_internacao DESC NULLS LAST
            LIMIT 1
        """


def get_patient_identification():
    return PacienteQuery.detalhes_por_prontuario()

