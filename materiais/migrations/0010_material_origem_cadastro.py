from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('materiais', '0009_alter_paciente_options_remove_paciente_criado_em_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='material',
            name='origem_cadastro',
            field=models.CharField(
                choices=[('sistema', 'Catálogo do sistema'), ('contingencia', 'Cadastro de contingência')],
                default='contingencia',
                max_length=20,
            ),
        ),
    ]