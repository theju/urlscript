from django.db import models
from django.utils.translation import ugettext_lazy as _


LANGS = (
    ('py', _('Python')),
    ('js', _('Javascript')),
)


class URL(models.Model):
    slug = models.CharField(max_length=10, unique=True, db_index=True)
    language = models.CharField(max_length=20, choices=LANGS)
    script = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.slug


class Cron(models.Model):
    url = models.ForeignKey('URL')
    # Interval in minutes
    interval = models.PositiveIntegerField(default=60)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{0} - {1}".format(self.url, self.interval)
