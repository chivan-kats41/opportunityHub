from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from honeypot.decorators import check_honeypot
from .forms import JobseekerRegisterForm, EmployerRegisterForm, ProfileForm
from .models import CustomUser


@check_honeypot
def register_view(request):
    role = request.GET.get('role', 'jobseeker')
    if request.method == 'POST':
        role = request.POST.get('role', 'jobseeker')
        FormClass = EmployerRegisterForm if role == 'employer' else JobseekerRegisterForm
        form = FormClass(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome to JobHub, {user.first_name}!')
            return redirect('dashboard:index')
    else:
        FormClass = EmployerRegisterForm if role == 'employer' else JobseekerRegisterForm
        form = FormClass()

    return render(request, 'accounts/register.html', {'form': form, 'role': role})


@check_honeypot
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            next_url = request.GET.get('next', '/dashboard/')
            return redirect(next_url)
        messages.error(request, 'Invalid username or password.')
    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('jobs:index')


@login_required
@check_honeypot
def profile_view(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('accounts:profile')
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'accounts/profile.html', {'form': form})


@login_required
def dashboard_redirect(request):
    if request.user.is_employer():
        return redirect('dashboard:employer')
    return redirect('dashboard:jobseeker')


@login_required
def employer_dashboard(request):
    from jobs.models import Job
    from applications.models import Application

    jobs = Job.objects.filter(employer=request.user)
    recent_apps = Application.objects.filter(
        job__employer=request.user
    ).select_related('job', 'applicant').order_by('-applied_at')[:10]

    context = {
        'total_jobs': jobs.count(),
        'active_jobs': jobs.filter(is_active=True).count(),
        'total_applications': Application.objects.filter(job__employer=request.user).count(),
        'recent_applications': recent_apps,
        'jobs': jobs.order_by('-created_at')[:5],
    }
    return render(request, 'dashboard/employer.html', context)


@login_required
def jobseeker_dashboard(request):
    from applications.models import Application

    apps = Application.objects.filter(applicant=request.user).select_related('job').order_by('-applied_at')

    context = {
        'total_applications': apps.count(),
        'pending_count':  apps.filter(status='pending').count(),
        'accepted_count': apps.filter(status='accepted').count(),
        'rejected_count': apps.filter(status='rejected').count(),
        'reviewed_count': apps.filter(status='reviewed').count(),
        'recent_applications': apps[:10],
    }
    return render(request, 'dashboard/jobseeker.html', context)
