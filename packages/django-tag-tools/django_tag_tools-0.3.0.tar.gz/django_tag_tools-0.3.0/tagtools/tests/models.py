from __future__ import unicode_literals

from django.db import models

from taggit.managers import TaggableManager
from taggit.models import Tag


class Headline(models.Model):
    headline = models.CharField(max_length=50)

    tags = TaggableManager()

    def __str__(self):
        return self.headline
