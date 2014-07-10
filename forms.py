from django import forms
from django.forms import ModelForm

class DemoImageForm(forms.Form):
    imagefile=forms.FileField()
    description=forms.CharField(required=False, max_length=2048)

class DemoDemoForm(forms.Form):
    file=forms.FileField()

class GameIconForm(forms.Form):
    file=forms.FileField()
