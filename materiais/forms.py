from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils import timezone
from .models import Material, Kit, Paciente, KitPaciente, Checklist

# ---------------------------------------------------------------------------
# Catálogo de especialidades cirúrgicas e seus procedimentos
# ---------------------------------------------------------------------------
ESPECIALIDADES_PROCEDIMENTOS = {
    'Cirurgia Geral': [
        'Apendicectomia',
        'Colecistectomia Laparoscópica',
        'Herniorrafia Inguinal',
        'Herniorrafia Ventral / Incisional',
        'Laparotomia Exploradora',
        'Colostomia / Ileostomia',
        'Gastrostomia / Gastrojejunostomia',
        'Esplenectomia',
        'Hemorroidectomia',
        'Tireoidectomia',
        'Mastectomia',
        'Fundoplicatura (Nissen)',
        'Gastrectomia',
    ],
    'Cirurgia Vascular': [
        'Safenectomia',
        'Fístula Arteriovenosa (FAV)',
        'Bypass Aortofemoral',
        'Amputação de Membro Inferior',
        'Endarterectomia de Carótida',
        'Correção de Aneurisma de Aorta',
    ],
    'Ortopedia e Traumatologia': [
        'Artroscopia de Joelho',
        'Artroscopia de Ombro',
        'Artroplastia de Quadril (ATQ)',
        'Artroplastia de Joelho (ATJ)',
        'Osteossíntese de Fêmur',
        'Osteossíntese de Tíbia',
        'Osteossíntese de Punho / Rádio',
        'Correção de Hallux Valgus',
        'Amputação de Dedo / Raio',
    ],
    'Ginecologia e Obstetrícia': [
        'Histerectomia Abdominal',
        'Histerectomia Vaginal',
        'Laparoscopia Diagnóstica / Cirúrgica',
        'Miomectomia',
        'Ooforectomia / Salpingooforectomia',
        'Curetagem Uterina',
        'Cesariana',
        'Salpingectomia',
        'Colporrafia Anterior / Posterior',
    ],
    'Urologia': [
        'Nefrectomia',
        'Cistoscopia',
        'Prostatectomia Radical',
        'Nefrolitotomia Percutânea (NLPC)',
        'Ureterolitotomia',
        'Ressecção Transuretral de Próstata (RTUP)',
        'Orquiectomia',
        'Circuncisão',
        'Pieloplastia',
    ],
    'Neurocirurgia': [
        'Craniotomia',
        'Derivação Ventricular (DVE / DVP)',
        'Laminectomia',
        'Discectomia Lombar',
        'Microdiscectomia',
        'Clipagem de Aneurisma Cerebral',
    ],
    'Otorrinolaringologia': [
        'Adenoidectomia',
        'Tonsilectomia (Amigdalectomia)',
        'Septoplastia',
        'Miringotomia c/ Tubo de Ventilação',
        'Sinusectomia Endoscópica (CENS)',
        'Parotidectomia',
        'Laringoscopia Cirúrgica',
    ],
    'Oftalmologia': [
        'Facoemulsificação (Catarata)',
        'Trabeculectomia (Glaucoma)',
        'Vitrectomia',
        'Correção de Estrabismo',
        'Pterígio',
        'Transplante de Córnea',
    ],
    'Cirurgia Plástica': [
        'Rinoplastia',
        'Mamoplastia Redutora',
        'Mamoplastia de Aumento',
        'Abdominoplastia',
        'Blefaroplastia',
        'Ritidoplastia (Facelift)',
        'Lipoaspiração',
        'Reconstrução Mamária',
    ],
    'Cirurgia Pediátrica': [
        'Herniorrafia Congênita',
        'Piloromiotomia',
        'Orquidopexia',
        'Apendicectomia Pediátrica',
        'Hipospádia',
    ],
    'Cirurgia Torácica': [
        'Pneumonectomia',
        'Lobectomia Pulmonar',
        'Toracoscopia (VATS)',
        'Correção de Pectus Excavatum',
        'Decorticação Pleural',
    ],
    'Proctologia': [
        'Retossigmoidectomia',
        'Colectomia Direita / Esquerda',
        'Fistulotomia Anal',
        'Hemorroidectomia',
        'Esfincterotomia Lateral Interna',
    ],
}

ESPECIALIDADE_CHOICES = [('', '---------')] + [(e, e) for e in ESPECIALIDADES_PROCEDIMENTOS]

# Lista plana de todos os procedimentos (para o Select server-side)
_all_procs: list[str] = []
for _procs in ESPECIALIDADES_PROCEDIMENTOS.values():
    for _p in _procs:
        if _p not in _all_procs:
            _all_procs.append(_p)
PROCEDIMENTO_CHOICES = [('', '---------')] + [(_p, _p) for _p in _all_procs]


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = ['nome', 'prontuario', 'nome_mae', 'data_nascimento', 'cpf', 'telefone']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome completo'}),
            'prontuario': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prontuário AGHU'}),
            'nome_mae': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome completo da mãe'}),
            'data_nascimento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'cpf': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '000.000.000-00'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(00) 00000-0000'}),
        }

