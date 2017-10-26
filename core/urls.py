from django.conf.urls import url

import core.views

urlpatterns = [
    url(r'^u/(?P<slug>[\w\-\+\.]+)/?$', core.views.run_fn, name="run_fn"),
]
