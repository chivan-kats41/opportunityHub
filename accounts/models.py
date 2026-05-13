from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    JOBSEEKER = 'jobseeker'
    EMPLOYER  = 'employer'
    ROLE_CHOICES = [
        (JOBSEEKER, 'Job Seeker'),
        (EMPLOYER,  'Employer'),
    ]

    role         = models.CharField(max_length=20, choices=ROLE_CHOICES, default=JOBSEEKER)
    phone        = models.CharField(max_length=20, blank=True)
    bio          = models.TextField(blank=True)
    profile_photo = models.ImageField(upload_to='profiles/', blank=True, null=True)
    company_name = models.CharField(max_length=200, blank=True)  # employers only
    website      = models.URLField(blank=True)

    def is_employer(self):
        return self.role == self.EMPLOYER

    def is_jobseeker(self):
        return self.role == self.JOBSEEKER

    def __str__(self):
        return f'{self.get_full_name() or self.username} ({self.get_role_display()})'