#!/usr/bin/env python3
"""
An example script to send data to CommCare using the Submission API

Usage:

    $ export CCHQ_PROJECT_SPACE=
    $ export CCHQ_USERNAME=
    $ export CCHQ_PASSWORD=
    $ export CCHQ_USER_ID=
"""


# A string to identify the origin of your data
DEVICE_ID = "submission_api_example"

# End of configurable settings

import csv
import os
import sys
import uuid
from datetime import datetime, timezone
from http.client import responses as http_responses
from typing import Any, Iterable, List, Optional, Tuple
from xml.etree import ElementTree as ET
import requests
from jinja2 import Template

COMMCARE_URL = 'https://www.commcarehq.org/'


class Answer: 
    text: str
    other_test: str

    def __init__(self, text: str, other_test: str): 
        self.text = text
        self.other_test = other_test


def main(filename):
    """
    Sends data to CommCare HQ using the Submission API.
    """
    data = get_data(filename)
    answers = as_cases(data)
    for answer in answers: 
        xform_str = render_xform(answer)
        success, message = submit_xform(xform_str)
        print (message)
    
    return "success", "message"


def get_data(csv_filename) -> Iterable[dict]:
    """
    Reads data in CSV format from the given filename, and yields it as
    dictionaries.
    """
    with open(csv_filename) as csv_file:
        reader = csv.DictReader(csv_file)
        yield from reader


def as_cases(data: Iterable[dict]) -> Iterable[Answer]:
    """
    Casts dictionaries as Case instances
    """
    for dict_ in data:
        yield Answer(
            text=dict_['text'],
            other_test=dict_['other_test']
        )


def render_xform(answer: Answer) -> str:
    context = {
        'device_id': DEVICE_ID,
        'now_utc': now_utc(),
        'cchq_username': os.environ['CCHQ_USERNAME'],
        'cchq_user_id': os.environ['CCHQ_USER_ID'],
        'submission_id': uuid.uuid4().hex,
        'answer': answer,
    }
    with open('xform.xml.j2') as template_file:
        template = Template(template_file.read())
    xform = template.render(**context)
    return xform


def submit_xform(xform: str) -> Tuple[bool, str]:
    """
    Submits the given XForm to CommCare.

    Returns (True, success_message) on success, or (False,
    failure_message) on failure.
    """
    url = join_url(COMMCARE_URL,
                   f'/a/{os.environ["CCHQ_PROJECT_SPACE"]}/receiver/')
    auth = (os.environ['CCHQ_USERNAME'], os.environ['CCHQ_PASSWORD'])
    headers = {'Content-Type': 'text/html; charset=UTF-8'}
    response = requests.post(url, xform.encode('utf-8'),
                             headers=headers, auth=auth)
    print(response)
    if not 200 <= response.status_code < 300:
        return False, http_responses[response.status_code]
    return parse_response(response.text)


def parse_response(text: str) -> Tuple[bool, str]:
    """
    Parses a CommCare HQ Submission API response.

    Returns (True, success_message) on success, or (False,
    failure_message) on failure.

    >>> text = '''
    ... <OpenRosaResponse xmlns="http://openrosa.org/http/response">
    ...     <message nature="submit_success">   √   </message>
    ... </OpenRosaResponse>
    ... '''
    >>> parse_response(text)
    (True, '   √   ')

    """
    xml = ET.XML(text)
    message = xml.find('{http://openrosa.org/http/response}message')
    success = message.attrib['nature'] == 'submit_success'
    return success, message.text


def join_url(base_url: str, endpoint: str) -> str:
    """
    Returns ``base_url`` + ``endpoint`` with the right forward slashes.

    >>> join_url('https://example.com/', '/api/foo')
    'https://example.com/api/foo'
    >>> join_url('https://example.com', 'api/foo')
    'https://example.com/api/foo'

    """
    return '/'.join((base_url.rstrip('/'), endpoint.lstrip('/')))


def now_utc() -> str:
    """
    Returns a UTC timestamp in ISO-8601 format with the offset as "Z".
    e.g. "2020-06-08T18:41:33.207Z"
    """
    now = datetime.now(tz=timezone.utc)
    now_iso = now.isoformat(timespec='milliseconds')
    now_iso_z = now_iso.replace('+00:00', 'Z')
    return now_iso_z

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit()
    success, message = main(sys.argv[1])
    print(message)
    if not success:
        sys.exit(1)
