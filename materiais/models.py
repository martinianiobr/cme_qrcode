from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Paciente(models.Model):
    # Dados principais do paciente (vindo do AGHU)
    prontuario = models.CharField(max_length=20, unique=True, help_text="Prontuário AGHU")
    nome = models.CharField(max_length=200, help_text="Nome completo do paciente")
    nome_mae = models.CharField(max_length=200, help_text="Nome completo da mãe")
    data_nascimento = models.DateField(help_text="Data de nascimento")
    cpf = models.CharField(max_length=14, unique=True, help_text="CPF do paciente")
    telefone = models.CharField(max_length=20, blank=True, null=True, help_text="Telefone para contato")
    
    # Controle de sincronização
    data_importacao = models.DateTimeField(auto_now_add=True, help_text="Data de importação do AGHU")
    fonte = models.CharField(max_length=10, default='LOCAL', help_text="Fonte dos dados (AGHU/LOCAL)")
    
    class Meta:
        verbose_name = 'Paciente'
        verbose_name_plural = 'Pacientes'
        ordering = ['nome']
    
    def __str__(self):
        return f"{self.nome} ({self.prontuario})"
    
    @property
    def idade(self):
        """Calcular idade atual do paciente"""
        from datetime import date
        hoje = date.today()
        idade = hoje.year - self.data_nascimento.year - ((hoje.month, hoje.day) < (self.data_nascimento.month, self.data_nascimento.day))
        return idade


class KitPaciente(models.Model):
    STATUS_CHOICES = [
        ('agendado', 'Agendado'),
        ('pre_operatorio', 'Pré-operatório'),
        ('intra_operatorio', 'Intra-operatório'),
        ('pos_operatorio', 'Pós-operatório'),
        ('concluido', 'Concluído'),
        ('cancelado', 'Cancelado'),
    ]
    
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    kit = models.ForeignKey('Kit', on_delete=models.CASCADE)
    data_cirurgia = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='agendado')
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-data_cirurgia']
    
    def __str__(self):
        return f"{self.paciente.nome} - {self.kit.nome}"
    
    def pode_iniciar_pre(self):
        """Sempre pode iniciar pré-operatório se estiver agendado"""
        return self.status == 'agendado'
    
    def pode_iniciar_intra(self):
        """Só pode iniciar intra se pré-operatório estiver concluído"""
        return self.checklists.filter(
            fase='pre',
            concluido=True
        ).exists()
    
    def pode_iniciar_pos(self):
        """Só pode iniciar pós se intra-operatório estiver concluído"""
        return self.checklists.filter(
            fase__in=['pre', 'intra'],
            concluido=True
        ).count() == 2
    
    def processo_concluido(self):
        """Verifica se todas as etapas foram concluídas"""
        return self.checklists.filter(concluido=True).count() == 3
    
    def proxima_etapa(self):
        """Retorna a próxima etapa a ser executada"""
        if not self.checklists.filter(fase='pre', concluido=True).exists():
            return 'pre'
        elif not self.checklists.filter(fase='intra', concluido=True).exists():
            return 'intra'
        elif not self.checklists.filter(fase='pos', concluido=True).exists():
            return 'pos'
        return None
    
    def atualizar_status(self):
        """Atualiza o status baseado nas etapas concluídas"""
        if self.processo_concluido():
            self.status = 'concluido'
        elif self.pode_iniciar_pos():
            self.status = 'intra_operatorio'
        elif self.pode_iniciar_intra():
            self.status = 'pre_operatorio'
        else:
            self.status = 'agendado'
        self.save()


class Material(models.Model):
    nome = models.CharField(max_length=100)
    categoria = models.CharField(max_length=50)
    lote = models.CharField(max_length=50)
    data_esterilizacao = models.DateField()
    status_esterilizacao = models.CharField(
        max_length=20,
        choices=[('OK', 'OK'), ('pendente', 'Pendente'), ('reprocessar', 'Reprocessar')],
        default='OK'
    )
    validade = models.DateField()
    responsavel = models.CharField(max_length=100)
    estoque = models.PositiveIntegerField(default=0)
    fornecedor = models.CharField(max_length=100, blank=True)
    localizacao = models.CharField(max_length=100, blank=True)
    codigo_qr = models.CharField(max_length=200, unique=True, blank=True)
    qr_image = models.ImageField(upload_to='qrcodes/', blank=True, null=True)  # imagem do QR

    def __str__(self):
        return self.nome

    class Meta:
        ordering = ['nome']

    def save(self, *args, **kwargs):
        # generate QR code string if missing
        if not self.codigo_qr:
            self.codigo_qr = f"MAT-{self.lote}-{self.nome}"
        # generate image if missing or code changed
        try:
            prev = Material.objects.get(pk=self.pk)
        except Material.DoesNotExist:
            prev = None
        if not self.qr_image or (prev and prev.codigo_qr != self.codigo_qr):
            import qrcode
            from io import BytesIO
            from django.core.files.base import ContentFile
            qr = qrcode.make(self.codigo_qr)
            buffer = BytesIO()
            qr.save(buffer, format="PNG")
            self.qr_image.save(f"{self.nome}_qr.png", ContentFile(buffer.getvalue()), save=False)
        super().save(*args, **kwargs)


