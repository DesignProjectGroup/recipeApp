# Generated by Django 2.1.2 on 2018-11-23 05:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0006_auto_20181113_1532'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recipe',
            name='ingredient_title',
        ),
        migrations.AddField(
            model_name='ingredient',
            name='ingredient_subtitle',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='ingredient',
            name='name',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='comment',
            name='recipe',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='recipes.Recipe'),
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='recipe',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='recipes.Recipe'),
        ),
    ]