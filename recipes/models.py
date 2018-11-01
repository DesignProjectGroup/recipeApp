from django.db import models


class Recipe(models.Model):
    title = models.CharField(max_length=200, null=True)
    ingredient_title = models.CharField(max_length=200, null=True)
    calorie = models.IntegerField(default=0, null=True)
    text = models.TextField(null=True)
    score = models.IntegerField(default=0, null=True)
    isHard = models.CharField(max_length=3, null=True)
    isVegetarian = models.CharField(max_length=3, null=True)
    isGood = models.CharField(max_length=3, null=True)
    image = models.ImageField(null=True)


class Ingredient(models.Model):
    calorie = models.IntegerField(default=0, null=True)
    count = models.IntegerField(default=0, null=True)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, null=True)


class Comment(models.Model):
    owner = models.CharField(max_length=200, null=True)
    isPositive = models.CharField(max_length=3, null=True)
    date = models.DateField(null=True)
    text = models.TextField(null=True)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, null=True)


class Food(models.Model):
    name = models.CharField(max_length=200, null=True)
    calorie = models.IntegerField(null=True)
    unit_amount = models.IntegerField(null=True)
    isVegetarian = models.CharField(max_length=3, null=True)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, null=True)


class VegetarianFood(models.Model):
    name = models.CharField(max_length=200, null=True)