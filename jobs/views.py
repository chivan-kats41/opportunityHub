from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from honeypot.decorators import check_honeypot
from .models import Job, Category
from .forms import JobForm, JobSearchForm
from accounts.decorators import employer_required


def index(request):
    """Homepage — hero + featured jobs + pricing section."""
    featured_jobs = Job.objects.filter(is_active=True, is_featured=True).select_related('category', 'employer')[:6]
    categories    = Category.objects.all()
    return render(request, 'jobs/index.html', {
        'featured_jobs': featured_jobs,
        'categories':    categories,
    })


def job_list(request):
    """Paginated, filtered job listings."""
    form = JobSearchForm(request.GET)
    jobs = Job.objects.filter(is_active=True).select_related('category', 'employer')

    if form.is_valid():
        q        = form.cleaned_data.get('q')
        location = form.cleaned_data.get('location')
        job_type = form.cleaned_data.get('job_type')
        category = form.cleaned_data.get('category')

        if q:
            jobs = jobs.filter(title__icontains=q) | jobs.filter(company_name__icontains=q) | jobs.filter(description__icontains=q)
        if location:
            jobs = jobs.filter(location__icontains=location)
        if job_type:
            jobs = jobs.filter(job_type=job_type)
        if category:
            jobs = jobs.filter(category=category)

    sort = request.GET.get('sort', 'relevant')
    if sort == 'newest':
        jobs = jobs.order_by('-created_at')
    elif sort == 'salary':
        jobs = jobs.order_by('-salary_range')
    else:
        jobs = jobs.order_by('-is_featured', '-created_at')

    paginator = Paginator(jobs, 10)
    page_obj  = paginator.get_page(request.GET.get('page'))
    categories = Category.objects.all()

    return render(request, 'jobs/list.html', {
        'page_obj':  page_obj,
        'form':      form,
        'categories': categories,
        'total':     jobs.count(),
        'sort':      sort,
    })


def job_detail(request, pk):
    job = get_object_or_404(Job, pk=pk, is_active=True)
    user_applied = False
    if request.user.is_authenticated and request.user.is_jobseeker():
        from applications.models import Application
        user_applied = Application.objects.filter(job=job, applicant=request.user).exists()
    return render(request, 'jobs/detail.html', {'job': job, 'user_applied': user_applied})


@employer_required
@check_honeypot
def job_create(request):
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.employer = request.user
            if not job.company_name:
                job.company_name = request.user.company_name
            job.save()
            messages.success(request, f'Job "{job.title}" posted successfully!')
            return redirect('jobs:detail', pk=job.pk)
    else:
        form = JobForm(initial={'company_name': request.user.company_name})
    return render(request, 'jobs/create.html', {'form': form})


@employer_required
@check_honeypot
def job_edit(request, pk):
    job = get_object_or_404(Job, pk=pk, employer=request.user)
    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, 'Job updated successfully.')
            return redirect('jobs:detail', pk=job.pk)
    else:
        form = JobForm(instance=job)
    return render(request, 'jobs/edit.html', {'form': form, 'job': job})


@employer_required
def job_delete(request, pk):
    job = get_object_or_404(Job, pk=pk, employer=request.user)
    if request.method == 'POST':
        title = job.title
        job.delete()
        messages.success(request, f'Job "{title}" deleted.')
        return redirect('dashboard:employer')
    return render(request, 'jobs/confirm_delete.html', {'job': job})


@employer_required
def my_jobs(request):
    jobs = Job.objects.filter(employer=request.user).order_by('-created_at')
    return render(request, 'jobs/my_jobs.html', {'jobs': jobs})



def companies_list(request):
    """Public companies directory — employers who have posted active jobs."""
    q = request.GET.get('q', '').strip()
 
    employers = (
        Job.objects
        .filter(is_active=True)
        .values(
            'employer_id',
            'employer__username',
            'employer__first_name',
            'employer__last_name',
            'employer__company_name',
            'employer__website',
            'employer__profile_photo',
            'company_name',
        )
        .annotate(
            open_jobs=Count('id'),
            latest_post=Max('created_at'),
        )
        .order_by('-open_jobs', '-latest_post')
    )
 
    if q:
        employers = employers.filter(company_name__icontains=q)
 
    paginator = Paginator(employers, 12)
    page_obj  = paginator.get_page(request.GET.get('page'))
 
    return render(request, 'jobs/companies.html', {
        'page_obj': page_obj,
        'total':    paginator.count,
        'q':        q,
    })