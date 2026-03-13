from django.shortcuts import render, get_object_or_404, redirect
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.views.decorators.http import require_http_methods
from django.db.models import Prefetch, Q
from .models import Paciente, Kit, KitPaciente, Checklist, Material
from .forms import KitPacienteForm
from .aghu_integration import AGHUIntegration
import json

User = get_user_model()


def _limitar_texto_linha(texto, tamanho=24):
    texto = (texto or '').strip()
    return texto[:tamanho]


def _gerar_zpl_etiquetas_materiais(materiais):
    """Gera ZPL para etiqueta 25x15mm (aprox 300x180 dots em 203dpi)."""
    etiquetas = []
    for material in materiais:
        qr_payload = f"MATERIAL_{material.id}"
        linha1 = _limitar_texto_linha(material.nome, 24)
        linha2 = _limitar_texto_linha(f"Lote: {material.lote}", 24)
        linha3 = _limitar_texto_linha(material.codigo_qr or qr_payload, 24)

        # 3 linhas de texto + QR pequeno para adesivo térmico.
        etiqueta = "\n".join([
            "^XA",
            "^PW300",
            "^LL180",
            "^CI28",
            "^FO12,12^BQN,2,4^FDLA," + qr_payload + "^FS",
            "^FO118,18^A0N,26,24^FD" + linha1 + "^FS",
            "^FO118,58^A0N,22,20^FD" + linha2 + "^FS",
            "^FO118,92^A0N,20,18^FD" + linha3 + "^FS",
            "^XZ",
        ])
        etiquetas.append(etiqueta)

    return "\n".join(etiquetas)


def _formatar_paciente_aghu(paciente_aghu):
    prontuario = str(paciente_aghu.get('prontuario', '')).strip()
    nome = (paciente_aghu.get('nome') or f'Paciente {prontuario}').strip()

    return {
        'id': prontuario,
        'text': f"{nome} ({prontuario})",
        'prontuario': prontuario,
        'nome': nome,
        'nome_mae': paciente_aghu.get('nome_mae', 'Nao informado'),
        'data_nascimento': paciente_aghu.get('data_nascimento'),
        'cpf': paciente_aghu.get('cpf', ''),
        'telefone': paciente_aghu.get('telefone', ''),
        'convenio': paciente_aghu.get('convenio', ''),
        'leito': paciente_aghu.get('leito', ''),
        'medico_responsavel': paciente_aghu.get('medico_responsavel', ''),
        'fonte': 'AGHU'
    }


def _importar_paciente_aghu(paciente_aghu):
    paciente, created = Paciente.objects.get_or_create(
        prontuario=str(paciente_aghu['prontuario']).strip(),
        defaults={
            'nome': (paciente_aghu.get('nome') or '').strip() or f"Paciente {paciente_aghu['prontuario']}",
            'nome_mae': (paciente_aghu.get('nome_mae') or 'Nao informado').strip(),
            'data_nascimento': paciente_aghu.get('data_nascimento') or timezone.now().date(),
            'cpf': paciente_aghu.get('cpf', ''),
            'telefone': paciente_aghu.get('telefone', ''),
            'fonte': 'AGHU',
        }
    )
    return paciente, created


def _gerar_cpf_contingencia(prontuario):
    digitos = ''.join(filter(str.isdigit, str(prontuario or '')))[-11:].zfill(11)
    return f'{digitos[:3]}.{digitos[3:6]}.{digitos[6:9]}-{digitos[9:]}'


def _importar_paciente_contingencia(prontuario):
    prontuario = str(prontuario).strip()
    paciente, created = Paciente.objects.get_or_create(
        prontuario=prontuario,
        defaults={
            'nome': f'Paciente {prontuario}',
            'nome_mae': 'Nao informado',
            'data_nascimento': timezone.now().date(),
            'cpf': _gerar_cpf_contingencia(prontuario),
            'telefone': '',
            'fonte': 'LOCAL',
        }
    )
    return paciente, created


