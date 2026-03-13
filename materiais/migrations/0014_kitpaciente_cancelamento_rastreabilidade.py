from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('materiais', '0013_kit_rastreabilidade'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='kitpaciente',
            name='cancelado_em',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='kitpaciente',
            name='cancelado_por',
            field=models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, related_name='processos_cancelados', to=settings.AUTH_USER_MODEL),
        ),
    ]
