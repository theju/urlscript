import urllib
import datetime
import multiprocessing

from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand, CommandError

from core.models import URL, Cron


def request_url(url):
    urllib.urlopen("http://{0}{1}".format(
        Site.objects.get_current().domain,
        reverse("run_fn", kwargs={"slug": url.slug})
    ))


class Command(BaseCommand):
    help = "Run the url scripts"
    can_import_settings = True

    def handle(self, *args, **options):
        pool = multiprocessing.Pool(multiprocessing.cpu_count())
        today = int(datetime.date.today().strftime("%s"))
        now = datetime.datetime.now()
        curr_time = int(now.strftime("%s")) - now.second
        mins_passed = int((curr_time - today) / 60.0)
        intervals = Cron.objects.filter(interval__lte=mins_passed)\
                                .values_list('interval', flat=True).\
                                order_by('interval').distinct()
        request = ""
        for interval in intervals:
            if mins_passed % interval == 0 or settings.DEBUG:
                for cron in Cron.objects.filter(interval=interval):
                    url = cron.url
                    pool.apply_async(request_url, (url, ))
        pool.close()
        pool.join()
