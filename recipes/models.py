from django.db import models


class Recipe(models.Model):
    title = models.CharField(max_length=200, null=True)
    calorie = models.IntegerField(default=0, null=True)
    text = models.TextField(null=True)
    score = models.IntegerField(default=0, null=True)
    isHard = models.CharField(max_length=3, null=True)
    isVegetarian = models.CharField(max_length=3, null=True)
    isGood = models.CharField(max_length=3, null=True)
    image = models.ImageField(null=True)


class Ingredient(models.Model):
    name = models.CharField(max_length=200, null=True)
    subtitle = models.CharField(max_length=200, null=True)
    calorie = models.IntegerField(default=0, null=True)
    count = models.CharField(max_length=200, null=True)
    measurementUnit = models.CharField(max_length=200, null=True)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, null=True)


class Food(models.Model):
    name = models.CharField(max_length=200, null=True)
    calorie = models.IntegerField(null=True)
    count = models.IntegerField(default=0, null=True)
    measurementUnit = models.CharField(max_length=200, null=True)
    isVegetarian = models.CharField(max_length=3, null=True)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, null=True)
    amountsOfGram = models.IntegerField(default=0, null=True)


class VegetarianFood(models.Model):
    name = models.CharField(max_length=200, null=True)


class MeasureTable(models.Model):
    name = models.CharField(max_length=200, null=True)
    object_type = models.CharField(max_length=200, null=True)
    technical_measure = models.IntegerField(null=True)
    measurementUnit = models.CharField(max_length=200, null=True)
