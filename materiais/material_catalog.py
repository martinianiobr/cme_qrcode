from datetime import timedelta

from django.utils import timezone

from .models import Material, Kit


SYSTEM_MATERIAL_CATALOG = [
    {
        'codigo_catalogo': 'CIR-001',
        'codigo_qr': 'SYS-CIR-001',
        'nome': 'Cabo de bisturi',
        'categoria': 'Corte',
        'tipo': 'No 3',
        'tamanho': '12 cm',
        'material_composicao': 'Aco inox',
        'uso_observacao': 'Para laminas pequenas',
        'classificacao_processamento': 'reutilizavel_esteril',
        'lote': 'CAT-001',
        'responsavel': 'Sistema',
        'estoque': 5,
        'fornecedor': 'Catalogo Base',
        'localizacao': 'Catalogo Padrao CME',
    },
    {
        'codigo_catalogo': 'CIR-002',
        'codigo_qr': 'SYS-CIR-002',
        'nome': 'Cabo de bisturi',
        'categoria': 'Corte',
        'tipo': 'No 4',
        'tamanho': '12 cm',
        'material_composicao': 'Aco inox',
        'uso_observacao': 'Para laminas grandes',
        'classificacao_processamento': 'reutilizavel_esteril',
        'lote': 'CAT-002',
        'responsavel': 'Sistema',
        'estoque': 5,
        'fornecedor': 'Catalogo Base',
        'localizacao': 'Catalogo Padrao CME',
    },
    {
        'codigo_catalogo': 'CIR-003',
        'codigo_qr': 'SYS-CIR-003',
        'nome': 'Lamina de bisturi',
        'categoria': 'Corte',
        'tipo': 'No 10',
        'tamanho': 'Unico uso',
        'material_composicao': 'Aco carbono',
        'uso_observacao': 'Incisões gerais',
        'classificacao_processamento': 'descartavel_esteril',
        'lote': 'CAT-003',
        'responsavel': 'Sistema',
        'estoque': 50,
        'fornecedor': 'Catalogo Base',
        'localizacao': 'Catalogo Padrao CME',
    },
    {
        'codigo_catalogo': 'CIR-004',
        'codigo_qr': 'SYS-CIR-004',
        'nome': 'Lamina de bisturi',
        'categoria': 'Corte',
        'tipo': 'No 11',
        'tamanho': 'Unico uso',
        'material_composicao': 'Aco carbono',
        'uso_observacao': 'Incisões puntiformes',
        'classificacao_processamento': 'descartavel_esteril',
        'lote': 'CAT-004',
        'responsavel': 'Sistema',
        'estoque': 50,
        'fornecedor': 'Catalogo Base',
        'localizacao': 'Catalogo Padrao CME',
    },
    {
        'codigo_catalogo': 'CIR-005',
        'codigo_qr': 'SYS-CIR-005',
        'nome': 'Tesoura Mayo',
        'categoria': 'Disseccao',
        'tipo': 'Reta',
        'tamanho': '14 cm',
        'material_composicao': 'Aco inox',
        'uso_observacao': 'Tecidos resistentes',
        'classificacao_processamento': 'reutilizavel_esteril',
        'lote': 'CAT-005',
        'responsavel': 'Sistema',
        'estoque': 8,
        'fornecedor': 'Catalogo Base',
        'localizacao': 'Catalogo Padrao CME',
    },
    {
        'codigo_catalogo': 'CIR-006', 'codigo_qr': 'SYS-CIR-006', 'nome': 'Tesoura Mayo', 'categoria': 'Disseccao', 'tipo': 'Curva', 'tamanho': '14 cm', 'material_composicao': 'Aco inox', 'uso_observacao': 'Tecidos resistentes', 'classificacao_processamento': 'reutilizavel_esteril', 'lote': 'CAT-006', 'responsavel': 'Sistema', 'estoque': 8, 'fornecedor': 'Catalogo Base', 'localizacao': 'Catalogo Padrao CME'
    },
    {
        'codigo_catalogo': 'CIR-007', 'codigo_qr': 'SYS-CIR-007', 'nome': 'Tesoura Metzenbaum', 'categoria': 'Disseccao', 'tipo': 'Reta', 'tamanho': '18 cm', 'material_composicao': 'Aco inox', 'uso_observacao': 'Tecidos delicados', 'classificacao_processamento': 'reutilizavel_esteril', 'lote': 'CAT-007', 'responsavel': 'Sistema', 'estoque': 8, 'fornecedor': 'Catalogo Base', 'localizacao': 'Catalogo Padrao CME'
    },
    {
        'codigo_catalogo': 'CIR-008', 'codigo_qr': 'SYS-CIR-008', 'nome': 'Tesoura Metzenbaum', 'categoria': 'Disseccao', 'tipo': 'Curva', 'tamanho': '18 cm', 'material_composicao': 'Aco inox', 'uso_observacao': 'Tecidos delicados', 'classificacao_processamento': 'reutilizavel_esteril', 'lote': 'CAT-008', 'responsavel': 'Sistema', 'estoque': 8, 'fornecedor': 'Catalogo Base', 'localizacao': 'Catalogo Padrao CME'
    },
    {
        'codigo_catalogo': 'CIR-009', 'codigo_qr': 'SYS-CIR-009', 'nome': 'Pinca Kelly', 'categoria': 'Hemostasia', 'tipo': 'Reta', 'tamanho': '14 cm', 'material_composicao': 'Aco inox', 'uso_observacao': 'Hemostasia media', 'classificacao_processamento': 'reutilizavel_esteril', 'lote': 'CAT-009', 'responsavel': 'Sistema', 'estoque': 10, 'fornecedor': 'Catalogo Base', 'localizacao': 'Catalogo Padrao CME'
    },
    {
        'codigo_catalogo': 'CIR-010', 'codigo_qr': 'SYS-CIR-010', 'nome': 'Pinca Kelly', 'categoria': 'Hemostasia', 'tipo': 'Curva', 'tamanho': '14 cm', 'material_composicao': 'Aco inox', 'uso_observacao': 'Hemostasia media', 'classificacao_processamento': 'reutilizavel_esteril', 'lote': 'CAT-010', 'responsavel': 'Sistema', 'estoque': 10, 'fornecedor': 'Catalogo Base', 'localizacao': 'Catalogo Padrao CME'
    },
    {
        'codigo_catalogo': 'CIR-011', 'codigo_qr': 'SYS-CIR-011', 'nome': 'Pinca Halsted (Mosquito)', 'categoria': 'Hemostasia', 'tipo': 'Reta', 'tamanho': '12 cm', 'material_composicao': 'Aco inox', 'uso_observacao': 'Hemostasia fina', 'classificacao_processamento': 'reutilizavel_esteril', 'lote': 'CAT-011', 'responsavel': 'Sistema', 'estoque': 10, 'fornecedor': 'Catalogo Base', 'localizacao': 'Catalogo Padrao CME'
    },
    {
        'codigo_catalogo': 'CIR-012', 'codigo_qr': 'SYS-CIR-012', 'nome': 'Pinca Halsted (Mosquito)', 'categoria': 'Hemostasia', 'tipo': 'Curva', 'tamanho': '12 cm', 'material_composicao': 'Aco inox', 'uso_observacao': 'Hemostasia fina', 'classificacao_processamento': 'reutilizavel_esteril', 'lote': 'CAT-012', 'responsavel': 'Sistema', 'estoque': 10, 'fornecedor': 'Catalogo Base', 'localizacao': 'Catalogo Padrao CME'
    },
    {
        'codigo_catalogo': 'CIR-013', 'codigo_qr': 'SYS-CIR-013', 'nome': 'Pinca Crile', 'categoria': 'Hemostasia', 'tipo': 'Reta', 'tamanho': '14 cm', 'material_composicao': 'Aco inox', 'uso_observacao': 'Hemostasia media', 'classificacao_processamento': 'reutilizavel_esteril', 'lote': 'CAT-013', 'responsavel': 'Sistema', 'estoque': 10, 'fornecedor': 'Catalogo Base', 'localizacao': 'Catalogo Padrao CME'
    },
    {
        'codigo_catalogo': 'CIR-014', 'codigo_qr': 'SYS-CIR-014', 'nome': 'Pinca Pean', 'categoria': 'Hemostasia', 'tipo': 'Reta', 'tamanho': '16 cm', 'material_composicao': 'Aco inox', 'uso_observacao': 'Hemostasia profunda', 'classificacao_processamento': 'reutilizavel_esteril', 'lote': 'CAT-014', 'responsavel': 'Sistema', 'estoque': 8, 'fornecedor': 'Catalogo Base', 'localizacao': 'Catalogo Padrao CME'
    },
    {
        'codigo_catalogo': 'CIR-015', 'codigo_qr': 'SYS-CIR-015', 'nome': 'Pinca Allis', 'categoria': 'Fixacao', 'tipo': 'Com dentes', 'tamanho': '15 cm', 'material_composicao': 'Aco inox', 'uso_observacao': 'Fixacao de tecidos', 'classificacao_processamento': 'reutilizavel_esteril', 'lote': 'CAT-015', 'responsavel': 'Sistema', 'estoque': 8, 'fornecedor': 'Catalogo Base', 'localizacao': 'Catalogo Padrao CME'
    },
    {
        'codigo_catalogo': 'CIR-016', 'codigo_qr': 'SYS-CIR-016', 'nome': 'Pinca Backhaus', 'categoria': 'Fixacao', 'tipo': 'Campo', 'tamanho': '11 cm', 'material_composicao': 'Aco inox', 'uso_observacao': 'Fixacao de campos', 'classificacao_processamento': 'reutilizavel_esteril', 'lote': 'CAT-016', 'responsavel': 'Sistema', 'estoque': 8, 'fornecedor': 'Catalogo Base', 'localizacao': 'Catalogo Padrao CME'
    },
    {
        'codigo_catalogo': 'CIR-017', 'codigo_qr': 'SYS-CIR-017', 'nome': 'Porta-agulha Mayo-Hegar', 'categoria': 'Sutura', 'tipo': 'Reto', 'tamanho': '14 cm', 'material_composicao': 'Aco inox com Widia', 'uso_observacao': 'Para agulhas medias', 'classificacao_processamento': 'reutilizavel_esteril', 'lote': 'CAT-017', 'responsavel': 'Sistema', 'estoque': 8, 'fornecedor': 'Catalogo Base', 'localizacao': 'Catalogo Padrao CME'
    },
    {
        'codigo_catalogo': 'CIR-018', 'codigo_qr': 'SYS-CIR-018', 'nome': 'Porta-agulha Crile-Wood', 'categoria': 'Sutura', 'tipo': 'Reto', 'tamanho': '15 cm', 'material_composicao': 'Aco inox', 'uso_observacao': 'Para agulhas delicadas', 'classificacao_processamento': 'reutilizavel_esteril', 'lote': 'CAT-018', 'responsavel': 'Sistema', 'estoque': 8, 'fornecedor': 'Catalogo Base', 'localizacao': 'Catalogo Padrao CME'
    },
    {
        'codigo_catalogo': 'CIR-019', 'codigo_qr': 'SYS-CIR-019', 'nome': 'Afastador Farabeuf', 'categoria': 'Exposicao', 'tipo': 'Manual', 'tamanho': '12 cm', 'material_composicao': 'Aco inox', 'uso_observacao': 'Par', 'classificacao_processamento': 'reutilizavel_esteril', 'lote': 'CAT-019', 'responsavel': 'Sistema', 'estoque': 6, 'fornecedor': 'Catalogo Base', 'localizacao': 'Catalogo Padrao CME'
    },
    {
        'codigo_catalogo': 'CIR-020', 'codigo_qr': 'SYS-CIR-020', 'nome': 'Afastador Langenbeck', 'categoria': 'Exposicao', 'tipo': 'Manual', 'tamanho': '20 cm', 'material_composicao': 'Aco inox', 'uso_observacao': 'Uso abdominal', 'classificacao_processamento': 'reutilizavel_esteril', 'lote': 'CAT-020', 'responsavel': 'Sistema', 'estoque': 6, 'fornecedor': 'Catalogo Base', 'localizacao': 'Catalogo Padrao CME'
    },
    {
        'codigo_catalogo': 'CIR-021', 'codigo_qr': 'SYS-CIR-021', 'nome': 'Afastador Balfour', 'categoria': 'Exposicao', 'tipo': 'Autoestatico', 'tamanho': '30 cm', 'material_composicao': 'Aco inox', 'uso_observacao': 'Com lamina', 'classificacao_processamento': 'reutilizavel_esteril', 'lote': 'CAT-021', 'responsavel': 'Sistema', 'estoque': 4, 'fornecedor': 'Catalogo Base', 'localizacao': 'Catalogo Padrao CME'
    },
    {
        'codigo_catalogo': 'CIR-022', 'codigo_qr': 'SYS-CIR-022', 'nome': 'Afastador Gosset', 'categoria': 'Exposicao', 'tipo': 'Autoestatico', 'tamanho': '25 cm', 'material_composicao': 'Aco inox', 'uso_observacao': 'Uso abdominal', 'classificacao_processamento': 'reutilizavel_esteril', 'lote': 'CAT-022', 'responsavel': 'Sistema', 'estoque': 4, 'fornecedor': 'Catalogo Base', 'localizacao': 'Catalogo Padrao CME'
    },
    {
        'codigo_catalogo': 'CIR-023', 'codigo_qr': 'SYS-CIR-023', 'nome': 'Sugador cirurgico', 'categoria': 'Aspiracao', 'tipo': 'Grosso', 'tamanho': '11 pol', 'material_composicao': 'Inox', 'uso_observacao': 'Reutilizavel', 'classificacao_processamento': 'reutilizavel_esteril', 'lote': 'CAT-023', 'responsavel': 'Sistema', 'estoque': 6, 'fornecedor': 'Catalogo Base', 'localizacao': 'Catalogo Padrao CME'
    },
    {
        'codigo_catalogo': 'CIR-024', 'codigo_qr': 'SYS-CIR-024', 'nome': 'Pinca bipolar', 'categoria': 'Energia', 'tipo': 'Reta', 'tamanho': '20 cm', 'material_composicao': 'Inox isolado', 'uso_observacao': 'Uso com cauterio', 'classificacao_processamento': 'reutilizavel_esteril', 'lote': 'CAT-024', 'responsavel': 'Sistema', 'estoque': 4, 'fornecedor': 'Catalogo Base', 'localizacao': 'Catalogo Padrao CME'
    },
    {
        'codigo_catalogo': 'CIR-025', 'codigo_qr': 'SYS-CIR-025', 'nome': 'Ponteira de cauterio', 'categoria': 'Energia', 'tipo': 'Agulha', 'tamanho': 'Unico uso', 'material_composicao': 'Metal condutor', 'uso_observacao': 'Corte fino', 'classificacao_processamento': 'descartavel_esteril', 'lote': 'CAT-025', 'responsavel': 'Sistema', 'estoque': 20, 'fornecedor': 'Catalogo Base', 'localizacao': 'Catalogo Padrao CME'
    },
    {
        'codigo_catalogo': 'CIR-026', 'codigo_qr': 'SYS-CIR-026', 'nome': 'Ponteira de cauterio', 'categoria': 'Energia', 'tipo': 'Faca longa', 'tamanho': 'Unico uso', 'material_composicao': 'Metal condutor', 'uso_observacao': 'Corte amplo', 'classificacao_processamento': 'descartavel_esteril', 'lote': 'CAT-026', 'responsavel': 'Sistema', 'estoque': 20, 'fornecedor': 'Catalogo Base', 'localizacao': 'Catalogo Padrao CME'
    },
    {
        'codigo_catalogo': 'CIR-027', 'codigo_qr': 'SYS-CIR-027', 'nome': 'Ponteira de cauterio', 'categoria': 'Energia', 'tipo': 'Alca', 'tamanho': 'Unico uso', 'material_composicao': 'Metal condutor', 'uso_observacao': 'Resseccao', 'classificacao_processamento': 'descartavel_esteril', 'lote': 'CAT-027', 'responsavel': 'Sistema', 'estoque': 20, 'fornecedor': 'Catalogo Base', 'localizacao': 'Catalogo Padrao CME'
    },
]


