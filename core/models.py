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

    def __str__(self):
        return self.slug
