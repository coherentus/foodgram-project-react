# Generated by Django 3.2.8 on 2021-12-20 08:56

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_alter_component_recipe'),
    ]

    operations = [
        migrations.AlterField(
            model_name='component',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipe_components', to='recipes.recipe', verbose_name='Рецепт'),
        ),
    ]
