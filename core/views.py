import re
import os
import sys
import json
import codecs
import subprocess

from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import Http404, HttpResponse, HttpResponseBadRequest

from .models import URL

HTTP_HEADER_RE = re.compile("HTTP_")


def get_headers(request):
    headers = {}
    for key in request.META:
        if HTTP_HEADER_RE.search(key) == 0:
            headers[key] = request.META[key]
    return headers


@csrf_exempt
def run_fn(request, slug=None):
    try:
        url_script = URL.objects.get(slug=slug)
    except URL.DoesNotExist:
        raise Http404

    lang = url_script.language

    base_dir = os.path.join(
        settings.SCRIPTS_TMP_DIR,
        url_script.slug
    )
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    # Handle the uploaded stuff
    body = codecs.encode(request.body, "base64").decode('utf8')
    files = {}
    for key in request.FILES:
        uploaded_file = open(os.path.join(base_dir, key), "wb")
        uploaded_file.write(request.FILES[key].read())
        uploaded_file.close()
        files[key] = uploaded_file.name

    stdin = {
        "path": request.path,
        "method": request.method,
        "encoding": request.encoding or settings.DEFAULT_CHARSET,
        "headers": get_headers(request),
        "COOKIES": request.COOKIES,
        "GET": request.GET,
        "POST": request.POST,
        "FILES": files,
        "body": body
    }

    stdin_file = open(os.path.join(base_dir, "in"), "w")
    stdin_file.write(json.dumps(stdin))
    stdin_file.close()
    stdin_file = open(os.path.join(base_dir, "in"), "r")

    stdout_file = open(os.path.join(base_dir, "out"), "w")
    stderr_file = open(os.path.join(base_dir, "err"), "w")

    with open(os.path.join(base_dir, "script"), "w") as script_file:
        script_file.write(url_script.script)
        script_file.close()
        bwrap_executable = [os.path.join(settings.BUBBLEWRAP_PATH, "bwrap")]
        options = [
            "--dir", "/tmp",
            "--proc", "/proc",
            "--dev", "/dev",
            "--ro-bind", "/usr", "/usr",
            "--ro-bind", "/etc/resolv.conf", "/etc/resolv.conf",
            "--ro-bind", "/etc/ssl", "/etc/ssl",
            "--ro-bind", "/etc/pki", "/etc/pki",
            "--symlink", "usr/lib", "/lib",
            "--symlink", "usr/lib64", "/lib64",
            "--symlink", "usr/bin", "/bin",
            "--symlink", "usr/sbin", "/sbin",
            "--unshare-user",
            "--uid", "0",
            "--gid", "0",
            "--unshare-pid",
            "--dir", "/run/user/0",
            "--chdir", "/run/user/0",
            "--bind", script_file.name, "/run/user/0/script." + lang,
        ]
        custom_options = settings.BWRAP_CUSTOM_OPTIONS
        executable = [
            settings.LANGUAGE_EXECUTABLE[url_script.language],
            "script." + lang,
        ]
        cmd = bwrap_executable + options + custom_options + executable
        try:
            exit_code = subprocess.call(
                cmd,
                stdin=stdin_file,
                stdout=stdout_file,
                stderr=stderr_file,
                shell=False,
                timeout=settings.SCRIPT_TIMEOUT
            )
        except subprocess.TimeoutExpired as ex:
            exit_code = -1
            stderr_file.write("TimedOut")
        finally:
            stdin_file.close()
            stdout_file.close()
            stderr_file.close()
        if exit_code != 0:
            stderr = open(stderr_file.name, "r").read()
            return HttpResponseBadRequest(stderr, content_type="text/plain")
        else:
            try:
                stdout = json.loads(open(stdout_file.name, "r").read())
                content_type = stdout.get("content_type", "text/plain")
                content = stdout.get("content", "")
                response = HttpResponse(content, content_type=content_type)
                response.status_code = stdout.get("status_code", 200)
                headers = stdout.get("headers", {})
                for (key, val) in headers.items():
                    response[key] = val
                cookies = stdout.get("cookies", {})
                for key in cookies:
                    response.set_cookie(key, **cookies[key])
                return response
            except ValueError:
                pass

    return HttpResponseBadRequest("Error", content_type="text/plain")
