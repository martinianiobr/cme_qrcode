class FrontDeskPatientQuery:
    @staticmethod
    def all():
        return """
            SELECT
                pacientes.prontuario,
                CASE WHEN
                    (char_length(pacientes.nome_social)>=3) THEN pacientes.nome_social
                ELSE
                    pacientes.nome
                END as nome,
                internacoes.dthr_internacao AS "Data da Internação",
                pacientes.nome_mae AS "Nome da mãe",
                pacientes.dt_nascimento AS "Data de Nascimento"
            FROM
                agh.ain_internacoes internacoes
            LEFT JOIN
                agh.aip_pacientes pacientes on internacoes.pac_codigo = pacientes.codigo
            WHERE
                internacoes.dthr_alta_medica is null AND
                CASE WHEN
                    (char_length(pacientes.nome_social)>=3) THEN pacientes.nome_social
                ELSE
                    pacientes.nome
                END ILIKE %s
        """

    @staticmethod
    def one():
        return """
            SELECT
                pacientes.prontuario,
                CASE WHEN
                    (char_length(pacientes.nome_social)>=3) THEN pacientes.nome_social
                ELSE
                    pacientes.nome
                END as nome,
                internacoes.dthr_internacao AS "Data da Internação",
                pacientes.nome_mae AS "Nome da mãe",
                pacientes.dt_nascimento AS "Data de Nascimento"
            FROM
                agh.ain_internacoes internacoes
            LEFT JOIN
                agh.aip_pacientes pacientes on internacoes.pac_codigo = pacientes.codigo
            WHERE
                internacoes.dthr_alta_medica is null AND
                pacientes.prontuario = %s
        """


class FrontDeskBedQuery:
    @staticmethod
    def all():
        return """
            SELECT
                pacientes.prontuario,
                CASE WHEN
                    (char_length(pacientes.nome_social)>=3) THEN pacientes.nome_social
                ELSE
                    pacientes.nome
                END as nome,
                internacoes.dthr_internacao as "Data Internação",
                pacientes.nome_mae as "Nome da mãe",
                pacientes.dt_nascimento as "Data Nascimento"
            FROM
                agh.ain_internacoes internacoes
            LEFT JOIN
                agh.aip_pacientes pacientes on internacoes.pac_codigo = pacientes.codigo
            WHERE
                internacoes.lto_lto_id is not null AND
                internacoes.dthr_alta_medica is null AND
                CASE WHEN
                    (char_length(pacientes.nome_social)>=3) THEN pacientes.nome_social
                ELSE
                    pacientes.nome
                END ILIKE %s
        """

    @staticmethod
    def one():
        return """
            SELECT
                pacientes.prontuario,
                CASE WHEN
                    (char_length(pacientes.nome_social)>=3) THEN pacientes.nome_social
                ELSE
                    pacientes.nome
                END as nome,
                internacoes.dthr_internacao as "Data Internação",
                pacientes.nome_mae as "Nome da mãe",
                pacientes.dt_nascimento as "Data Nascimento"
            FROM
                agh.ain_internacoes internacoes
            LEFT JOIN
                agh.aip_pacientes pacientes on internacoes.pac_codigo = pacientes.codigo
            WHERE
                internacoes.lto_lto_id is not null AND
                internacoes.dthr_alta_medica is null AND
              pacientes.prontuario = %s
         """


def get_patient_identification():
    return """
        SELECT
            pacientes.prontuario,
            CASE WHEN
                (char_length(pacientes.nome_social)>=3) THEN pacientes.nome_social
            ELSE
                pacientes.nome
            END as nome,
            internacoes.dthr_internacao as "Data Internação",
            pacientes.nome_mae as "Nome da mãe",
            pacientes.dt_nascimento as "Data Nascimento"
        FROM
            agh.ain_internacoes internacoes
        LEFT JOIN
            agh.aip_pacientes pacientes on internacoes.pac_codigo = pacientes.codigo
        WHERE
            internacoes.lto_lto_id is not null AND
            internacoes.dthr_alta_medica is null AND
            CASE
                -- pesquisa pelo prontuario do paciente
                WHEN %s IS NOT NULL THEN pacientes.prontuario = %s
                -- pesquisa pelo nome do paciente
                WHEN %s IS NOT NULL THEN 
                    CASE WHEN
                        (char_length(pacientes.nome_social)>=3) THEN pacientes.nome_social
                    ELSE
                        pacientes.nome
                    END ILIKE %s
            END
    """

