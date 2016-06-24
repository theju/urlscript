# URLScript

A script for every URL.

On accessing a URL, you can run a script in your favourite language
within a sandbox (powered by [bubblewrap](https://github.com/projectatomic/bubblewrap)).

**Note**: This project has been developed and tested against Python3 in a
Fedora cloud VM. It should work in other distros and python versions as well.

## Installation

```bash
$ git clone https://github.com/theju/urlscript.git
$ git clone https://github.com/projectatomic/bubblewrap.git
$ cd bubblewrap
$ make
$ cd ..
$ virtualenv us_env
$ source us_env/bin/activate
$ cd urlscript
$ pip install -r requirements.txt
// Create a local.py under urlscript/urlscript to customize the settings.py
$ python manage.py migrate
$ python manage.py createsuperuser
$ python manage.py runserver
```

## Configuration

Under the `urlscript/urlscript` directory, you have a `settings.py` file that
contains a lot of the configuration details (see [django settings](https://docs.djangoproject.com/en/1.9/topics/settings/)).

Settings specific to URLScript:

- BUBBLEWRAP_PATH: Path where the `bwrap` executable resides
- SCRIPTS_TMP_DIR: Where the temporary stdin, stdout and script will reside
- SCRIPT_TIMEOUT: The max time for the script to run
- LANGUAGE_EXECUTABLE: The executable path for the languages.

To customize these variables, you can create a `local.py` under the `urlscript/urlscript`
directory.

Visit `http://localhost:8000/admin/` and login to the admin with the above created
credentials. Then create a new URL and then access `http://localhost:8000/u/<slug>/`
to run the script.

## API

Every URLScript will have access to stdin, stdout, stderr apart from other
portions of the filesystem (may be readonly). It may read the details of
the request from the stdin and may write out to the stdout.

The stdin contains the details of the corresponding request that spawned
the script. The stdin data is formatted as JSON and will have the following
attributes (inspired from django's [HTTPRequest](https://docs.djangoproject.com/en/1.9/ref/request-response/#httprequest-objects)).

- path: The URL that was accessed. Example: /u/some-script-slug/
- method: The HTTP method. Example: 'GET', 'POST' etc. Default: GET
- encoding: The encoding used to decode the form.
- headers: The list of all the HTTP headers. Please see [this](https://docs.djangoproject.com/en/1.9/ref/request-response/#django.http.HttpRequest.META) for more details.
- COOKIES: Key-value pair of all cookies. Default: {}
- GET: Key-value pairs of the HTTP GET parameters. Default: {}
- POST: Key-value pairs of the HTTP POST parameters. Default: {}
- FILES: Key-value pairs of the uploaded files. Default: {}
- body: String that has the HTTP request body. Useful for low level file
upload processing. The value of this attribute is base64 encoded.

The stdout may contain the details of the response to be sent out. The stdout must be a
JSON encoded object with the following attributes (inspired from django's
[HTTPResponse](https://docs.djangoproject.com/en/1.9/ref/request-response/#httpresponse-objects)).

- content_type: The mime-type of the response to be sent out.
Example: application/json (default: text/plain)
- headers: The headers of the response represented as key-value pairs.
Example: {"Content-Disposition": "attachment"}. Default: {}
- status_code: The status code of the response as an integer.
Example: 400 (default: 200)
- cookies: The key-value pairs of cookies to be set on the response.
Example: {'utm_src': {'value': 'gg', 'max_age': 86400, 'httponly': True}. Default: {}
- content: The content as a string. Default: '' (empty string)

## Example python script

```python
import requests
import json
import sys
import re

req_data = sys.stdin.read()
req = json.loads(req_data)

if re.compile('image').search(req['headers'].get('HTTP_ACCEPT', '')):
    # HTTP Post to an external URL
    requests.post("http://requestb.in/<some_random_scr>")

# Write out a 1x1 png
output = {
    "content_type": "image/png",
    "headers": {},
    "content": "\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDAT\x08\xd7c````\x00\x00\x00\x05\x00\x01^\xf3*:\x00\x00\x00\x00IEND\xaeB`\x82",
    "status_code": 200,
    "cookies": {}
}
sys.stdout.write(json.dumps(output))
# Below line should not be required but just in case
sys.stdout.flush()
```

## Cron-like functionality

It is possible to trigger the running of scripts periodically using the cron functionality.
In the admin select the url you want to invoke periodically every interval minutes.

Setup the django management command in your server's cron to run the management command to
automate this.

In `/etc/cron.d/` create a new file called urlscript with the following contents:

```bash
SHELL=/bin/bash
* * * * * ubuntu source ~/us_env/bin/activate && cd ~/urlscript && python manage.py run_urlscript
```

## Supported Languages

- Python
- Javascript (Node)

Support for other languages should also be possible. Feel free to send a PR to add support.