def _resposta_item_checklist(checklist, material, ja_checado=False):
    return {
        'status': 'success',
        'message': (
            f'Material {material.nome} ja estava conferido.'
            if ja_checado else
            f'Material {material.nome} marcado com sucesso!'
        ),
        'item_id': material.id,
        'material_nome': material.nome,
        'material_codigo': material.codigo_qr,
        'progresso': checklist.progresso(),
        'itens_checados': checklist.itens_checados(),
        'total_itens': checklist.total_itens(),
        'concluido': checklist.concluido,
        'already_checked': ja_checado,
        'timestamp': timezone.now().isoformat(),
    }

@login_required
def dashboard_kit_paciente(request):
    """Dashboard principal com processos ativos"""
    kits_paciente = KitPaciente.objects.select_related('paciente', 'kit').prefetch_related(
        Prefetch('checklists', queryset=Checklist.objects.order_by('fase'))
    ).order_by('-data_cirurgia')

    busca = request.GET.get('q', '').strip()
    status = request.GET.get('status', '').strip()
    data_cirurgia = request.GET.get('data', '').strip()

    if busca:
        kits_paciente = kits_paciente.filter(
            Q(paciente__nome__icontains=busca) |
            Q(paciente__prontuario__icontains=busca) |
            Q(kit__nome__icontains=busca)
        )

    if status:
        kits_paciente = kits_paciente.filter(status=status)
    else:
        # Por padrão, exibe apenas processos em andamento para operação diária.
        kits_paciente = kits_paciente.exclude(status__in=['concluido', 'cancelado'])

    if data_cirurgia:
        kits_paciente = kits_paciente.filter(data_cirurgia__date=data_cirurgia)
    
    context = {
        'kits_paciente': kits_paciente,
        'title': 'Processos Cirúrgicos',
        'phase_choices': Checklist.FASE_CHOICES,
    }
    return render(request, 'materiais/dashboard_kit_paciente.html', context)


@login_required
def auditoria_fluxos(request):
    """Ambiente de auditoria de conferências por usuário e fluxo."""
    if not request.user.is_staff:
        raise PermissionDenied('Acesso restrito aos administradores do sistema.')

    kits_paciente = KitPaciente.objects.select_related(
        'paciente', 'kit', 'cancelado_por'
    ).prefetch_related(
        Prefetch('checklists', queryset=Checklist.objects.order_by('fase'))
    ).order_by('-data_cirurgia')

    busca = request.GET.get('q', '').strip()
    status = request.GET.get('status', '').strip()
    usuario_id = request.GET.get('usuario', '').strip()
    data_inicio = request.GET.get('data_inicio', '').strip()
    data_fim = request.GET.get('data_fim', '').strip()

    if busca:
        kits_paciente = kits_paciente.filter(
            Q(paciente__nome__icontains=busca)
            | Q(paciente__prontuario__icontains=busca)
            | Q(kit__nome__icontains=busca)
        )

    if status:
        kits_paciente = kits_paciente.filter(status=status)

    if data_inicio:
        kits_paciente = kits_paciente.filter(data_cirurgia__date__gte=data_inicio)

    if data_fim:
        kits_paciente = kits_paciente.filter(data_cirurgia__date__lte=data_fim)

    kits_lista = list(kits_paciente)

    usuarios_ids = set()
    for kit_paciente in kits_lista:
        for checklist in kit_paciente.checklists.all():
            for item in (checklist.itens or {}).values():
                usuario_item = item.get('usuario')
                if item.get('checado') and usuario_item:
                    try:
                        usuarios_ids.add(int(usuario_item))
                    except (TypeError, ValueError):
                        continue

    usuarios_map = User.objects.in_bulk(usuarios_ids)
    usuarios_filtro = User.objects.filter(id__in=usuarios_ids).order_by('first_name', 'username')

    conferencias = []
    usuario_id_int = None
    if usuario_id:
        try:
            usuario_id_int = int(usuario_id)
        except ValueError:
            usuario_id_int = None

    for kit_paciente in kits_lista:
        for checklist in kit_paciente.checklists.all():
            for item in (checklist.itens or {}).values():
                if not item.get('checado'):
                    continue

                usuario_item = item.get('usuario')
                try:
                    usuario_item_int = int(usuario_item) if usuario_item is not None else None
                except (TypeError, ValueError):
                    usuario_item_int = None

                if usuario_id_int and usuario_item_int != usuario_id_int:
                    continue

                usuario_obj = usuarios_map.get(usuario_item_int) if usuario_item_int else None
                data_item = parse_datetime(item.get('data') or '')
                if data_item is not None and timezone.is_aware(data_item):
                    data_item = timezone.localtime(data_item)

                conferencias.append({
                    'kit_paciente': kit_paciente,
                    'checklist': checklist,
                    'material_nome': item.get('material_nome', 'Material'),
                    'material_codigo': item.get('material_codigo', '-'),
                    'metodo': item.get('metodo', 'manual'),
                    'usuario': usuario_obj,
                    'usuario_id': usuario_item_int,
                    'data_conferencia': data_item,
                })

    data_minima = timezone.make_aware(datetime.min)
    conferencias.sort(
        key=lambda x: x['data_conferencia'] or data_minima,
        reverse=True,
    )

    context = {
        'kits_total': len(kits_lista),
        'conferencias_total': len(conferencias),
        'conferencias': conferencias,
        'usuarios_filtro': usuarios_filtro,
        'phase_choices': Checklist.FASE_CHOICES,
    }
    return render(request, 'materiais/auditoria_fluxos.html', context)