class KitPacienteForm(forms.ModelForm):
    class Meta:
        model = KitPaciente
        fields = ['paciente', 'kit', 'data_cirurgia']
        widgets = {
            'paciente': forms.Select(attrs={'class': 'form-control'}),
            'kit': forms.Select(attrs={'class': 'form-control'}),
            'data_cirurgia': forms.DateTimeInput(attrs={
                'class': 'form-control', 
                'type': 'datetime-local'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['paciente'].queryset = Paciente.objects.all().order_by('nome')
        self.fields['kit'].queryset = Kit.objects.all().order_by('especialidade', 'procedimento_cirurgico', 'nome')
        self.fields['data_cirurgia'].required = False
        self.fields['kit'].label_from_instance = lambda obj: (
            (
                f"{obj.nome} - {obj.procedimento_cirurgico}"
                if obj.procedimento_cirurgico else obj.nome
            )
            + (
                f" | gerado em {obj.criado_em.strftime('%d/%m/%Y %H:%M')}"
                if obj.criado_em else ""
            )
            + (
                f" por {obj.criado_por.get_full_name() or obj.criado_por.username}"
                if obj.criado_por else ""
            )
        )
        
        # Adicionar opções de busca
        self.fields['paciente'].widget.attrs.update({
            'data-live-search': 'true',
            'placeholder': 'Selecione o paciente...'
        })
        self.fields['kit'].widget.attrs.update({
            'data-live-search': 'true',
            'placeholder': 'Selecione o kit cirúrgico...'
        })

class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = [
            'codigo_catalogo', 'nome', 'categoria', 'tipo', 'tamanho', 'material_composicao',
            'classificacao_processamento', 'uso_observacao', 'lote', 'data_esterilizacao',
            'status_esterilizacao', 'validade', 'responsavel', 'estoque', 'fornecedor', 'localizacao'
        ]
        widgets = {
            'codigo_catalogo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex.: CIR-028'}),
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Nome'}),
            'categoria': forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Categoria'}),
            'tipo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tipo / variação'}),
            'tamanho': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tamanho'}),
            'material_composicao': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Material de fabricação'}),
            'classificacao_processamento': forms.Select(attrs={'class': 'form-select'}),
            'uso_observacao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Uso clínico ou observações operacionais'}),
            'lote': forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Lote'}),
            'data_esterilizacao': forms.DateInput(attrs={'class': 'form-control', 'type':'date'}),
            'status_esterilizacao': forms.Select(attrs={'class': 'form-select'}),
            'validade': forms.DateInput(attrs={'class': 'form-control', 'type':'date'}),
            'responsavel': forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Responsável'}),
            'estoque': forms.NumberInput(attrs={'class': 'form-control', 'min':'0', 'placeholder':'Quantidade'}),
            'fornecedor': forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Fornecedor'}),
            'localizacao': forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Localização'}),
        }

    def clean_estoque(self):
        estoque = self.cleaned_data.get('estoque')
        if estoque is not None and estoque < 0:
            raise forms.ValidationError('Estoque não pode ser negativo.')
        return estoque

    def clean_codigo_catalogo(self):
        codigo_catalogo = self.cleaned_data.get('codigo_catalogo')
        if codigo_catalogo:
            return codigo_catalogo.strip().upper()
        return codigo_catalogo

    def clean_validade(self):
        validade = self.cleaned_data.get('validade')
        if validade and validade < timezone.now().date():
            raise forms.ValidationError('Validade não pode ser no passado.')
        return validade

class KitForm(forms.ModelForm):
    especialidade = forms.ChoiceField(
        choices=ESPECIALIDADE_CHOICES,
        required=False,
        label='Especialidade',
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_especialidade'}),
    )
    procedimento_cirurgico = forms.ChoiceField(
        choices=PROCEDIMENTO_CHOICES,
        required=False,
        label='Procedimento cirúrgico',
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_procedimento_cirurgico'}),
    )
    materiais = forms.ModelMultipleChoiceField(
        queryset=Material.objects.none(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'kit-material-checkbox'}),
        required=False,
        label='Materiais'
    )

    class Meta:
        model = Kit
        fields = ['nome', 'especialidade', 'procedimento_cirurgico', 'materiais', 'lacre']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do kit'}),
            'lacre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Gerado automaticamente',
                'id': 'id_lacre',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['lacre'].required = False
        self.fields['materiais'].queryset = Material.objects.all().order_by('categoria', 'nome', 'tipo')
        self.fields['materiais'].label_from_instance = lambda obj: (
            f"{obj.categoria} | {obj.nome}" + (f" - {obj.tipo}" if obj.tipo else "")
        )

class ChecklistForm(forms.ModelForm):
    class Meta:
        model = Checklist
        fields = ['kit_paciente', 'fase', 'observacoes']
        widgets = {
            'kit_paciente': forms.Select(attrs={'class': 'form-select'}),
            'fase': forms.Select(attrs={'class': 'form-select'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['kit_paciente'].queryset = KitPaciente.objects.all().order_by('-data_cirurgia')
        self.fields['kit_paciente'].label = 'Kit do Paciente'