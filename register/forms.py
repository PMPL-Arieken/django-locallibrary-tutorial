from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import datetime  # for checking renewal date range.

from django import forms


class RegisterForm(forms.Form):
    email = forms.EmailField(help_text="Enter a valid email",label="Email")
    password = forms.CharField(widget=forms.PasswordInput,label="Password")
    password2 = forms.CharField(widget=forms.PasswordInput,label="Confirm Password")

    def clean_email(self):
        email = self.data.get("email")
        count = User.objects.filter(email=email).count()
        if count > 0:
            raise forms.ValidationError("User already exists")
        return email

    def clean_password(self):
        password = self.data.get("password")
        password2 = self.data.get("password2")
        if password != password2:
            raise forms.ValidationError("Passwords must be equal")
        return password
