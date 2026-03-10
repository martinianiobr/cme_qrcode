from django.shortcuts import render, redirect, get_object_or_404
from .forms import MaterialForm, KitForm, ChecklistForm
from .models import Material, Kit, Checklist, ChecklistItem, LeituraQR
from django.core.files.base import ContentFile
from io import BytesIO
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils import timezone

# class-based imports
from django.views.generic import ListView, CreateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from .aghu_service import buscar_paciente_por_prontuario, buscar_pacientes_por_nome



# ------------------ MATERIAIS ------------------
class MaterialListView(LoginRequiredMixin, ListView):
    model = Material
    template_name = 'materiais/lista_materiais.html'
    context_object_name = 'materiais'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get('q')
        if q:
            qs = (qs.filter(nome__icontains=q) | qs.filter(codigo_qr__icontains=q)).distinct()
        return qs

class MaterialCreateView(LoginRequiredMixin, CreateView):
    model = Material
    form_class = MaterialForm
    template_name = 'materiais/cadastrar_material.html'
    success_url = reverse_lazy('lista_materiais')

    def form_valid(self, form):
        messages.success(self.request, 'Material cadastrado com sucesso.')
        return super().form_valid(form)


# ------------------ KITS ------------------
class KitListView(LoginRequiredMixin, ListView):
    model = Kit
    template_name = 'materiais/lista_kits.html'
    context_object_name = 'kits'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(nome__icontains=q)
        return qs

class KitCreateView(LoginRequiredMixin, CreateView):
    model = Kit
    form_class = KitForm
    template_name = 'materiais/cadastrar_kit.html'
    success_url = reverse_lazy('lista_kits')

    def form_valid(self, form):
        messages.success(self.request, 'Kit cadastrado com sucesso.')
        return super().form_valid(form)


# ------------------ CHECKLISTS ------------------
class ChecklistListView(LoginRequiredMixin, ListView):
    model = Checklist
    template_name = 'materiais/lista_checklists.html'
    context_object_name = 'checklists'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get('q')
        fase = self.request.GET.get('fase')
        
        # CORREÇÃO: Filtrar apenas checklists que têm kit_paciente
        qs = qs.filter(kit_paciente__isnull=False)
        
        if q:
            qs = qs.filter(kit_paciente__paciente__nome__icontains=q).distinct()
        if fase in ['pre', 'intra', 'pos']:
            qs = qs.filter(fase=fase)
        return qs

class ChecklistCreateView(LoginRequiredMixin, CreateView):
    model = Checklist
    form_class = ChecklistForm
    template_name = 'materiais/cadastrar_checklist.html'
    success_url = reverse_lazy('lista_checklists')

    def form_valid(self, form):
        # assign current user before saving
        checklist = form.save(commit=False)

        prontuario = form.cleaned_data.get('prontuario')
        if prontuario:
            dados = buscar_paciente_por_prontuario(prontuario)
            if dados:
                checklist.paciente_prontuario = dados["prontuario"]
                checklist.paciente_nome = dados["nome"]
                checklist.paciente = dados["nome"]
            else:
                messages.warning(self.request, 'Prontuário não encontrado no AGHU. Checklist será salvo apenas com o nome informado.')

        checklist.conferido_por = self.request.user
        checklist.save()
        # prepopulate items from the kit
        for mat in checklist.kit.materiais.all():
            ChecklistItem.objects.get_or_create(checklist=checklist, material=mat)
        messages.success(self.request, 'Checklist criado com sucesso.')
        return redirect(self.success_url)



@login_required
def detalhe_checklist(request, pk):
    checklist = get_object_or_404(Checklist, pk=pk)
    itens = ChecklistItem.objects.filter(checklist=checklist).select_related('material')
    total = itens.count()
    checked = itens.filter(conferido=True).count()
    percent = int((checked / total * 100) if total else 0)
    return render(request, 'materiais/detalhe_checklist.html', {
        'checklist': checklist,
        'itens': itens,
        'total': total,
        'checked': checked,
        'percent': percent,
        'hoje': timezone.now().date(),
    })


@login_required
def dashboard(request):
    data = {
        'total_materiais': Material.objects.count(),
        'total_kits': Kit.objects.count(),
        'total_checklists': Checklist.objects.count(),
    }
    return render(request, 'materiais/dashboard.html', data)


