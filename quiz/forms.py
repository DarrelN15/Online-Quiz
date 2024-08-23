from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm, UserCreationForm

# Custom user creation form with additional fields
class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, help_text='Required.')  # First name field
    last_name = forms.CharField(max_length=30, required=True, help_text='Required.')  # Last name field
    email = forms.EmailField(max_length=254, required=True, help_text='Required. Enter a valid email address.')  # Email field

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')  # Fields included in the form

    # Custom save method to handle additional fields
    def save(self, commit=True):
        user = super().save(commit=False)  # Get the user instance without saving
        user.email = self.cleaned_data['email']  # Set the email field from cleaned data
        if commit:
            user.save()  # Save the user if commit is True
        return user

# Form for editing user profiles
class EditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']  # Fields included in the form

# Custom password change form with metadata for field inclusion
class CustomPasswordChangeForm(PasswordChangeForm):
    class Meta:
        model = User
        fields = ['old_password', 'new_password1', 'new_password2']  # Fields included in the form