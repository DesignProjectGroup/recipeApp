# Generated by Django 2.1.2 on 2018-12-30 19:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('comments', '0011_auto_20181230_1940'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='commentdataset',
            name='isTrain',
        ),
        migrations.AlterField(
            model_name='comment',
            name='recipe',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='recipes.Recipe'),
        ),
    ]
