from django.db import models
from recipes.models import Recipe


class Comment(models.Model):
    owner = models.CharField(max_length=200, null=True)
    isPositive = models.CharField(max_length=3, null=True)
    date = models.DateField(null=True)
    text = models.TextField(null=True)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, null=True)


class ProbabilityOfWords(models.Model):
    word = models.CharField(max_length=200, null=True)
    probabilityOfPositive = models.FloatField(default=0)
    probabilityOfNegative = models.FloatField(default=0)
