# Generated by Django 2.1.2 on 2018-12-20 20:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('comments', '0008_auto_20181220_2038'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='isTrain',
            field=models.CharField(max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='comment',
            name='recipe',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='recipes.Recipe'),
        ),
    ]