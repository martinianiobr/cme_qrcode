from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('materiais', '0010_material_origem_cadastro'),
    ]

    operations = [
        migrations.AddField(
            model_name='material',
            name='classificacao_processamento',
            field=models.CharField(
                choices=[
                    ('reutilizavel_esteril', 'Reutilizável estéril'),
                    ('reprocessamento', 'Reutilizável para reprocessamento'),
                    ('descartavel_esteril', 'Descartável estéril'),
                    ('descartavel_nao_esteril', 'Descartável não estéril'),
                ],
                default='reutilizavel_esteril',
                max_length=30,
            ),
        ),
        migrations.AddField(
            model_name='material',
            name='codigo_catalogo',
            field=models.CharField(blank=True, max_length=20, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='material',
            name='material_composicao',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='material',
            name='tamanho',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='material',
            name='tipo',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='material',
            name='uso_observacao',
            field=models.TextField(blank=True),
        ),
    ]