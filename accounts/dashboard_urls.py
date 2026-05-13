from django.urls import path
from accounts import views

app_name = 'dashboard'

urlpatterns = [
    path('',          views.dashboard_redirect,  name='index'),
    path('employer/', views.employer_dashboard,  name='employer'),
    path('jobseeker/', views.jobseeker_dashboard, name='jobseeker'),
]