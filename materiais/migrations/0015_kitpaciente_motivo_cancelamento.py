from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('materiais', '0014_kitpaciente_cancelamento_rastreabilidade'),
    ]

    operations = [
        migrations.AddField(
            model_name='kitpaciente',
            name='motivo_cancelamento',
            field=models.TextField(blank=True),
        ),
    ]
