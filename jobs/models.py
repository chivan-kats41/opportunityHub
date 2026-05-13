from django.db import models
from django.conf import settings
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Job(models.Model):
    FULL_TIME  = 'full_time'
    PART_TIME  = 'part_time'
    REMOTE     = 'remote'
    CONTRACT   = 'contract'
    INTERNSHIP = 'internship'

    JOB_TYPE_CHOICES = [
        (FULL_TIME,  'Full-time'),
        (PART_TIME,  'Part-time'),
        (REMOTE,     'Remote'),
        (CONTRACT,   'Contract'),
        (INTERNSHIP, 'Internship'),
    ]

    title        = models.CharField(max_length=200)
    description  = models.TextField()
    company_name = models.CharField(max_length=200)
    location     = models.CharField(max_length=200)
    job_type     = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES, default=FULL_TIME)
    salary_range = models.CharField(max_length=100, blank=True, help_text='e.g. UGX 5M – 8M or USD 1,500/mo')
    category     = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='jobs')
    employer     = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posted_jobs')
    deadline     = models.DateField(null=True, blank=True)
    is_active    = models.BooleanField(default=True)
    is_featured  = models.BooleanField(default=False)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_featured', '-created_at']

    def __str__(self):
        return f'{self.title} @ {self.company_name}'

    def get_job_type_badge(self):
        badge_map = {
            self.FULL_TIME:  'badge-ft',
            self.PART_TIME:  'badge-pt',
            self.REMOTE:     'badge-remote',
            self.CONTRACT:   'badge-contract',
            self.INTERNSHIP: 'badge-internship',
        }
        return badge_map.get(self.job_type, 'badge-secondary')

    @property
    def application_count(self):
        return self.applications.count()