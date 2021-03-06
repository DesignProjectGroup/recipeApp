# Generated by Django 2.1.2 on 2018-12-11 19:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('comments', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='recipe',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='recipes.Recipe'),
        ),
        migrations.AlterField(
            model_name='probabilityofwords',
            name='probabilityOfNegative',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='probabilityofwords',
            name='probabilityOfPositive',
            field=models.FloatField(default=0),
        ),
    ]
