from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def employer_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if not request.user.is_employer():
            messages.error(request, 'This page is for employers only.')
            return redirect('jobs:list')
        return view_func(request, *args, **kwargs)
    return wrapper


def jobseeker_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if not request.user.is_jobseeker():
            messages.error(request, 'This page is for job seekers only.')
            return redirect('jobs:list')
        return view_func(request, *args, **kwargs)
    return wrapper