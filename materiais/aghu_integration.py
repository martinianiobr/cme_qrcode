"""
Integração com AGHU para busca de pacientes reais
"""
import requests
import json
from django.conf import settings
from django.core.cache import cache
from datetime import datetime, timedelta

class AGHUIntegration:
    """Classe para integração com sistema AGHU"""
    
    BASE_URL = getattr(settings, 'AGHU_BASE_URL', 'http://aghu.hospital.gov.br')
    TIMEOUT = getattr(settings, 'AGHU_TIMEOUT', 10)
    
    @classmethod
    def buscar_paciente_por_prontuario(cls, prontuario):
        """
        Buscar paciente no AGHU pelo prontuário
        Retorna dados do paciente ou None se não encontrado
        """
        try:
            # Cache por 5 minutos para não sobrecarregar AGHU
            cache_key = f'paciente_aghu_{prontuario}'
            cached_data = cache.get(cache_key)
            
            if cached_data:
                return cached_data
            
            # Simulação de chamada API AGHU
            # Na implementação real, substituir pela chamada real:
            # url = f"{cls.BASE_URL}/api/pacientes/{prontuario}"
            # response = requests.get(url, timeout=cls.TIMEOUT, headers={'Authorization': f'Bearer {cls.get_token()}'})
            
            # Dados simulados para demonstração
            paciente_data = cls._simular_busca_aghu(prontuario)
            
            if paciente_data:
                # Salvar no cache
                cache.set(cache_key, paciente_data, 300)  # 5 minutos
                return paciente_data
                
            return None
            
        except Exception as e:
            print(f"Erro na busca AGHU: {e}")
            return None
    
    @classmethod
    def buscar_pacientes_por_nome(cls, nome, limite=10):
        """
        Buscar pacientes no AGHU pelo nome
        Retorna lista de pacientes encontrados
        """
        try:
            cache_key = f'pacientes_nome_{nome}_{limite}'
            cached_data = cache.get(cache_key)
            
            if cached_data:
                return cached_data
            
            # Na implementação real:
            # url = f"{cls.BASE_URL}/api/pacientes?nome={nome}&limite={limite}"
            # response = requests.get(url, timeout=cls.TIMEOUT)
            
            # Dados simulados para demonstração
            pacientes_data = cls._simular_busca_por_nome(nome, limite)
            
            if pacientes_data:
                cache.set(cache_key, pacientes_data, 300)
                return pacientes_data
                
            return []
            
        except Exception as e:
            print(f"Erro na busca AGHU: {e}")
            return []
    
    @classmethod
    def _simular_busca_aghu(cls, prontuario):
        """
        Simular dados de paciente do AGHU para demonstração
        Substituir por chamada real quando disponível
        """
        # Dados simulados baseados no prontuário
        pacientes_simulados = {
            '123456': {
                'prontuario': '123456',
                'nome': 'JOÃO DA SILVA SANTOS',
                'nome_mae': 'MARIA APARECIDA SILVA',
                'data_nascimento': '1980-05-15',
                'cpf': '123.456.789-00',
                'telefone': '(11) 98765-4321',
                'convenio': 'UNIMED',
                'leito': 'UTI-001',
                'medico_responsavel': 'Dr. Carlos Alberto'
            },
            '789012': {
                'prontuario': '789012',
                'nome': 'MARIA APARECIDA DOS SANTOS',
                'nome_mae': 'JOANA DAS DORES SANTOS',
                'data_nascimento': '1975-08-22',
                'cpf': '987.654.321-00',
                'telefone': '(11) 91234-5678',
                'convenio': 'AMIL',
                'leito': 'ENF-023',
                'medico_responsavel': 'Dra. Ana Paula'
            },
            '345678': {
                'prontuario': '345678',
                'nome': 'CARLOS ROBERTO OLIVEIRA',
                'nome_mae': 'HELENA DE OLIVEIRA',
                'data_nascimento': '1985-12-10',
                'cpf': '456.789.012-00',
                'telefone': '(11) 87654-3210',
                'convenio': 'SULAMERICA',
                'leito': 'CLI-045',
                'medico_responsavel': 'Dr. Marcos Vinícius'
            }
        }
        
        return pacientes_simulados.get(str(prontuario))
    
    @classmethod
    def _simular_busca_por_nome(cls, nome, limite=10):
        """
        Simular busca por nome no AGHU
        """
        pacientes_simulados = [
            {
                'prontuario': '123456',
                'nome': 'JOÃO DA SILVA SANTOS',
                'data_nascimento': '1980-05-15',
                'cpf': '123.456.789-00',
                'telefone': '(11) 98765-4321'
            },
            {
                'prontuario': '789012',
                'nome': 'MARIA APARECIDA DOS SANTOS',
                'data_nascimento': '1975-08-22',
                'cpf': '987.654.321-00',
                'telefone': '(11) 91234-5678'
            },
            {
                'prontuario': '345678',
                'nome': 'CARLOS ROBERTO OLIVEIRA',
                'data_nascimento': '1985-12-10',
                'cpf': '456.789.012-00',
                'telefone': '(11) 87654-3210'
            }
        ]
        
        # Filtrar por nome
        nome_upper = nome.upper()
        resultados = []
        
        for paciente in pacientes_simulados:
            if nome_upper in paciente['nome'].upper():
                resultados.append(paciente)
                if len(resultados) >= limite:
                    break
        
        return resultados
    
    @classmethod
    def get_token(cls):
        """
        Obter token de autenticação do AGHU
        Implementar conforme documentação do AGHU
        """
        # Implementar obtenção de token real
        return "token_aghu_simulado"
