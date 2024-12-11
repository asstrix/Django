from django import forms
from .models import Advertisement
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model


class AdvertisementForm(forms.ModelForm):
    photo1 = forms.FileField(required=False)
    photo2 = forms.FileField(required=False)
    photo3 = forms.FileField(required=False)
    photo4 = forms.FileField(required=False)

    class Meta:
        model = Advertisement
        fields = ['title', 'content']


class SignUpForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ('username', 'password1', 'password2',)
