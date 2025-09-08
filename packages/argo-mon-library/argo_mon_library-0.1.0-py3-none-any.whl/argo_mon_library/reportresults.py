from datetime import datetime

from .restresource import RestResourceItem, RestResourceList


class ReportResultsGroup(RestResourceItem):
    """Class to represent group data in report results"""
    def __init__(self, parent, data={}):
        super().__init__(parent, data)
        if data is not None:
            self.name = data.get("name")
            self.type = data.get("type")
            self.results = data.get("results")

    @property
    def results(self):
        return ReportResultsResults(self)

    @results.setter
    def results(self, value):
        self._results = value

    def _fetch_route(self):
        return ""

    def _fetch_args(self) -> list:
        return []


class ReportResultsGroupsBase(RestResourceList):
    """Base class used by groups and supergroups in report results"""
    def __init__(self, parent):
        super().__init__(parent, 1)
        self._fetch()

    def _fetch_route(self):
        return ""

    def _fetch_args(self) -> list:
        return []

    def by_name(self, name: str):
        for i in self:
            if i.name == name:
                return i
        return None


class ReportResultsGroups(ReportResultsGroupsBase):
    """Class to represent a collection of groups in report results"""
    def _fetch(self):
        for i in self._parent._groups:
            self.update({i["name"]: ReportResultsGroup(self, i)})
        self._pageCount = 1
        self._currentPage = 1


class ReportResultsSupergroup(ReportResultsGroup):
    """Class to represent supergroups data in report results"""
    @property
    def groups(self) -> ReportResultsGroups:
        return ReportResultsGroups(self)

    @groups.setter
    def groups(self, value):
        self._groups = value


class ReportResultsSupergroups(ReportResultsGroupsBase):
    """Class to represent a collection of supergroups in report results"""
    def _fetch(self):
        for i in self._parent.results:
            self.update({i["name"]: ReportResultsSupergroup(self, i)})
        self._pageCount = 1
        self._currentPage = 1


class ReportResultsResult(RestResourceItem):
    """Class to represent a specific report result entry, pertaining to a (super)group far a specific time span"""
    def __init__(self, parent, data={}):
        super().__init__(parent, data)
        if data is not None:
            try:
                self.date = datetime.strptime(str(data.get("date")), "%Y-%m-%d")
            except ValueError:
                self.date = datetime.strptime(str(data.get("date")), "%Y-%m")
            self.availability = data.get("availability")
            self.reliability = data.get("reliability")
            self.unknown = data.get("unknown")
            self.uptime = data.get("uptime")
            self.downtime = data.get("downtime")

    def _fetch_route(self):
        return ""

    def _fetch_args(self) -> list:
        return []


class ReportResultsResults(RestResourceList):
    """Class to represent a collection of report result entries"""
    def __init__(self, parent):
        super().__init__(parent, 1)
        self._fetch()

    def _fetch(self):
        for i in self._parent._results:
            self.update({i["date"]: ReportResultsResult(self, i)})
            self._pageCount = 1
            self._currentPage = 1


class ReportResults(RestResourceItem):
    """Main class to represent report results"""
    @property
    def data_root(self):
        return None

    @property
    def supergroups(self) -> ReportResultsSupergroups:
        return ReportResultsSupergroups(self)

    def _fetch_route(self):
        return "get_report_results"

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
            "granularity": self._parent._parent._parent._period._granularity,
        }
