from flask import make_response, render_template
from werkzeug.exceptions import HTTPException

class InputError(HTTPException):
    def __init__(self, status_code, error_code, error_message, html_page, trackers=None, tracker=None, username=None, condition=None, now=None, log=None):
        message = {"error_code": error_code, "error_message": error_message}
        self.response = make_response(render_template(html_page, error=error_message, trackers=trackers, tracker=tracker, username=username, condition=condition, now=now, log=log), status_code)

class ServerError(HTTPException):
    def __init__(self, status_code, error_code, error_message):
        message = {"error_code": error_code, "error_message": error_message}
        self.response = make_response(error_message, status_code)