@login_required
def criar_kit_paciente(request):
    """Criar novo vínculo kit-paciente com integração AGHU"""
    if request.method == 'POST':
        form = KitPacienteForm(request.POST)
        if form.is_valid():
            kit_paciente = form.save(commit=False)
            if not kit_paciente.data_cirurgia:
                kit_paciente.data_cirurgia = timezone.now()
            kit_paciente.save()
            form.save_m2m()

            # ESSENCIAL: Criar automaticamente as 3 etapas
            for fase, _ in Checklist.FASE_CHOICES:
                checklist = Checklist.objects.create(
                    kit_paciente=kit_paciente,
                    fase=fase,
                    usuario_responsavel=request.user
                )
                checklist.gerar_itens_automaticamente()

            messages.success(request, f'Kit do paciente {kit_paciente.paciente.nome} criado com sucesso!')
            return redirect('detalhes_kit_paciente', kit_paciente.id)
    else:
        initial = {}
        paciente_id = request.GET.get('paciente_id')
        kit_id = request.GET.get('kit_id')
        if paciente_id and Paciente.objects.filter(pk=paciente_id).exists():
            initial['paciente'] = paciente_id
        if kit_id and Kit.objects.filter(pk=kit_id).exists():
            initial['kit'] = kit_id
        form = KitPacienteForm(initial=initial)

    # Contexto extra para exibição do kit selecionado
    ctx = {'form': form}
    kit_id = request.GET.get('kit_id') or request.POST.get('kit')
    if kit_id:
        try:
            ctx['kit_selecionado'] = Kit.objects.get(pk=kit_id)
        except Kit.DoesNotExist:
            pass
    return render(request, 'materiais/criar_kit_paciente.html', ctx)

@require_http_methods(["GET"])
@login_required
def buscar_pacientes_aghu(request):
    """API para buscar pacientes no AGHU"""
    termo = request.GET.get('term', '').strip()
    
    if not termo:
        return JsonResponse({'pacientes': []})
    
    resultados = []
    # se termo é numérico, tentar prontuário primeiro
    if termo.isdigit():
        paciente_aghu = AGHUIntegration.buscar_paciente_por_prontuario(termo)
        if paciente_aghu:
            resultados.append(_formatar_paciente_aghu(paciente_aghu))
            return JsonResponse({'pacientes': resultados})
    
    # Buscar por nome ou trecho
    pacientes_aghu = AGHUIntegration.buscar_pacientes_por_nome(termo, limite=10)
    
    # Formatar para o select2
    for paciente in pacientes_aghu:
        resultados.append(_formatar_paciente_aghu(paciente))

    if not resultados and termo.isdigit():
        resultados.append({
            'id': termo,
            'text': f'Nao encontrado no AGHU - usar contingencia ({termo})',
            'prontuario': termo,
            'nome': f'Paciente {termo}',
            'nome_mae': 'Nao informado',
            'data_nascimento': None,
            'fonte': 'CONTINGENCIA'
        })
    
    return JsonResponse({'pacientes': resultados})

