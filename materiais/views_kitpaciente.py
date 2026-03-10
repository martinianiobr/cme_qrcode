from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from .models import Paciente, Kit, KitPaciente, Checklist, Material
from .forms import KitPacienteForm
from .aghu_integration import AGHUIntegration
import json

@login_required
def dashboard_kit_paciente(request):
    """Dashboard principal com processos ativos"""
    kits_paciente = KitPaciente.objects.all().order_by('-data_cirurgia')
    
    context = {
        'kits_paciente': kits_paciente,
        'title': 'Processos Cirúrgicos'
    }
    return render(request, 'materiais/dashboard_kit_paciente.html', context)

@login_required
def criar_kit_paciente(request):
    """Criar novo vínculo kit-paciente com integração AGHU"""
    if request.method == 'POST':
        form = KitPacienteForm(request.POST)
        if form.is_valid():
            kit_paciente = form.save()
            
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
        form = KitPacienteForm()
    
    return render(request, 'materiais/criar_kit_paciente.html', {'form': form})

@require_http_methods(["GET"])
def buscar_pacientes_aghu(request):
    """API para buscar pacientes no AGHU"""
    termo = request.GET.get('term', '').strip()
    
    if not termo:
        return JsonResponse({'pacientes': []})
    
    # Buscar pacientes no AGHU
    pacientes_aghu = AGHUIntegration.buscar_pacientes_por_nome(termo, limite=10)
    
    # Formatar para o select2
    resultados = []
    for paciente in pacientes_aghu:
        resultados.append({
            'id': paciente['prontuario'],
            'text': f"{paciente['nome']} ({paciente['prontuario']})",
            'prontuario': paciente['prontuario'],
            'nome': paciente['nome'],
            'data_nascimento': paciente['data_nascimento'],
            'cpf': paciente['cpf'],
            'telefone': paciente['telefone'],
            'convenio': paciente.get('convenio', ''),
            'leito': paciente.get('leito', ''),
            'medico_responsavel': paciente.get('medico_responsavel', ''),
            'fonte': 'AGHU'
        })
    
    return JsonResponse({'pacientes': resultados})

@login_required
def criar_paciente_aghu(request):
    """Criar paciente local baseado nos dados do AGHU"""
    if request.method == 'POST':
        prontuario = request.POST.get('prontuario')
        
        # Buscar paciente no AGHU
        paciente_aghu = AGHUIntegration.buscar_paciente_por_prontuario(prontuario)
        
        if not paciente_aghu:
            messages.error(request, 'Paciente não encontrado no AGHU!')
            return redirect('criar_kit_paciente')
        
        # Verificar se paciente já existe localmente
        if Paciente.objects.filter(prontuario=prontuario).exists():
            messages.info(request, 'Paciente já cadastrado localmente!')
            return redirect('criar_kit_paciente')
        
        # Criar paciente localmente
        paciente = Paciente.objects.create(
            nome=paciente_aghu['nome'],
            prontuario=paciente_aghu['prontuario'],
            data_nascimento=paciente_aghu['data_nascimento'],
            cpf=paciente_aghu['cpf'],
            telefone=paciente_aghu['telefone']
        )
        
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
        'processo_concluido': kit_paciente.processo_concluido()
    }
    
    return render(request, 'materiais/detalhes_kit_paciente.html', context)

@login_required
def checklist_etapa(request, kit_paciente_id, fase):
    """Acessar checklist específico com validação de acesso"""
    kit_paciente = get_object_or_404(KitPaciente, id=kit_paciente_id)
    
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
@csrf_exempt
def processar_qr_code(request):
    """Processar QR Code lido via mobile ou leitor"""
    try:
        data = json.loads(request.body)
        qr_data = data.get('qr_data', '').strip()
        
        if not qr_data:
            return JsonResponse({'status': 'error', 'message': 'QR Code vazio'})
        
        # Identificar tipo de QR Code
        if qr_data.startswith('KIT_PACIENTE_'):
            # QR Code de Kit do Paciente
            kit_paciente_id = qr_data.split('_')[2]
            return JsonResponse({
                'status': 'redirect',
                'url': f'/materiais/kit-paciente/{kit_paciente_id}/'
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
            
            # Marcar item como checado
            if checklist.marcar_item(material_id, request.user, 'qr_code'):
                material = Material.objects.get(id=material_id)
                return JsonResponse({
                    'status': 'success',
                    'message': f'Material {material.nome} marcado com sucesso!',
                    'item_id': material_id,
                    'progresso': checklist.progresso(),
                    'timestamp': timezone.now().isoformat()
                })
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
                    if checklist.marcar_item(material.id, request.user, 'qr_code'):
                        return JsonResponse({
                            'status': 'success',
                            'message': f'Material {material.nome} marcado com sucesso!',
                            'item_id': material.id,
                            'progresso': checklist.progresso()
                        })
                
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
