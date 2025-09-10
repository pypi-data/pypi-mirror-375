"""Utility functions for the datascribe API.

This module provides utility functions for DataScribe API interactions.
"""

import backoff
import requests
from requests import Session
from requests.exceptions import RequestException


def retry_session() -> Session:
    """Create a requests session with retry logic for handling request exceptions.

    This function uses the `backoff` library to retry requests that fail due to
    network-related errors, such as connection timeouts or server errors.

    Returns:
        Session: A session object that will retry requests on failure.
    """
    session = requests.Session()
    backoff.on_exception(
        backoff.expo,
        RequestException,
        max_time=60,
    )(session.request)
    return session
