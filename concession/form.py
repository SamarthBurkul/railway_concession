# forms.py
from django import forms
from .models import UserProfile

class PreferencesForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['theme', 'font_size', 'contrast_mode']