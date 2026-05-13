from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    path('',                    views.index,      name='index'),
    path('jobs/',               views.job_list,   name='list'),
    path('jobs/create/',        views.job_create, name='create'),
    path('jobs/my-jobs/',       views.my_jobs,    name='my_jobs'),
    path('jobs/<int:pk>/',      views.job_detail, name='detail'),
    path('jobs/<int:pk>/edit/', views.job_edit,   name='edit'),
    path('jobs/<int:pk>/delete/', views.job_delete, name='delete'),
    path('companies/',             views.companies_list, name='companies'),
]