SYSTEM_KIT_CATALOG = [
    {
        'nome': 'Kit Cirurgia Geral Basico',
        'especialidade': 'Cirurgia Geral',
        'procedimento_cirurgico': 'Pequena cirurgia',
        'lacre': 'KIT-CG-001',
        'material_codes': ['CIR-001', 'CIR-003', 'CIR-005', 'CIR-009', 'CIR-017', 'CIR-019'],
    },
    {
        'nome': 'Kit Laparotomia',
        'especialidade': 'Cirurgia Geral',
        'procedimento_cirurgico': 'Laparotomia',
        'lacre': 'KIT-CG-002',
        'material_codes': ['CIR-001', 'CIR-004', 'CIR-006', 'CIR-010', 'CIR-014', 'CIR-021', 'CIR-024'],
    },
    {
        'nome': 'Kit Sutura e Hemostasia',
        'especialidade': 'Cirurgia Geral',
        'procedimento_cirurgico': 'Sutura de urgencia',
        'lacre': 'KIT-CG-003',
        'material_codes': ['CIR-003', 'CIR-005', 'CIR-011', 'CIR-013', 'CIR-017', 'CIR-018'],
    },
]


def ensure_system_material_catalog():
    today = timezone.now().date()
    validade = today + timedelta(days=365)

    created_count = 0
    for item in SYSTEM_MATERIAL_CATALOG:
        _, created = Material.objects.update_or_create(
            codigo_catalogo=item['codigo_catalogo'],
            defaults={
                'codigo_qr': item['codigo_qr'],
                'nome': item['nome'],
                'categoria': item['categoria'],
                'tipo': item.get('tipo', ''),
                'tamanho': item.get('tamanho', ''),
                'material_composicao': item.get('material_composicao', ''),
                'uso_observacao': item.get('uso_observacao', ''),
                'classificacao_processamento': item.get('classificacao_processamento', 'reutilizavel_esteril'),
                'lote': item['lote'],
                'data_esterilizacao': today,
                'status_esterilizacao': 'OK',
                'validade': validade,
                'responsavel': item['responsavel'],
                'estoque': item['estoque'],
                'fornecedor': item['fornecedor'],
                'localizacao': item['localizacao'],
                'origem_cadastro': 'sistema',
            },
        )
        if created:
            created_count += 1

    return created_count


def ensure_system_kit_catalog():
    ensure_system_material_catalog()

    materiais_por_codigo = {
        mat.codigo_catalogo: mat
        for mat in Material.objects.filter(codigo_catalogo__isnull=False)
    }

    created_count = 0
    for item in SYSTEM_KIT_CATALOG:
        kit, created = Kit.objects.get_or_create(
            nome=item['nome'],
            procedimento_cirurgico=item['procedimento_cirurgico'],
            defaults={
                'especialidade': item['especialidade'],
                'lacre': item['lacre'],
                'origem_cadastro': 'sistema',
                'codigo_qr': f"KIT-{item['lacre']}",
            }
        )

        materiais_do_kit = [
            materiais_por_codigo[codigo]
            for codigo in item['material_codes']
            if codigo in materiais_por_codigo
        ]
        if materiais_do_kit:
            kit.materiais.set(materiais_do_kit)

        if created:
            created_count += 1

    return created_count