import sys
from datetime import datetime
from typing import Optional, Union

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

from .exceptions import MonException
from .httprequests import HttpRequests
from .reports import Reports


class Period(object):
    """
    Helper class used for period definition (start/end date and granularity) for service API calls that need a
    reporting period. See the ArgoMonitoringService::period method for more details.
    """

    def __init__(
        self,
        start_date: Union[datetime, str],
        end_date: Union[datetime, str, None] = None,
        granularity: str = "daily",
    ):
        self._start_date: datetime
        self._end_date: datetime
        if type(start_date) is str:
            if start_date == "now":
                self._start_date = datetime.now()
            elif start_date == "today":
                self._start_date = datetime.now().replace(
                    hour=0, minute=0, second=0, microsecond=0
                )
            else:
                self._start_date = datetime.strptime(
                    start_date, "%Y-%m-%dT%H:%M:%SZ"
                )
        elif type(start_date) is datetime:
            self._start_date = start_date
        else:
            raise ValueError("Invalid type for parameter 'start_date'")
        if end_date is None:
            self._end_date = self._start_date.replace(
                hour=23, minute=59, second=59, microsecond=0
            )
        else:
            if type(end_date) is str:
                if end_date == "now":
                    self._end_date = datetime.now()
                elif end_date == "today":
                    self._end_date = datetime.now().replace(
                        hour=0, minute=0, second=0, microsecond=0
                    )
                else:
                    self._end_date = datetime.strptime(end_date, "%Y-%m-%dT%H:%M:%SZ")
            elif type(end_date) is datetime:
                self._end_date = end_date
            else:
                raise ValueError("Invalid type for parameter 'end_date'")
        if granularity in ["daily", "monthly", "custom"]:
            self._granularity = granularity
        else:
            raise MonException("Invalid granularity parameter")


class ArgoMonitoringService(object):
    """Module main class, to access the REST API"""

    def __init__(self, endpoint: str, apikey: str):
        self._endpoint = endpoint
        self._conn = HttpRequests(apikey)
        self._period = Period(
            datetime.now().replace(hour=0, minute=0, second=0, microsecond=0),
            datetime.now().replace(hour=23, minute=59, second=59, microsecond=0),
        )
        self._reports: Optional[Reports] = None

    @property
    def reports(self) -> Reports:
        """
        Access a list of reports for the current tenant
        """
        self._reports = self._reports or Reports(self)
        return self._reports

    @property
    def connection(self):
        return self._conn

    @property
    def endpoint(self):
        return self._endpoint

    def period(
        self,
        start_date: Union[datetime, str],
        end_date: Union[datetime, str, None] = None,
        granularity="daily",
    ) -> Self:
        """
        Define a period for requests that need a start and end date. After a call to this method, subsequent calls
        will use the same period, until another call changes it. Omitting the end_date parameter will default to the
        end of the same day as the start_date parameter (H:M:S=23:59:59).

        Both start_date and end_date may be either python datetime objects, or Zulu-formatted date-time strings, i.e.:
            1979-01-01T00:00:00Z

        Other datetime formats when passing strings are not supported, with the exception of the literals 'now' and
        'today' which will use the current date and/or time.

        The optional granularity parameter may take the values of 'daily' (default) or 'monthly' and will be used
        to group result values per the respected time frame.
        """
        self._period = Period(start_date, end_date, granularity)
        return self
