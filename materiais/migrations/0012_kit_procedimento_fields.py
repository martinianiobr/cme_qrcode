from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('materiais', '0011_material_catalogo_padrao_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='kit',
            name='especialidade',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='kit',
            name='origem_cadastro',
            field=models.CharField(
                choices=[('sistema', 'Catálogo do sistema'), ('manual', 'Cadastro manual')],
                default='manual',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='kit',
            name='procedimento_cirurgico',
            field=models.CharField(blank=True, max_length=150),
        ),
    ]