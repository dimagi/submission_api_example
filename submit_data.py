#!/usr/bin/env python3
"""
An example script to send data to CommCare using the Submission API

Usage:

    $ export CCHQ_USERNAME=user@example.com
    $ export CCHQ_PASSWORD=M7MwnA7okswFXwKC
    $ export CCHQ_USER_ID=c0ffeeeeeb574eb8b5d5036c9a61a483
    $ submit_data.py sample_data.csv

"""

# Configure the following settings with your values

# Your project space
PROJECT_SPACE = 'my-project-space'

# The case type of the cases you are sending to CommCare
CASE_TYPE = 'person'

# The ID of the user or location that your cases must be assigned to
OWNER_ID = 'c0ffeeeee1e34b12bb5da0dc838e8406'

# An XML namespace to identify your XForm submission
FORM_XMLNS = 'http://example.com/submission-api-example-form/'

# A string to identify the origin of your data
DEVICE_ID = "submission_api_example"

# End of configurable settings

import csv
import os
import sys
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from http.client import responses as http_responses
from typing import Any, Iterable, List, Optional, Tuple
from xml.etree import ElementTree as ET
import requests
from jinja2 import Template

COMMCARE_URL = 'https://www.commcarehq.org/'


@dataclass
class CaseProperty:
    name: str
    value: Any


@dataclass
class Case:
    id: str  # A UUID. Generated if not given in the data.
    name: str  # Required
    modified_on: str  # Generated if not given. e.g. "2020-06-08T18:41:33.207Z"
    properties: List[CaseProperty]  # All other given data
    server_modified_on: Optional[str]
    owner_id: str = OWNER_ID
    type: str = CASE_TYPE


def main(filename):
    """
    Sends data to CommCare HQ using the Submission API.
    """
    data = get_data(filename)
    cases = as_cases(data)
    xform_str = render_xform(cases)
    success, message = submit_xform(xform_str)
    return success, message


def get_data(csv_filename) -> Iterable[dict]:
    """
    Reads data in CSV format from the given filename, and yields it as
    dictionaries.
    """
    with open(csv_filename) as csv_file:
        reader = csv.DictReader(csv_file)
        yield from reader


def as_cases(data: Iterable[dict]) -> Iterable[Case]:
    """
    Casts dictionaries as Case instances
    """
    reserved = ('id', 'name', 'case_type', 'modified_on', 'server_modified_on')
    for dict_ in data:
        properties = [CaseProperty(name=key, value=value)
                      for key, value in dict_.items()
                      if key not in reserved]
        yield Case(
            id=dict_.get('id', str(uuid.uuid4())),
            name=dict_['name'],
            modified_on=dict_.get('modified_on', now_utc()),
            server_modified_on=dict_.get('server_modified_on'),
            properties=properties,
        )


def render_xform(cases: Iterable[Case]) -> str:
    context = {
        'form_xmlns': FORM_XMLNS,
        'device_id': DEVICE_ID,
        'now_utc': now_utc(),
        'cchq_username': os.environ['CCHQ_USERNAME'],
        'cchq_user_id': os.environ['CCHQ_USER_ID'],
        'submission_id': uuid.uuid4().hex,
        'cases': list(cases),
    }
    with open('xform_template.xml') as template_file:
        template = Template(template_file.read())
    xform = template.render(**context)
    return xform


def submit_xform(xform: str) -> Tuple[bool, str]:
    """
    Submits the given XForm to CommCare.

    Returns (True, success_message) on success, or (False,
    failure_message) on failure.
    """
    url = join_url(COMMCARE_URL, f'/a/{PROJECT_SPACE}/receiver/')
    auth = (os.environ['CCHQ_USERNAME'], os.environ['CCHQ_PASSWORD'])
    headers = {'Content-Type': 'text/html; charset=UTF-8'}
    response = requests.post(url, xform.encode('utf-8'),
                             headers=headers, auth=auth)
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


def missing_env_vars():
    return [env_var
            for env_var in ('CCHQ_USERNAME', 'CCHQ_PASSWORD', 'CCHQ_USER_ID')
            if env_var not in os.environ]


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit()
    if missing := missing_env_vars():
        print('Missing environment variables:', ', '.join(missing))
        sys.exit(1)
    success, message = main(sys.argv[1])
    print(message)
    if not success:
        sys.exit(1)
