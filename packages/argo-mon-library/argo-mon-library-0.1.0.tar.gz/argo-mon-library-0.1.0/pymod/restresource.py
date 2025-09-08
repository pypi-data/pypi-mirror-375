import abc
import json
import logging
from collections import OrderedDict
from typing import Union

logger = logging.getLogger(__name__)


class RestResource(abc.ABC):
    """Base class for REST API responses"""

    def __init__(self, parent):
        """Initialize a REST response

        Args:
            parent(oject): an ArgoMonitoringService object or another RestResource instance
        """
        self._parent = parent

    @property
    def endpoint(self):
        return self._parent.endpoint

    @property
    def connection(self):
        return self._parent.connection

    @property
    def id_name(self):
        """
        Return the JSON field name that identifies the resource.
        Defaults to "id", subclasses may need to override it
        """
        return "id"

    @property
    def data_root(self):
        """
        Return the JSON field name that contains the resource data.
        Defaults to "data", subclasses may need to override it
        """
        return "data"

    def _fetch_params(self) -> dict:
        """Method to provide values for querystring params on the GET REST route"""
        return {}


class RestResourceItem(RestResource):
    """Base class for REST API responses representing a single item"""

    def __init__(self, parent, data: dict):
        """
        Initialize a REST response item, setting properties from provided data dictionary.
        If the dictionary contains a single entry named "__fetch__" instead of actual response data,
        then the data will be fetched from the API.
        """
        logger.debug("Initing RestResourceItem object " + str(type(self)))
        self._parent = parent
        self.id = None
        if len(data) == 1 and data.get("__fetch__") is not None:
            self.id = data["__fetch__"]
            if self.data_root is None:
                data = self._fetch()
            else:
                data = self._fetch()[self.data_root][0]
        for k in data:
            # logger.debug("setting " + k + " to " + (str(data[k]) or "<None>"))
            setattr(self, k, data[k])

    def __str__(self):
        """Return a JSON representation of the resource, recursivly."""
        # Extract a dictonary of primitive properties
        d1 = {
            x: self.__dict__[x]
            for x in self.__dict__
            if not isinstance(self.__dict__[x], RestResource)
            and x not in {"_parent", "parent"}
        }
        while True:
            changed = False
            for k, v in d1.items():
                if k.startswith("__"):
                    del d1[k]
                    changed = True
                    break
                if k.startswith("_"):
                    d1[k[1:]] = v
                    del d1[k]
                    changed = True
                    break
            if not changed:
                break
        # Loop over properties that are RestResource instances (excluding "_parent")
        # and append their properties to the dictionary
        for x in self.__dict__:
            if isinstance(self.__dict__[x], RestResource) and x not in {"_parent"}:
                d2 = self.__dict__[x].__dict__
                del d2["_parent"]
                d1 = {**d1, x: d2}
        # Return a JSON representation of the built dictionary
        return json.dumps(d1, default=str)

    @abc.abstractmethod
    def _fetch_route(self) -> str:
        """Abstract method to be implemented by subclasses, to denote the REST API route for GET requests

        Should return the key from the parent service object route dict, that corresponds to the REST route
        """
        return ""

    @abc.abstractmethod
    def _fetch_args(self) -> list:
        """Abstract method to be implemented by subcasses, to provide values for params on the GET REST route"""
        return []

    def _fetch(self):
        """Fetch an entry from the REST API, using the fetch route denoted by self::_fetch_route"""
        logger.debug("FETCHING ITEM")
        res = self.connection.make_request(
            self.connection.routes[self._fetch_route()][1].format(
                self.endpoint, *self._fetch_args()
            ),
            self._fetch_route(),
            self._fetch_params(),
        )
        return res


