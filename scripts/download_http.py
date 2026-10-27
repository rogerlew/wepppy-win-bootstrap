"""Bounded HTTP diagnostics shared by the bootstrap download clients."""
import json
import re
from http.client import IncompleteRead
from urllib.error import HTTPError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

MAX_ERROR_BYTES = 8192


class DownloadError(RuntimeError):
    pass


class DownloadRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        old, new = urlsplit(req.full_url), urlsplit(newurl)
        redirected = super().redirect_request(req, fp, code, msg, headers, newurl)
        if redirected is not None and (old.scheme, old.netloc) != (new.scheme, new.netloc):
            redirected.remove_header('Authorization')
        return redirected


def describe_http_error(error, token=''):
    incomplete = False
    try:
        body = error.read(MAX_ERROR_BYTES + 1)
    except IncompleteRead as failure:
        body = failure.partial
        incomplete = True
    except OSError:
        body = b'Unable to read server error body; connection interrupted or timed out.'
    text = body[:MAX_ERROR_BYTES].decode('utf-8', errors='replace')
    reference = error.headers.get('X-Request-Id') or error.headers.get('X-Correlation-Id')
    code = None
    try:
        payload = json.loads(text)
    except (ValueError, TypeError):
        payload = None
    if isinstance(payload, dict):
        detail = payload.get('error', payload.get('detail'))
        if isinstance(detail, dict):
            text = detail.get('message') or detail.get('details') or 'Server request failed.'
            code = detail.get('code')
        elif isinstance(detail, str):
            text = detail
        reference = payload.get('request_id') or reference
    if '<html' in str(text).lower() or '<!doctype' in str(text).lower():
        text = re.sub(r'<[^>]*>', ' ', str(text))
    message = f'HTTP {error.code} {error.reason}: {text or "Server returned no error body."}'
    if code:
        message += f'\nError code: {code}'
    if reference:
        message += f'\nRequest ID: {reference}'
    if len(body) > MAX_ERROR_BYTES:
        message += '\n[Server error body truncated]'
    if incomplete:
        message += '\n[Server error body incomplete]'
    # Prevent server-supplied terminal controls, retaining ordinary line breaks.
    message = ''.join(c for c in message if c in '\n\t' or c.isprintable())
    return message.replace(token, '[redacted]') if token else message


def open_download(url, token='', *, headers=None, timeout=None):
    # Keep the existing initial-fetch timeout behavior. Only the new failed-file
    # diagnostic requests impose an explicit socket timeout.
    request_headers = dict(headers or {})
    if token:
        request_headers['Authorization'] = 'Bearer ' + token
    try:
        return build_opener(DownloadRedirect()).open(
            Request(url, headers=request_headers), timeout=timeout)
    except HTTPError as error:
        try:
            message = describe_http_error(error, token)
        finally:
            error.close()
        raise DownloadError(message) from None