@login_required
def criar_paciente_aghu(request):
    """Criar paciente local baseado nos dados do AGHU

    Se chamado via AJAX (XHR) responde com JSON contendo id/text do paciente,
    caso contrário redireciona de volta à página de novo processo.
    """
    if request.method == 'POST':
        prontuario = request.POST.get('prontuario')
        # Buscar paciente no AGHU
        paciente_aghu = AGHUIntegration.buscar_paciente_por_prontuario(prontuario)
        
        if not paciente_aghu:
            # fallback de contingencia para nao bloquear o fluxo assistencial
            if prontuario and str(prontuario).isdigit():
                paciente, created = _importar_paciente_contingencia(prontuario)
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({
                        'id': paciente.id,
                        'text': f"{paciente.nome} ({paciente.prontuario})",
                        'prontuario': paciente.prontuario,
                        'nome': paciente.nome,
                        'nome_mae': paciente.nome_mae,
                        'data_nascimento': paciente.data_nascimento,
                        'contingencia': True,
                    })
                messages.warning(request, 'Paciente criado por contingência (AGHU não retornou dados).')
                return redirect('criar_kit_paciente')

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'error': 'Paciente não encontrado no AGHU!'}, status=404)
            messages.error(request, 'Paciente não encontrado no AGHU!')
            return redirect('criar_kit_paciente')
        
        # Verificar se paciente já existe localmente
        paciente, created = _importar_paciente_aghu(paciente_aghu)
        if not created:
            # já existia
            msg = 'Paciente já cadastrado localmente!'
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'id': paciente.id,
                    'text': f"{paciente.nome} ({paciente.prontuario})",
                    'prontuario': paciente.prontuario,
                    'nome': paciente.nome,
                    'nome_mae': paciente.nome_mae,
                    'data_nascimento': paciente.data_nascimento,
                    'existing': True,
                })
            messages.info(request, msg)
            return redirect('criar_kit_paciente')
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'id': paciente.id,
                'text': f"{paciente.nome} ({paciente.prontuario})",
                'prontuario': paciente.prontuario,
                'nome': paciente.nome,
                'nome_mae': paciente.nome_mae,
                'data_nascimento': paciente.data_nascimento,
            })
        
        messages.success(request, f'Paciente {paciente.nome} importado do AGHU com sucesso!')
        return redirect('criar_kit_paciente')
    
    return render(request, 'materiais/buscar_paciente_aghu.html')

@login_required
def detalhes_kit_paciente(request, kit_paciente_id):
    """Detalhes do processo do paciente com validação de etapas"""
    kit_paciente = get_object_or_404(KitPaciente, id=kit_paciente_id)
    
    # Buscar ou criar checklists para cada etapa
    checklists = {}
    for fase, nome_fase in Checklist.FASE_CHOICES:
        checklist, created = Checklist.objects.get_or_create(
            kit_paciente=kit_paciente,
            fase=fase,
            defaults={'usuario_responsavel': request.user}
        )
        if created:
            checklist.gerar_itens_automaticamente()
        
        checklists[fase] = {
            'obj': checklist,
            'pode_acessar': checklist.pode_acessar(),
            'progresso': checklist.progresso(),
            'itens_checados': checklist.itens_checados(),
            'total_itens': checklist.total_itens()
        }
    
    context = {
        'kit_paciente': kit_paciente,
        'checklists': checklists,
        'proxima_etapa': kit_paciente.proxima_etapa(),
        'processo_concluido': kit_paciente.processo_concluido(),
        'phase_choices': Checklist.FASE_CHOICES,
        'hoje': timezone.now().date(),
    }
    
    return render(request, 'materiais/detalhes_kit_paciente.html', context)

