import requests, sys

from pynetbox.core.api import Api as PyNetboxApi
from pypeeringmanager.core.app import App

class Api(PyNetboxApi):
    """The API object is the point of entry to pypeeringmanager.
    After instantiating the Api() with the appropriate named arguments
    you can specify which app and endpoint you wish to interact with.
    There is only one app available, peering.
    Calling any of these attributes will return
    :py:class:`.App` which exposes endpoints as attributes.
    **Additional Attributes**:
        *  **http_session(requests.Session)**:
                Override the default session with your own. This is used to control
                a number of HTTP behaviors such as SSL verification, custom headers,
                retires, and timeouts.
                See `custom sessions <advanced.html#custom-sessions>`__ for more info.
    :param str url: The base URL to the instance of Peering-Manager you
        wish to connect to.
    :param str token: Your Peering-Manager token.
    :param bool,optional threading: Set to True to use threading in ``.all()``
        and ``.filter()`` requests.
    :raises AttributeError: If app doesn't exist.
    :Examples:
    >>> import pypeeringmanager
    >>> pm = pypeeringmanager.api(
    ...     'http://localhost:8000',
    ...     token='d6f4e314a5b5fefd164995169f28ae32d987704f'
    ... )
    >>> pm.peering.internet_exchange_peering_sessions.all()
    """

    def __init__(
        self, url, token=None, threading=False,
    ):
        base_url = "{}/api".format(url if url[-1] != "/" else url[:-1])
        self.token = token
        self.private_key = None
        self.private_key_file = None
        self.base_url = base_url
        self.session_key = None
        self.http_session = requests.Session()
        if threading and sys.version_info.major == 2:
            raise NotImplementedError(
                "Threaded pypeeringmanager calls not supported in Python 2"
            )
        self.threading = threading

        self.peering = App(self, "peering")
        self.net = App(self, "net")
        self.extras = App(self, "extras")

    @property
    def version(self):
       raise NotImplementedError

    def openapi(self):
       raise NotImplementedError
