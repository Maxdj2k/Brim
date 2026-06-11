from django.contrib.auth.models import User
from django.db import models


class SiteScan(models.Model):
    url = models.URLField(unique=True)
    domain = models.CharField(max_length=255)
    score = models.FloatField(default=0)
    reachable = models.BooleanField(default=False)
    signals = models.JSONField(default=dict)
    scanned_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.domain} ({self.score})"


class SiteReview(models.Model):
    url = models.URLField()
    domain = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="site_reviews")
    accreditation = models.PositiveSmallIntegerField(default=3)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("url", "user")

    def __str__(self):
        return f"{self.user.username} -> {self.domain} ({self.accreditation})"