class RestResourceList(OrderedDict, RestResource):
    """
    Base class for REST API responses representing a paged list of items.

    Inherits OrderedDict to keep an internal dict of RestResourceItems when iterrating,
    and a separate cache dict to avoid re-fetching individual items.
    """

    def __init__(self, parent, page_size=10):
        logger.debug("Initing RestResourceList object " + str(type(self)))
        super(OrderedDict, self).__init__()
        super(RestResource, self).__init__()
        self._parent = parent
        self._page_size = page_size
        self._page_count = 1
        self._currentPage = 0
        self._cache = OrderedDict()

    def refresh(self):
        """Clear the internal dict, the cache dict, and reset paging"""
        self.clear()
        self._cache.clear()
        self._currentPage = 0
        self._page_count = 1
        return self

    def _add_route(self) -> str:
        """Abstract method to be implemented by subclasses, to denote the REST API route for POST requests

        Should return the key from the parent service object route dict, that corresponds to the REST route
        """
        raise Exception("Operation not supported or not implemented")

    def _add_args(self) -> list:
        """Abstract method to be implemented by subcasses, to provide values for params on the POST REST route"""
        raise Exception("Operation not supported or not implemented")

    @abc.abstractmethod
    def _fetch_route(self) -> str:
        """Abstract method to be implemented by subcasses, to denote the REST API route for GET requests

        Should return the key from the parent service object route dict, that corresponds to the REST route
        """
        return ""

    @abc.abstractmethod
    def _fetch_args(self) -> list:
        """Abstract method to be implemented by subcasses, to provide values for params on the GET REST route"""
        return []

    def _create_child(self, data: dict):
        """Abstract method to be implemented by subclasses, to create the appropriate RestResourceItem instance"""
        raise Exception("Operation not supported or not implemented")

    def _fetch(self):
        """
        Fetch results from the REST API, using the fetch route denoted by self::_fetch_route

        Will fetch up to self::_page_size results each time, keeping track of the current page
        of results in self::_currentPage
        """
        logger.debug("FETCHING LIST")
        res = self.connection.make_request(
            self.connection.routes[self._fetch_route()][1].format(
                self.endpoint, *self._fetch_args()
            ),
            self._fetch_route(),
            # params={"page": self._currentPage + 1},
        )
        # hardcode page_count to 1, as the API does not support paging
        self._page_count = 1
        # Create a RestResourceItem for each JSON object in the response, and add it to the internal dict
        if self.data_root is None:
            data_root = res
        else:
            data_root = res[self.data_root]
        for i in data_root:
            self.update({i[self.id_name]: self._create_child(i)})
        self._currentPage += 1

    def __iter__(self):
        """Iterate over all results, using self::_fetch for each page"""
        self._currentPage = 0
        logger.debug("ITERING")
        while self._currentPage < self._page_count:
            self._fetch()
            logger.debug(
                "PAGE " + str(self._currentPage) + " of " + str(self._page_count)
            )
            if len(self.items()) == 0:
                return None
            else:
                for i, j in enumerate(self.items()):
                    if i >= (self._currentPage - 1) * self._page_size:
                        yield j[1]
        logger.debug("EOD")

    def __getitem__(self, id):
        """
        OrderedDict __getitem__ override.

        Checks if the internal dict has an item with the requested id, from an iteration.
        If not, check the cache. If there's no such item, attempt a fetch request and cache the item
        upon success
        """
        if isinstance(id, int):
            item = list(self)[id]
        else:
            item = super(OrderedDict, self).get(id)
            if item is None:
                item = self._cache.get(id)
                if item is None:
                    item = self._create_child({"__fetch__": id})
                    if item is not None:
                        self._cache.update({getattr(item, self.id_name): item})
        return item

    def get(self, id, default=None):
        """
        OrderedDict get override. Calls __getitem__ but ignores errors and returns default value on failures, instead
        """
        tmp = None
        try:
            tmp = self.__getitem__(id)
        finally:
            return tmp or default

    def add(self, item: Union[RestResourceItem, dict, str]):
        """
        Creates a new subresource under the resource list

        This will issue an API request using the endpoint specified by the _add_route property,
        posting a JSON representation of the given item. If the request succeedes, the appropriate
        RestResourceItem subclassed object will be returned, populated with the response's data
        """
        if self._add_route != "":
            if isinstance(item, RestResourceItem):
                body = str(item)
            elif isinstance(item, dict):
                body = json.dumps(item)
            else:
                body = item
            res = self.connection.make_request(
                self.connection.routes[self._add_route()][1].format(
                    self.endpoint, *self._add_args()
                ),
                self._add_route(),
                body=body,
            )
            ret = self._create_child(res)
            return ret
        else:
            raise Exception("Operation not supported or not implemented")

    def __str__(self):
        return "[{0}]".format(", ".join([str(x) for x in list(self)]))
