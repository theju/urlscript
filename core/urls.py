from django.urls import re_path

import core.views

urlpatterns = [
    re_path(r'^u/(?P<slug>[\w\-\+\.]+)/?$', core.views.run_fn, name="run_fn"),
]
