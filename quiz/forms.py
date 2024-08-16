from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm

class EditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

class CustomPasswordChangeForm(PasswordChangeForm):
    class Meta:
        model = User
        fields = ['old_password', 'new_password1', 'new_password2']
