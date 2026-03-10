from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils import timezone
from .models import Material, Kit, Paciente, KitPaciente, Checklist


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
        self.fields['kit'].queryset = Kit.objects.all().order_by('nome')
        
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
            'nome', 'categoria', 'lote', 'data_esterilizacao', 'status_esterilizacao',
            'validade', 'responsavel', 'estoque', 'fornecedor', 'localizacao'
        ]
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Nome'}),
            'categoria': forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Categoria'}),
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

    def clean_validade(self):
        validade = self.cleaned_data.get('validade')
        if validade and validade < timezone.now().date():
            raise forms.ValidationError('Validade não pode ser no passado.')
        return validade

class KitForm(forms.ModelForm):
    class Meta:
        model = Kit
        fields = ['nome','materiais','lacre']
        widgets = {
            'nome': forms.TextInput(attrs={'class':'form-control','placeholder':'Nome do kit'}),
            'lacre': forms.TextInput(attrs={'class':'form-control','placeholder':'Lacre'}),
            'materiais': forms.CheckboxSelectMultiple(attrs={'class':'form-check'})
        }

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