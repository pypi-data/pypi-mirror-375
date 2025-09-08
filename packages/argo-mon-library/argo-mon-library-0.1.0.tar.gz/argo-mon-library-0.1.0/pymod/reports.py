import json
from datetime import datetime

from .reportresults import ReportResults
from .reportstatus import ReportStatus
from .restresource import RestResourceItem, RestResourceList


class ReportThresholds(object):
    """Report thresholds representation class"""
    def __init__(self, data={}):
        if data is not None:
            self.availability = data.get("availability")
            self.reliability = data.get("reliability")
            self.uptime = data.get("uptime")
            self.unknown = data.get("unknown")
            self.downtime = data.get("downtime")
        else:
            self.availability = 0
            self.reliability = 0
            self.uptime = 0.0
            self.unknown = 0.0
            self.downtime = 0.0

    def __str__(self):
        return json.dumps(self.__dict__)


class ReportProfile(object):
    """Report profile representation class"""
    def __init__(self, parent, data={}):
        if data is not None:
            self.id = data.get("id")
            self.type = data.get("type")
            self.name = data.get("name")
        else:
            self.id = ""
            self.type = ""
            self.name = ""

    def __str__(self):
        return json.dumps(self.__dict__)


class ReportProfiles(RestResourceList):
    """Report profile collection class"""
    def __init__(self, parent, data={}):
        super().__init__(parent, 1)
        self._fetch()

    def _fetch(self):
        for i in self._parent._profiles:
            self.update({i["id"]: ReportProfile(self, i)})
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


class ReportFilterTag(RestResourceItem):
    """Report filter tag representation class"""
    def __init__(self, parent, data={}):
        super().__init__(parent, data)
        if data is not None:
            self.name = data.get("name")
            self.value = data.get("value")
            self.context = data.get("context")
        else:
            self.name = ""
            self.value = ""
            self.context = ""

    def _fetch_route(self):
        return ""

    def _fetch_args(self) -> list:
        return []


class ReportFilterTags(RestResourceList):
    """Report filter tag collection class"""
    def __init__(self, parent, data={}):
        super().__init__(parent, 1)
        self._fetch()

    def _fetch(self):
        for i in self._parent._filter_tags:
            self.update({i["name"]: ReportFilterTag(self, i)})
            self._pageCount = 1
            self._currentPage = 1

    def _fetch_route(self):
        return ""

    def _fetch_args(self) -> list:
        return []


class ReportTopologySchemaGroup(RestResourceItem):
    """Report topology schema group representation class"""
    def __init__(self, parent, data={}):
        super().__init__(parent, data)
        if data is not None:
            self.type = data.get("type")
            if data.get("group") is not None:
                self.group = ReportTopologySchemaGroup(self, data.get("group"))
            else:
                self.group = None
        else:
            self.type = ""
            self.group = None

    def _fetch_route(self):
        return ""

    def _fetch_args(self) -> list:
        return []


class ReportTopologySchema(RestResourceItem):
    """Report topology schema entry representation class, beloning to a group"""
    def __init__(self, parent, data={}):
        super().__init__(parent, data)
        if data is not None:
            self.group = ReportTopologySchemaGroup(self, data.get("group"))
        else:
            self.group = None

    def _fetch_route(self):
        return ""

    def _fetch_args(self) -> list:
        return []


class ReportComputations(object):
    """Report computations representation class"""
    def __init__(self, data={}):
        if data is not None:
            self.ar = data.get("ar")
            self.status = data.get("status")
            self.trends = data.get("trends")
        else:
            self.ar = False
            self.status = False
            self.trends = []

    def __str__(self):
        return json.dumps(self.__dict__)


class Report(RestResourceItem):
    """Main class for monitoring reports"""

    @property
    def info(self):
        return self._info

    @info.setter
    def info(self, value):
        self._info = value

    @property
    def name(self) -> str:
        return self._info["name"]

    @property
    def description(self) -> str:
        return self._info["description"]

    @property
    def tenant(self):
        return self._tenant

    @tenant.setter
    def tenant(self, value):
        self._tenant = value

    @property
    def disabled(self):
        return self._disabled

    @disabled.setter
    def disabled(self, value):
        self._disabled = value

    @property
    def created_on(self) -> datetime:
        return datetime.strptime(self._info["created"], "%Y-%m-%d %H:%M:%S")

    @property
    def updated_on(self) -> datetime:
        return datetime.strptime(self._info["updated"], "%Y-%m-%d %H:%M:%S")

    @property
    def computations(self) -> ReportComputations:
        return ReportComputations(self._computations)

    @computations.setter
    def computations(self, value):
        self._computations = value

    @property
    def thresholds(self) -> ReportThresholds:
        return ReportThresholds(self._thresholds)

    @thresholds.setter
    def thresholds(self, value):
        self._thresholds = value

    @property
    def profiles(self) -> ReportProfiles:
        return ReportProfiles(self, self._profiles)

    @profiles.setter
    def profiles(self, value):
        self._profiles = value

    @property
    def filter_tags(self) -> ReportFilterTags:
        return ReportFilterTags(self, self._filter_tags)

    @filter_tags.setter
    def filter_tags(self, value):
        self._filter_tags = value

    @property
    def topology_schema(self) -> ReportTopologySchema:
        return ReportTopologySchema(self, self._topology_schema)

    @topology_schema.setter
    def topology_schema(self, value):
        self._topology_schema = value

    def _fetch_route(self):
        return "get_report"

    def _fetch_args(self) -> list:
        return [self.id]

    @property
    def status(self) -> ReportStatus:
        return ReportStatus(self, {"__fetch__": self.name})

    @property
    def results(self) -> ReportResults:
        return ReportResults(self, {"__fetch__": self.name})


class Reports(RestResourceList):
    """Collection class for report lists"""
    def _fetch_route(self):
        return "get_reports"

    def _fetch_args(self) -> list:
        return []

    def _create_child(self, data):
        return Report(self, data)

    def by_name(self, name: str):
        for i in self:
            if i.name == name:
                return i
        return None
