class MonException(Exception):
    """Base exception class for all Argo Monitoring service related errors"""

    def __init__(self, *args, **kwargs):
        super(MonException, self).__init__(*args, **kwargs)


class MonServiceException(MonException):
    """Exception for Argo Monitoring Service API errors"""

    def __init__(self, json, request):
        errord = dict()

        if json.get("message"):
            self.msg = "While trying the [{0}]: {1}".format(request, json["message"])
            errord.update(error=self.msg)

        if json.get("code"):
            self.code = json["code"]
            errord.update(status_code=self.code)

        super(MonServiceException, self).__init__(errord)


class MonTimeoutException(MonServiceException):
    """Exception for timeouts errors

    Timeouts can come from the load balancer for partial requests that were not
    completed in the required time frame.
    """

    def __init__(self, json, request):
        super(MonTimeoutException, self).__init__(json, request)


class MonConnectionException(MonException):
    """Exception for connection related problems catched from requests library"""

    def __init__(self, exp, request):
        self.msg = "While trying the [{0}]: {1}".format(request, repr(exp))
        super(MonConnectionException, self).__init__(self.msg)
