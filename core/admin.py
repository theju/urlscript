from django.contrib import admin

from .models import URL, Cron


admin.site.register(URL)
admin.site.register(Cron)
