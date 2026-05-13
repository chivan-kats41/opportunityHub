from django.urls import path
from . import views

app_name = 'applications'

urlpatterns = [
    path('apply/<int:job_id>/',        views.apply_view,      name='apply'),
    path('my/',                         views.my_applications, name='my_applications'),
    path('job/<int:job_id>/applicants/', views.job_applicants, name='job_applicants'),
    path('<int:app_id>/status/',        views.update_status,   name='update_status'),
]