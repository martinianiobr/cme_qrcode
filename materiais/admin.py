from django.contrib import admin
from .models import Material, Kit, Checklist, ChecklistItem, LeituraQR, Paciente, KitPaciente


@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ('nome','prontuario','data_nascimento','telefone')
    search_fields = ('nome','prontuario')
    list_filter = ('data_nascimento',)


@admin.register(KitPaciente)
class KitPacienteAdmin(admin.ModelAdmin):
    list_display = ('paciente','kit','data_cirurgia','status','criado_em')
    search_fields = ('paciente__nome','kit__nome')
    list_filter = ('status','data_cirurgia')


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('nome','categoria','lote','validade','estoque','status_esterilizacao')
    search_fields = ('nome','categoria','lote','codigo_qr')
    list_filter = ('status_esterilizacao','validade')


@admin.register(Kit)
class KitAdmin(admin.ModelAdmin):
    list_display = ('nome','lacre')
    search_fields = ('nome','lacre')
    filter_horizontal = ('materiais',)


@admin.register(Checklist)
class ChecklistAdmin(admin.ModelAdmin):
    list_display = ('kit_paciente','fase','usuario_responsavel','data_inicio','data_conclusao','concluido')
    search_fields = ('kit_paciente__paciente__nome','kit_paciente__kit__nome')
    list_filter = ('fase','concluido','data_inicio')


@admin.register(ChecklistItem)
class ChecklistItemAdmin(admin.ModelAdmin):
    list_display = ('checklist','material','conferido','data_conferencia')


@admin.register(LeituraQR)
class LeituraQRAdmin(admin.ModelAdmin):
    list_display = ('acao','material','kit','usuario','timestamp')
