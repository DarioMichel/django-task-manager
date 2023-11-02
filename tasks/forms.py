from django import forms
from .models import Task

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['titulo','descripcion','es_importante']
        
        Widget = {
            'titulo': forms.TextInput(attrs={'class':'form-control', 'placeholder':'Escribe un titulo para la Tarea'}),
            'descripcion': forms.Textarea(attrs={'class':'form-controla', 'placeholder':'Escribe una descripcion para la Tarea'}),
            'es_importante': forms.CheckboxInput(attrs={'class':'form-check-input m-auto'})
        }