@csrf_exempt
@login_required
def scan_qr(request):
    # endpoint expecting JSON {"codigo": "..."}
    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido'}, status=405)

    try:
        import json
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({'error': 'JSON inválido'}, status=400)

    codigo = data.get('codigo')
    checklist_id = data.get('checklist_id')
    if not codigo:
        return JsonResponse({'error': 'Código ausente'}, status=400)

    checklist = None
    if checklist_id:
        try:
            checklist = Checklist.objects.get(pk=checklist_id)
        except Checklist.DoesNotExist:
            return JsonResponse({'error': 'Checklist não encontrado'}, status=404)

    usuario = request.user
    # busca material ou kit
    material = Kit_obj = None
    try:
        material = Material.objects.get(codigo_qr=codigo)
    except Material.DoesNotExist:
        try:
            Kit_obj = Kit.objects.get(codigo_qr=codigo)
        except Kit.DoesNotExist:
            # item não cadastrado
            LeituraQR.objects.create(usuario=usuario, acao='forasteiro', observacao=codigo)
            return JsonResponse({'error': 'Item não cadastrado'}, status=404)

    if Kit_obj:
        # valida se o checklist fornecido (se houver) corresponde ao kit
        if checklist and checklist.kit != Kit_obj:
            return JsonResponse({'error': 'Kit não corresponde ao checklist atual'}, status=400)
        # para leitura de kit, apenas logar e não conferir cada item
        if not checklist:
            checklist = Checklist.objects.filter(kit=Kit_obj).order_by('-data_inicio').first()
        LeituraQR.objects.create(checklist=checklist, kit=Kit_obj, usuario=usuario, acao='kit')
        return JsonResponse({'success': True, 'tipo': 'kit'})
    else:
        # validações
        now = timezone.now().date()
        if material.validade < now:
            return JsonResponse({'error': 'Material vencido'}, status=400)
        if material.status_esterilizacao != 'OK':
            return JsonResponse({'error': 'Material não esterilizado'}, status=400)
        if material.estoque <= 0:
            return JsonResponse({'error': 'Sem estoque'}, status=400)

        # encontrar checklist relevante
        if checklist:
            # se veio checklist explícito, garantir que o material pertence ao kit desse checklist
            if not checklist.kit.materiais.filter(pk=material.pk).exists():
                LeituraQR.objects.create(usuario=usuario, material=material, acao='forasteiro')
                return JsonResponse({'error': 'Material não pertence ao checklist atual'}, status=400)
        else:
            checklist = Checklist.objects.filter(kit__materiais=material).order_by('-data_inicio').first()
            if not checklist:
                LeituraQR.objects.create(usuario=usuario, material=material, acao='forasteiro')
                return JsonResponse({'error': 'Material não vinculado a nenhum checklist ativo'}, status=404)

        item, _ = ChecklistItem.objects.get_or_create(checklist=checklist, material=material)
        item.conferido = True
        item.data_conferencia = timezone.now()
        item.save()
        LeituraQR.objects.create(checklist=checklist, material=material, usuario=usuario, acao='conferido')
        
        # Verifica se o checklist foi concluído
        if checklist.verificar_conclusao():
            return JsonResponse({
                'success': True, 
                'tipo': 'material',
                'concluido': True,
                'message': 'Checklist concluído com sucesso!'
            })
        
        return JsonResponse({'success': True, 'tipo': 'material'})


@login_required
def buscar_pacientes_aghu(request):
    """
    API para buscar pacientes no AGHU por nome ou prontuário
    """
    termo = request.GET.get('termo', '').strip()
    tipo = request.GET.get('tipo', 'nome')  # 'nome' ou 'prontuario'
    
    if not termo:
        return JsonResponse({'error': 'Termo de busca não informado'}, status=400)
    
    try:
        if tipo == 'prontuario':
            prontuario = int(termo)
            paciente = buscar_paciente_por_prontuario(prontuario)
            if paciente:
                return JsonResponse({'pacientes': [paciente]})
            else:
                return JsonResponse({'pacientes': []})
        else:
            pacientes = buscar_pacientes_por_nome(termo, limite=10)
            return JsonResponse({'pacientes': pacientes})
    except Exception as e:
        return JsonResponse({'error': f'Erro na busca: {str(e)}'}, status=500)


@login_required
def gerar_qr_codes_para_impressao(request, checklist_id):
    """
    Gera página com QR codes de todos os materiais de um checklist para impressão
    """
    checklist = get_object_or_404(Checklist, pk=checklist_id)
    materiais = checklist.kit.materiais.all()
    
    context = {
        'checklist': checklist,
        'materiais': materiais,
    }
    return render(request, 'materiais/imprimir_qrcodes.html', context)
