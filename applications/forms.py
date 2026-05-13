from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from .models import Application


class ApplicationForm(forms.ModelForm):
    class Meta:
        model  = Application
        fields = ['cover_letter', 'resume']
        widgets = {
            'cover_letter': forms.Textarea(attrs={
                'rows': 6,
                'placeholder': 'Tell the employer why you are the best fit for this role…'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['resume'].widget.attrs.update({'accept': '.pdf'})
        self.helper = FormHelper()
        self.helper.form_tag = False   # template owns the <form> tag

    def clean_resume(self):
        resume = self.cleaned_data.get('resume')
        if resume:
            if not resume.name.endswith('.pdf'):
                raise forms.ValidationError('Only PDF files are accepted.')
            if resume.size > 5 * 1024 * 1024:
                raise forms.ValidationError('File size must not exceed 5 MB.')
        return resume


class StatusUpdateForm(forms.ModelForm):
    class Meta:
        model  = Application
        fields = ['status']