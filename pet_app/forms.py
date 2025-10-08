from django import forms
from .models import Pet

class PetForm(forms.ModelForm):
    class Meta:
        model = Pet
        fields = ['name', 'category', 'age', 'breed', 'description', 'image','contact_email' ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Pet Name'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'age': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Age in years'}),
            'breed': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Breed'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Describe the pet'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
