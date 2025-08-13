from django import forms
from .models import DataEntry, MatchedPair, Classification, EvaluationSession
import json

class JSONFileUploadForm(forms.Form):
    """Form for uploading JSON files"""
    ground_truth_file = forms.FileField(
        label='Ground Truth JSON File',
        help_text='Upload the ground truth data file (JSON format)',
        required=True
    )
    predicted_file = forms.FileField(
        label='Predicted JSON File',
        help_text='Upload the predicted data file (JSON format)',
        required=True
    )
    replace_existing = forms.BooleanField(
        label='Replace all existing data',
        help_text='If checked, will delete all existing data, pairs, and classifications. If unchecked, will update existing entries.',
        required=False,
        initial=False
    )
    
    def clean_ground_truth_file(self):
        file = self.cleaned_data['ground_truth_file']
        if not file.name.endswith('.json'):
            raise forms.ValidationError('File must be a JSON file')
        
        try:
            content = file.read().decode('utf-8')
            data = json.loads(content)
            if not isinstance(data, list):
                raise forms.ValidationError('JSON must contain a list of objects')
            
            # Validate structure
            for item in data:
                if not isinstance(item, dict):
                    raise forms.ValidationError('Each item must be an object')
                if 'polymer_system' not in item or 'force_field' not in item:
                    raise forms.ValidationError('Each item must have polymer_system and force_field')
            
            return data
        except json.JSONDecodeError:
            raise forms.ValidationError('Invalid JSON format')
        except UnicodeDecodeError:
            raise forms.ValidationError('File must be UTF-8 encoded')
    
    def clean_predicted_file(self):
        file = self.cleaned_data['predicted_file']
        if not file.name.endswith('.json'):
            raise forms.ValidationError('File must be a JSON file')
        
        try:
            content = file.read().decode('utf-8')
            data = json.loads(content)
            if not isinstance(data, list):
                raise forms.ValidationError('JSON must contain a list of objects')
            
            # Validate structure
            for item in data:
                if not isinstance(item, dict):
                    raise forms.ValidationError('Each item must be an object')
                if 'polymer_system' not in item or 'force_field' not in item:
                    raise forms.ValidationError('Each item must have polymer_system and force_field')
            
            return data
        except json.JSONDecodeError:
            raise forms.ValidationError('Invalid JSON format')
        except UnicodeDecodeError:
            raise forms.ValidationError('File must be UTF-8 encoded')

class EvaluationSessionForm(forms.ModelForm):
    """Form for creating evaluation sessions"""
    class Meta:
        model = EvaluationSession
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter session name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Optional description'}),
        }

class ClassificationForm(forms.ModelForm):
    """Form for individual property classifications"""
    class Meta:
        model = Classification
        fields = ['classification']
        widgets = {
            'classification': forms.Select(attrs={'class': 'form-control'})
        } 