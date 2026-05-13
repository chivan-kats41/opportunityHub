from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, Field
from .models import Job, Category


class JobForm(forms.ModelForm):
    class Meta:
        model  = Job
        fields = ['title', 'description', 'company_name', 'location', 'job_type',
                  'salary_range', 'category', 'deadline', 'is_active', 'is_featured']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 8}),
            'deadline':    forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.all()
        self.helper = FormHelper()
        self.helper.form_tag = False   # template provides the <form> tag
        self.helper.layout = Layout(
            'title',
            Row(Column('company_name'), Column('location')),
            Row(Column('job_type'), Column('category')),
            Row(Column('salary_range'), Column('deadline')),
            'description',
            Row(Column('is_active'), Column('is_featured')),
        )


class JobSearchForm(forms.Form):
    q        = forms.CharField(required=False, label='Keyword',
                               widget=forms.TextInput(attrs={'placeholder': 'Job title, company…'}))
    location = forms.CharField(required=False, label='Location',
                               widget=forms.TextInput(attrs={'placeholder': 'City or region'}))
    job_type = forms.ChoiceField(required=False, choices=[('', 'All Types')] + Job.JOB_TYPE_CHOICES)
    category = forms.ModelChoiceField(required=False, queryset=Category.objects.all(),
                                      empty_label='All Categories')