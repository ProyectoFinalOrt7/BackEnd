# Generated by Django 3.2.7 on 2021-10-29 01:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('democracia', '0007_voto'),
    ]

    operations = [
        migrations.AddField(
            model_name='voto',
            name='comentario',
            field=models.CharField(default='', max_length=1024),
        ),
        migrations.AlterField(
            model_name='voto',
            name='voto',
            field=models.CharField(choices=[('A', 'Afirmativo'), ('N', 'Negativo')], max_length=1),
        ),
    ]