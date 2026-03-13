from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('materiais', '0012_kit_procedimento_fields'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='kit',
            name='criado_em',
            field=models.DateTimeField(auto_now_add=True, null=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='kit',
            name='criado_por',
            field=models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, related_name='kits_criados', to=settings.AUTH_USER_MODEL),
        ),
    ]