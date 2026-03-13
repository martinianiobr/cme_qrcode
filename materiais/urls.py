from django.urls import path
from . import views
from .views import (
    MaterialListView, MaterialCreateView,
    KitListView, KitCreateView,
    ChecklistListView, ChecklistCreateView,
)
from .views_kitpaciente import (
    dashboard_kit_paciente, criar_kit_paciente, detalhes_kit_paciente,
    auditoria_fluxos,
    checklist_etapa, scan_qr_code, processar_qr_code,
    marcar_item_manual, relatorio_final, concluir_etapa, imprimir_etiquetas_materiais,
    excluir_kit_paciente,
    criar_paciente_aghu, buscar_pacientes_aghu
)

urlpatterns = [
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Novo Sistema de Processos
    path('processos/', dashboard_kit_paciente, name='dashboard_kit_paciente'),
    path('auditoria/fluxos/', auditoria_fluxos, name='auditoria_fluxos'),
    path('processos/novo/', criar_kit_paciente, name='criar_kit_paciente'),
    path('processos/<int:kit_paciente_id>/', detalhes_kit_paciente, name='detalhes_kit_paciente'),
    path('processos/<int:kit_paciente_id>/etiquetas/', imprimir_etiquetas_materiais, name='imprimir_etiquetas_materiais'),
    path('processos/<int:kit_paciente_id>/excluir/', excluir_kit_paciente, name='excluir_kit_paciente'),
    path('processos/<int:kit_paciente_id>/<str:fase>/', checklist_etapa, name='checklist_etapa'),
    path('processos/concluir-etapa/<int:checklist_id>/', concluir_etapa, name='concluir_etapa'),
    path('processos/relatorio/<int:kit_paciente_id>/', relatorio_final, name='relatorio_final'),
    
    # QR Code Scanner
    path('scan/', scan_qr_code, name='scan_qr_code'),
    path('processar-qr/', processar_qr_code, name='processar_qr_code'),
    path('marcar-item/<int:checklist_id>/<int:material_id>/', marcar_item_manual, name='marcar_item_manual'),

    # Materiais
    path('cadastrar/', MaterialCreateView.as_view(), name='cadastrar_material'),
    path('materiais/', MaterialListView.as_view(), name='lista_materiais'),

    # Kits
    path('cadastrar-kit/', KitCreateView.as_view(), name='cadastrar_kit'),
    path('kits/', KitListView.as_view(), name='lista_kits'),

    # Checklists (antigo - manter por compatibilidade)
    path('cadastrar-checklist/', ChecklistCreateView.as_view(), name='cadastrar_checklist'),
    path('checklists/', ChecklistListView.as_view(), name='lista_checklists'),
    path('checklists/<int:pk>/', views.detalhe_checklist, name='detalhe_checklist'),
    path('checklists/<int:checklist_id>/imprimir-qrcodes/', views.gerar_qr_codes_para_impressao, name='imprimir_qrcodes'),
    
    # APIs
    # AJAX patient search uses the newer implementation in views_kitpaciente
    path('api/buscar-pacientes/', buscar_pacientes_aghu, name='buscar_pacientes_aghu'),
    path('api/criar-paciente/', criar_paciente_aghu, name='criar_paciente_aghu'),
]
