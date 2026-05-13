from django import forms
from django.contrib.auth.forms import UserCreationForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, Field
from .models import CustomUser


class JobseekerRegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=100, required=True)
    last_name  = forms.CharField(max_length=100, required=True)
    email      = forms.EmailField(required=True)
    phone      = forms.CharField(max_length=20, required=False)

    class Meta:
        model  = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'phone', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = CustomUser.JOBSEEKER
        if commit:
            user.save()
        return user

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False   # template owns the <form> tag
        self.helper.layout = Layout(
            Row(Column('first_name'), Column('last_name')),
            'username', 'email', 'phone',
            'password1', 'password2',
        )


class EmployerRegisterForm(UserCreationForm):
    first_name   = forms.CharField(max_length=100, required=True)
    last_name    = forms.CharField(max_length=100, required=True)
    email        = forms.EmailField(required=True)
    company_name = forms.CharField(max_length=200, required=True)
    phone        = forms.CharField(max_length=20, required=False)
    website      = forms.URLField(required=False)

    class Meta:
        model  = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email',
                  'company_name', 'phone', 'website', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = CustomUser.EMPLOYER
        if commit:
            user.save()
        return user

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False   # template owns the <form> tag
        self.helper.layout = Layout(
            Row(Column('first_name'), Column('last_name')),
            'username', 'email', 'company_name',
            Row(Column('phone'), Column('website')),
            'password1', 'password2',
        )


class ProfileForm(forms.ModelForm):
    class Meta:
        model  = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone', 'bio',
                  'profile_photo', 'company_name', 'website']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False   # template owns the <form> tag
        self.helper.layout = Layout(
            Row(Column('first_name'), Column('last_name')),
            'email', 'phone', 'bio', 'profile_photo',
            Row(Column('company_name'), Column('website')),
        )