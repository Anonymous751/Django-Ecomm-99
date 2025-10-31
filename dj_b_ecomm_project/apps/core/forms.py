from django import forms
from .models import Contact

from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Contact


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'email', 'message']
        labels = {
            'name': _("Name"),
            'email': _("Email"),
            'message': _("Message"),
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5
            }),
        }

