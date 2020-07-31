# -*- coding: utf-8 -*-

"""Implements a simple wrapper around urlopen."""

from http.client import HTTPResponse
from typing import Dict, Iterable, Optional
from urllib.request import Request, urlopen


def _execute_request(
    url: str, method: Optional[str] = None, headers: Optional[Dict[str, str]] = None
) -> HTTPResponse:
    base_headers = {"User-Agent": "Mozilla/5.0"}
    if headers:
        base_headers.update(headers)
    if url.lower().startswith("http"):
        request = Request(url, headers=base_headers, method=method)
    else:
        raise ValueError("Invalid URL")
    return urlopen(request)  # nosec


def get(url) -> str:
    """Send an http GET request.

    :param str url:
        The URL to perform the GET request for.
    :rtype: str
    :returns:
        UTF-8 encoded string of response
    """
    return _execute_request(url).read().decode("utf-8")
