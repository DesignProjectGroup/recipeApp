# Generated by Django 2.1.2 on 2018-11-25 18:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0011_merge_20181125_1859'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='food',
            name='measurement_unit',
        ),
        migrations.AddField(
            model_name='food',
            name='amountsOfGram',
            field=models.IntegerField(default=0, null=True),
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