class Kit(models.Model):
    nome = models.CharField(max_length=100)
    materiais = models.ManyToManyField(Material)
    lacre = models.CharField(max_length=50)
    codigo_qr = models.CharField(max_length=200, unique=True, blank=True)
    qr_image = models.ImageField(upload_to='qrcodes/', blank=True, null=True)  # imagem do QR

    def __str__(self):
        return self.nome

    class Meta:
        ordering = ['nome']

    def save(self, *args, **kwargs):
        if not self.codigo_qr:
            self.codigo_qr = f"KIT-{self.nome}-{self.lacre}"
        try:
            prev = Kit.objects.get(pk=self.pk)
        except Kit.DoesNotExist:
            prev = None
        if not self.qr_image or (prev and prev.codigo_qr != self.codigo_qr):
            import qrcode
            from io import BytesIO
            from django.core.files.base import ContentFile
            qr = qrcode.make(self.codigo_qr)
            buffer = BytesIO()
            qr.save(buffer, format="PNG")
            self.qr_image.save(f"{self.nome}_qr.png", ContentFile(buffer.getvalue()), save=False)
        super().save(*args, **kwargs)


class Checklist(models.Model):
    FASE_CHOICES = [
        ('pre', 'Pré-cirurgia'),
        ('intra', 'Intraoperatório'),
        ('pos', 'Pós-cirurgia'),
    ]
    
    METODO_CHECK_CHOICES = [
        ('manual', 'Manual'),
        ('qr_code', 'QR Code'),
        ('leitor', 'Leitor Externo'),
    ]

    # ESSENCIAL: Vínculo com KitPaciente em vez de Kit
    kit_paciente = models.ForeignKey(KitPaciente, on_delete=models.CASCADE, related_name='checklists')
    fase = models.CharField(max_length=10, choices=FASE_CHOICES)
    itens = models.JSONField(default=dict)  # Estrutura: {material_id: {checado: bool, data: datetime, usuario: id, metodo: str}}
    concluido = models.BooleanField(default=False)
    usuario_responsavel = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    data_inicio = models.DateTimeField(auto_now_add=True)
    data_conclusao = models.DateTimeField(null=True, blank=True)
    observacoes = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['kit_paciente', 'fase']
        ordering = ['fase']
    
    def __str__(self):
        return f"{self.kit_paciente.paciente.nome} - {self.get_fase_display()} - {self.kit_paciente.kit.nome}"
    
    def progresso(self):
        """Calcula o progresso do checklist"""
        if not self.itens:
            return 0
        total = len(self.itens)
        concluidos = sum(1 for item in self.itens.values() if item.get('checado', False))
        return int((concluidos / total) * 100) if total > 0 else 0
    
    def itens_checados(self):
        """Retorna número de itens checados"""
        if not self.itens:
            return 0
        return sum(1 for item in self.itens.values() if item.get('checado', False))
    
    def total_itens(self):
        """Retorna total de itens"""
        return len(self.itens) if self.itens else 0
    
    def pode_acessar(self):
        """Verifica se esta etapa pode ser acessada"""
        if self.fase == 'pre':
            return True  # Sempre pode acessar pré
        
        if self.fase == 'intra':
            # Só pode acessar intra se pré estiver concluído
            return self.kit_paciente.checklists.filter(
                fase='pre', 
                concluido=True
            ).exists()
        
        if self.fase == 'pos':
            # Só pode acessar pós se intra estiver concluído
            return self.kit_paciente.checklists.filter(
                fase='intra', 
                concluido=True
            ).exists()
        
        return False
    
    def marcar_item(self, material_id, usuario, metodo='manual'):
        """Marca um item como checado"""
        if str(material_id) not in self.itens:
            return False
        
        self.itens[str(material_id)].update({
            'checado': True,
            'data': timezone.now().isoformat(),
            'usuario': usuario.id,
            'metodo': metodo
        })
        self.save()
        
        # Verificar se todos os itens foram checados
        if self.todos_itens_checados():
            self.concluir()
        
        return True
    
    def todos_itens_checados(self):
        """Verifica se todos os itens foram checados"""
        if not self.itens:
            return False
        return all(item.get('checado', False) for item in self.itens.values())
    
    def concluir(self):
        """Marca checklist como concluído"""
        self.concluido = True
        self.data_conclusao = timezone.now()
        self.save()
        # Atualizar status do kit_paciente
        self.kit_paciente.atualizar_status()
    
    def gerar_itens_automaticamente(self):
        """Gera itens automaticamente baseado nos materiais do kit"""
        materiais = self.kit_paciente.kit.materiais.all()
        itens_dict = {}
        
        for material in materiais:
            itens_dict[str(material.id)] = {
                'material_id': material.id,
                'material_nome': material.nome,
                'material_codigo': material.codigo_qr,
                'checado': False,
                'data': None,
                'usuario': None,
                'metodo': None
            }
        
        self.itens = itens_dict
        self.save()


class ChecklistItem(models.Model):
    checklist = models.ForeignKey(Checklist, on_delete=models.CASCADE)
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    conferido = models.BooleanField(default=False)
    data_conferencia = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ('checklist', 'material')

    def __str__(self):
        return f"{self.material.nome} in {self.checklist}"


class LeituraQR(models.Model):
    ACOES = [
        ('conferido', 'Conferido'),
        ('uso', 'Uso'),
        ('descartado', 'Descartado'),
        ('kit', 'Kit lido'),
        ('forasteiro', 'Item não previsto'),
    ]

    checklist = models.ForeignKey(Checklist, on_delete=models.CASCADE, null=True, blank=True)
    material = models.ForeignKey(Material, on_delete=models.SET_NULL, null=True, blank=True)
    kit = models.ForeignKey(Kit, on_delete=models.SET_NULL, null=True, blank=True)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    acao = models.CharField(max_length=20, choices=ACOES)
    timestamp = models.DateTimeField(auto_now_add=True)
    observacao = models.TextField(blank=True)

    def __str__(self):
        who = self.material or self.kit or 'desconhecido'
        return f"{self.get_acao_display()} - {who} ({self.timestamp})"
