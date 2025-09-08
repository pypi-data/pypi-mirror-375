import json
import logging
import socket

import requests

from .exceptions import (MonConnectionException, MonServiceException,
                         MonTimeoutException)

logger = logging.getLogger(__name__)


class HttpRequests(object):
    """Class for HTTP requests to the Monounting Service API"""

    def __init__(self, apikey: str):
        self.apikey = apikey.rstrip()

        self.routes = {
            "get_reports": [
                "get",
                "https://{0}/api/v2/reports",
            ],
            "get_report": [
                "get",
                "https://{0}/api/v2/reports/{1}",
            ],
            "get_report_status": [
                "get",
                "https://{0}/api/v3/status/{1}",
            ],
            "get_report_results": [
                "get",
                "https://{0}/api/v3/results/{1}",
            ],
            "get_resource_report_status": [
                "get",
                "https://{0}/api/v3/status/{1}/id/{2}",
            ],
            "get_resource_report_results": [
                "get",
                "https://{0}/api/v3/status/{1}/id/{2}",
            ],
        }

    def _error_dict(self, response_content, status):
        try:
            error_dict = json.loads(response_content) if response_content else dict()
        except ValueError:
            error_dict = {"error": {"code": status, "message": response_content}}

        return error_dict

    def make_request(
        self, url, route_name, params=None, body=None, **reqkwargs
    ) -> dict:
        """Common method for PUT, GET, POST HTTP requests with appropriate service error handling"""
        m = self.routes[route_name][0]
        decoded = None
        try:
            # populate all requests with the X-Api-Key apikey header
            # if there is no defined headers dict in the reqkwargs, introduce it
            if "headers" not in reqkwargs:
                headers = {
                    "X-Api-Key": "{0}".format(self.apikey),
                    "Accept": "application/json"
                }
                reqkwargs["headers"] = headers
            else:
                # if the there are already other headers defined, just append the X-Api-Key one
                reqkwargs["headers"]["X-Api-Key"] = "{0}".format(self.apikey)

            reqmethod = getattr(requests, m)
            logger.debug(
                "doing a "
                + reqmethod.__name__
                + " request on "
                + url
                + " with params "
                + str(params)
            )
            r = reqmethod(url, data=body, params=params, **reqkwargs)

            content = r.content
            status_code = r.status_code

            logger.debug("STATUS CODE:" + str(status_code))
            if status_code == 200 or status_code == 201:
                decoded = self._error_dict(content, status_code)

            # handle authn/z related errors for all calls
            elif status_code == 401 or status_code == 403:
                raise MonServiceException(
                    json=self._error_dict(
                        content or json.dumps({"message": "Auth failure"}),
                        status_code,
                    ),
                    request=route_name,
                )

            elif status_code == 408:
                raise MonTimeoutException(
                    json=self._error_dict(content, status_code), request=route_name
                )

            # handle any other erroneous behaviour by raising exception
            else:
                raise MonServiceException(
                    json=self._error_dict(content, status_code), request=route_name
                )

        except (
            requests.exceptions.ConnectionError,
            requests.exceptions.ReadTimeout,
            socket.error,
        ) as e:
            raise MonConnectionException(e, route_name)

        else:
            return decoded if decoded else {}
