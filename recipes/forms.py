from django import forms
from recipes.models import MeasureTable


class UserProduct(forms.Form):
    OPTIONS = ()
    products = MeasureTable.objects.values_list('name').distinct()
    for i in products:
        x = i+i
        OPTIONS = (x,)+OPTIONS
    userProducts = forms.MultipleChoiceField(widget=forms.SelectMultiple(attrs={'class':'recipes-user-products'}), choices=OPTIONS, label='')
