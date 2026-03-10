from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('materiais', '0002_empty'),
    ]

    operations = [
        migrations.AddField(
            model_name='material',
            name='status_esterilizacao',
            field=models.CharField(
                max_length=20,
                choices=[('OK', 'OK'), ('pendente', 'Pendente'), ('reprocessar', 'Reprocessar')],
                default='OK',
            ),
        ),
        migrations.AddField(
            model_name='material',
            name='estoque',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='material',
            name='fornecedor',
            field=models.CharField(max_length=100, blank=True, default=''),
        ),
        migrations.AddField(
            model_name='material',
            name='localizacao',
            field=models.CharField(max_length=100, blank=True, default=''),
        ),
        # also add qr_image now already exists and codigo_qr exists earlier
    ]
