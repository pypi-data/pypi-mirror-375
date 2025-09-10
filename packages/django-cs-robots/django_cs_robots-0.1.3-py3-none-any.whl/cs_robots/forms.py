# core/forms.py
from django import forms

class RobotsTxtForm(forms.Form):
    content = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 20, 'cols': 80}),
        label="Contenido del fichero robots.txt",
        help_text="Guarda los cambios para sobreescribir el fichero físico."
    )