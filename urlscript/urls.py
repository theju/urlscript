from django.urls import re_path, include
from django.contrib import admin

import core.urls

urlpatterns = [
    re_path(r'^admin/', admin.site.urls),

    re_path(r'^', include(core.urls)),
]
