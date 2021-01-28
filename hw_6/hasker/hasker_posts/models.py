from django.db import models
from django.utils import timezone

from hasker_login.models import HaskerUser


class Questions(models.Model):
    id = models.IntegerField(primary_key=True, auto_created=True)
    title = models.CharField(max_length=300, blank=False, null=False)
    contains = models.CharField(max_length=5000, blank=False, null=False)
    author = models.ForeignKey(HaskerUser, on_delete=models.SET_NULL, blank=True, null=True)
    created = models.DateTimeField(default=timezone.now)
    tags = models.CharField(max_length=300, blank=True, null=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = "Hasker Question"
        verbose_name_plural = "Hasker  Questions"


class Answers(models.Model):
    id = models.IntegerField(primary_key=True, auto_created=True)
    question = models.ForeignKey(Questions, on_delete=models.SET_NULL, blank=True, null=True)
    contains = models.CharField(max_length=5000, blank=False, null=False)
    author = models.ForeignKey(HaskerUser, models.SET_NULL, blank=True, null=True)
    created = models.DateTimeField(default=timezone.now)
    marker_is_correct = models.BooleanField(blank=True, null=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = "Hasker Answer"
        verbose_name_plural = "Hasker Answers"


class Tags(models.Model):
    id = models.IntegerField(primary_key=True, auto_created=True)
    tag = models.CharField(max_length=100, blank=False, null=False)
    created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.tag

    class Meta:
        verbose_name = "Hasker Tag"
        verbose_name_plural = "Hasker Tags"

