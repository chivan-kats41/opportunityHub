from django.db import models
from django.conf import settings
from jobs.models import Job


def resume_upload_path(instance, filename):
    return f'resumes/user_{instance.applicant.id}/{filename}'


class Application(models.Model):
    PENDING  = 'pending'
    REVIEWED = 'reviewed'
    ACCEPTED = 'accepted'
    REJECTED = 'rejected'

    STATUS_CHOICES = [
        (PENDING,  'Pending'),
        (REVIEWED, 'Reviewed'),
        (ACCEPTED, 'Accepted'),
        (REJECTED, 'Rejected'),
    ]

    job          = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    applicant    = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='applications')
    cover_letter = models.TextField(blank=True)
    resume       = models.FileField(upload_to=resume_upload_path)
    status       = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    applied_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('job', 'applicant')
        ordering = ['-applied_at']

    def __str__(self):
        return f'{self.applicant.get_full_name()} → {self.job.title}'

    def get_status_badge_class(self):
        badge_map = {
            self.PENDING:  'bg-warning text-dark',
            self.REVIEWED: 'bg-info text-dark',
            self.ACCEPTED: 'bg-success',
            self.REJECTED: 'bg-danger',
        }
        return badge_map.get(self.status, 'bg-secondary')