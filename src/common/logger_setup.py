import logging

from flask import has_request_context, request


class RequestIDFilter(logging.Filter):
    def filter(self, record):
        if has_request_context():
            record.request_id = getattr(request, 'request_id', 'no-request-id')
            record.url = getattr(request, 'url', 'no-url')
        else:
            record.request_id = 'not-request'
            record.url = 'not-request'
        return True