@login_required
def checklist_etapa(request, kit_paciente_id, fase):
    """Acessar checklist específico com validação de acesso"""
    kit_paciente = get_object_or_404(KitPaciente, id=kit_paciente_id)

    if kit_paciente.status == 'cancelado':
        messages.error(request, 'Este processo está cancelado e não permite novas conferências.')
        return redirect('detalhes_kit_paciente', kit_paciente_id)
    
    # VALIDAÇÃO ESSENCIAL: Verificar se pode acessar esta etapa
    checklist = get_object_or_404(Checklist, kit_paciente=kit_paciente, fase=fase)
    
    if not checklist.pode_acessar():
        messages.error(request, f'Você não pode acessar {checklist.get_fase_display()} ainda!')
        return redirect('detalhes_kit_paciente', kit_paciente_id)
    
    # Salvar checklist ativo na sessão para QR Code
    request.session['checklist_ativo'] = checklist.id
    request.session['kit_paciente_ativo'] = kit_paciente_id
    
    context = {
        'kit_paciente': kit_paciente,
        'checklist': checklist,
        'materiais': kit_paciente.kit.materiais.all(),
        'itens_json': json.dumps(checklist.itens)
    }
    
    return render(request, 'materiais/checklist_etapa.html', context)

@login_required
@require_http_methods(["POST"])
def processar_qr_code(request):
    """Processar QR Code lido via mobile ou leitor"""
    try:
        data = json.loads(request.body)
        qr_data = data.get('qr_data', '').strip()
        
        if not qr_data:
            return JsonResponse({'status': 'error', 'message': 'QR Code vazio'})
        
        # Identificar tipo de QR Code
        if qr_data.startswith('KIT_PACIENTE_'):
            # QR Code de Kit do Paciente - direciona para a página de detalhes do processo
            kit_paciente_id = qr_data.split('_')[2]
            return JsonResponse({
                'status': 'redirect',
                'url': f'/materiais/processos/{kit_paciente_id}/'
            })
        
        elif qr_data.startswith('MATERIAL_'):
            # QR Code de Material para marcar no checklist
            material_id = qr_data.split('_')[1]
            checklist_id = request.session.get('checklist_ativo')
            
            if not checklist_id:
                return JsonResponse({
                    'status': 'error', 
                    'message': 'Nenhum checklist ativo'
                })
            
            checklist = Checklist.objects.get(id=checklist_id)
            material = Material.objects.get(id=material_id)
            ja_checado = checklist.itens.get(str(material_id), {}).get('checado', False)
            
            # Marcar item como checado
            if ja_checado or checklist.marcar_item(material_id, request.user, 'qr_code'):
                return JsonResponse(_resposta_item_checklist(checklist, material, ja_checado))
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Material não encontrado neste checklist'
                })
        
        else:
            # Tentar encontrar por código QR direto
            try:
                material = Material.objects.get(codigo_qr=qr_data)
                checklist_id = request.session.get('checklist_ativo')
                
                if checklist_id:
                    checklist = Checklist.objects.get(id=checklist_id)
                    ja_checado = checklist.itens.get(str(material.id), {}).get('checado', False)
                    if ja_checado or checklist.marcar_item(material.id, request.user, 'qr_code'):
                        return JsonResponse(_resposta_item_checklist(checklist, material, ja_checado))
                
                return JsonResponse({
                    'status': 'info',
                    'message': f'Material {material.nome} encontrado',
                    'material_id': material.id
                })
                
            except Material.DoesNotExist:
                return JsonResponse({
                    'status': 'error',
                    'message': 'QR Code não reconhecido'
                })
    
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Erro ao processar QR Code: {str(e)}'
        })

@login_required
def marcar_item_manual(request, checklist_id, material_id):
    """Marcar item manualmente (alternativa ao QR Code)"""
    checklist = get_object_or_404(Checklist, id=checklist_id)
    material = get_object_or_404(Material, id=material_id)
    
    if checklist.marcar_item(material_id, request.user, 'manual'):
        messages.success(request, f'{material.nome} marcado com sucesso!')
    else:
        messages.error(request, 'Erro ao marcar material')
    
    return redirect('checklist_etapa', checklist.kit_paciente.id, checklist.fase)

