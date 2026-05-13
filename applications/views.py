from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from honeypot.decorators import check_honeypot
from jobs.models import Job
from .models import Application
from .forms import ApplicationForm, StatusUpdateForm
from accounts.decorators import jobseeker_required, employer_required


@jobseeker_required
@check_honeypot
def apply_view(request, job_id):
    job = get_object_or_404(Job, pk=job_id, is_active=True)

    # Prevent duplicate applications
    if Application.objects.filter(job=job, applicant=request.user).exists():
        messages.warning(request, 'You have already applied for this job.')
        return redirect('jobs:detail', pk=job.pk)

    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            app = form.save(commit=False)
            app.job       = job
            app.applicant = request.user
            app.save()
            messages.success(request, f'Application submitted for "{job.title}"!')
            return redirect('applications:my_applications')
    else:
        form = ApplicationForm()

    return render(request, 'applications/apply.html', {'form': form, 'job': job})


@jobseeker_required
def my_applications(request):
    apps = Application.objects.filter(applicant=request.user).select_related('job', 'job__employer')
    return render(request, 'applications/my_applications.html', {'applications': apps})


@employer_required
def job_applicants(request, job_id):
    job  = get_object_or_404(Job, pk=job_id, employer=request.user)
    apps = Application.objects.filter(job=job).select_related('applicant')
    return render(request, 'applications/applicants.html', {'job': job, 'applications': apps})


@employer_required
def update_status(request, app_id):
    app = get_object_or_404(Application, pk=app_id, job__employer=request.user)
    if request.method == 'POST':
        form = StatusUpdateForm(request.POST, instance=app)
        if form.is_valid():
            form.save()
            messages.success(request, f'Status updated to "{app.get_status_display()}".')
    return redirect('applications:job_applicants', job_id=app.job.pk)