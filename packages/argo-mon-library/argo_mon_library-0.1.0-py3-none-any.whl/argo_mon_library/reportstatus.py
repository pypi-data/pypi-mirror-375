from datetime import datetime

from .restresource import RestResourceItem, RestResourceList


class ReportStatusGroupStatus(RestResourceItem):
    """Class to represent the status of a group in a status report"""
    def __init__(self, parent, data={}):
        if data is not None:
            self.timestamp = datetime.strptime(
                str(data.get("timestamp")), "%Y-%m-%dT%H:%M:%SZ"
            )
            self.value = data.get("value")
        else:
            self.timestamp = ""
            self.value = ""

    def _fetch_route(self):
        return ""

    def _fetch_args(self) -> list:
        return []


class ReportStatusGroupStatuses(RestResourceList):
    """Collection class for group status entries in a status report"""
    def __init__(self, parent):
        super().__init__(parent, 1)
        self._fetch()

    def _fetch(self):
        for i in self._parent._statuses:
            self.update({i["timestamp"]: ReportStatusGroupStatus(self, i)})
            self._pageCount = 1
            self._currentPage = 1


class ReportStatusGroupEndpoint(RestResourceItem):
    """Class to represent a specific endpoint belonging to a group in a status report"""
    def __init__(self, parent, data={}):
        super().__init__(parent, data)
        if data is not None:
            self.name = data.get("hostname")
            self.service = data.get("service")
            self.id = data.get("info").get("ID")
            self.url = data.get("info").get("URL")
            self.statuses = data.get("statuses")
        else:
            self.hostname = ""
            self.service = ""
            self.id = ""
            self.url = ""
            self.statuses = []

    @property
    def statuses(self):
        return ReportStatusGroupStatuses(self)

    @statuses.setter
    def statuses(self, value):
        self._statuses = value

    def _fetch_route(self):
        return ""

    def _fetch_args(self) -> list:
        return []


class ReportStatusGroupEndpoints(RestResourceList):
    """Collection class for group endpoints in a status report"""
    def __init__(self, parent):
        super().__init__(parent, 1)
        self._fetch()

    def _fetch(self):
        for i in self._parent._endpoints:
            self.update({i["info"]["ID"]: ReportStatusGroupEndpoint(self, i)})
            self._pageCount = 1
            self._currentPage = 1

    def by_name(self, name: str):
        for i in self:
            if i.name == name:
                return i
        return None


class ReportStatusGroup(RestResourceItem):
    """Class to represent a specific group in a status report"""
    def __init__(self, parent, data={}):
        super().__init__(parent, data)
        if data is not None:
            self.name = data.get("name")
            self.type = data.get("type")
            self.statuses = data.get("statuses")
            self.endpoints = data.get("endpoints")
        else:
            self.name = ""
            self.type = ""

    @property
    def statuses(self):
        return ReportStatusGroupStatuses(self)

    @statuses.setter
    def statuses(self, value):
        self._statuses = value

    @property
    def endpoints(self):
        return ReportStatusGroupEndpoints(self)

    @endpoints.setter
    def endpoints(self, value):
        self._endpoints = value

    def _fetch_route(self):
        return ""

    def _fetch_args(self) -> list:
        return []


class ReportStatusGroups(RestResourceList):
    """Collection class for groups in a status report"""
    def __init__(self, parent):
        super().__init__(parent, 1)
        self._fetch()

    def _fetch(self):
        for i in self._parent._groups:
            self.update({i["name"]: ReportStatusGroup(self, i)})
            self._pageCount = 1
            self._currentPage = 1

    def _fetch_route(self):
        return ""

    def _fetch_args(self) -> list:
        return []

    def by_name(self, name: str):
        for i in self:
            if i.name == name:
                return i
        return None


class ReportStatus(RestResourceItem):
    """Main class for status reports"""
    @property
    def groups(self) -> ReportStatusGroups:
        return ReportStatusGroups(self)

    @groups.setter
    def groups(self, value):
        self._groups = value

    @property
    def data_root(self):
        return None

    def _fetch_route(self):
        return "get_report_status"

    def _fetch_args(self) -> list:
        return [self.id]

    def _fetch_params(self) -> dict:
        return {
            "start_time": (
                str(self._parent._parent._parent._period._start_date) + "Z"
            ).replace(" ", "T"),
            "end_time": (
                str(self._parent._parent._parent._period._end_date) + "Z"
            ).replace(" ", "T"),
        }