@login_required
def scan_qr_code(request):
    """Página mobile para scanning"""
    checklist_id = request.session.get('checklist_ativo')
    kit_paciente_id = request.session.get('kit_paciente_ativo')
    
    context = {
        'checklist_id': checklist_id,
        'kit_paciente_id': kit_paciente_id
    }
    
    if checklist_id:
        try:
            checklist = Checklist.objects.get(id=checklist_id)
            context.update({
                'checklist': checklist,
                'kit_paciente': checklist.kit_paciente
            })
        except Checklist.DoesNotExist:
            pass
    
    return render(request, 'materiais/scan_qr_code.html', context)

@login_required
def relatorio_final(request, kit_paciente_id):
    """Relatório final do processo completo"""
    kit_paciente = get_object_or_404(KitPaciente, id=kit_paciente_id)
    
    # Buscar todos os checklists
    checklists = kit_paciente.checklists.all().order_by('fase')
    
    # Calcular estatísticas
    total_itens = sum(checklist.total_itens() for checklist in checklists)
    itens_checados = sum(checklist.itens_checados() for checklist in checklists)
    taxa_conformidade = int((itens_checados / total_itens) * 100) if total_itens > 0 else 0
    
    context = {
        'kit_paciente': kit_paciente,
        'checklists': checklists,
        'total_itens': total_itens,
        'itens_checados': itens_checados,
        'taxa_conformidade': taxa_conformidade,
        'processo_concluido': kit_paciente.processo_concluido()
    }
    
    return render(request, 'materiais/relatorio_final.html', context)

@login_required
@require_http_methods(["POST"])
def concluir_etapa(request, checklist_id):
    """Concluir etapa manualmente"""
    checklist = get_object_or_404(Checklist, id=checklist_id)
    
    if checklist.todos_itens_checados():
        checklist.concluir()
        messages.success(request, f'{checklist.get_fase_display()} concluído com sucesso!')
    else:
        messages.warning(request, 'Existem itens não marcados nesta etapa!')
    
    return redirect('detalhes_kit_paciente', checklist.kit_paciente.id)


@login_required
def imprimir_etiquetas_materiais(request, kit_paciente_id):
    """Tela de impressão de etiquetas QR por material (fluxo KitPaciente)."""
    kit_paciente = get_object_or_404(KitPaciente.objects.select_related('paciente', 'kit'), id=kit_paciente_id)
    materiais = list(kit_paciente.kit.materiais.all().order_by('nome'))

    if request.GET.get('formato') == 'zpl':
        zpl = _gerar_zpl_etiquetas_materiais(materiais)
        resposta = HttpResponse(zpl, content_type='text/plain; charset=utf-8')
        resposta['Content-Disposition'] = (
            f'attachment; filename="etiquetas_kit_paciente_{kit_paciente.id}.zpl"'
        )
        return resposta

    context = {
        'kit_paciente': kit_paciente,
        'materiais': materiais,
        'total_etiquetas': len(materiais),
        'zpl_url': reverse('imprimir_etiquetas_materiais', args=[kit_paciente.id]) + '?formato=zpl',
    }
    return render(request, 'materiais/imprimir_etiquetas_materiais.html', context)


@login_required
@require_http_methods(["POST"])
def excluir_kit_paciente(request, kit_paciente_id):
    """Cancela um processo cirúrgico sem excluir dados para manter rastreabilidade."""
    kit_paciente = get_object_or_404(KitPaciente, id=kit_paciente_id)
    if kit_paciente.status == 'cancelado':
        messages.info(request, 'Este processo já estava cancelado.')
        return redirect('detalhes_kit_paciente', kit_paciente.id)

    motivo_cancelamento = (request.POST.get('motivo_cancelamento') or '').strip()
    if not motivo_cancelamento:
        messages.error(request, 'Informe o motivo do cancelamento para continuar.')
        return redirect('detalhes_kit_paciente', kit_paciente.id)

    nome_paciente = kit_paciente.paciente.nome
    kit_paciente.cancelar(request.user, motivo_cancelamento)

    # Limpa sessão de checklist ativo caso o processo cancelado estivesse em uso.
    if request.session.get('kit_paciente_ativo') == kit_paciente.id:
        request.session.pop('kit_paciente_ativo', None)
        request.session.pop('checklist_ativo', None)

    messages.success(request, f'Processo cirúrgico de {nome_paciente} foi cancelado com sucesso.')
    return redirect('dashboard_kit_paciente')
