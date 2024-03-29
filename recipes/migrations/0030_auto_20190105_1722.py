# Generated by Django 2.1.2 on 2019-01-05 17:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0029_auto_20190105_1502'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredient',
            name='count',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='recipe',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='recipes.Recipe'),
        ),
    ]
