from pynetbox.core.response import Record
from pypeeringmanager.models.peering import Routers, InternetExchanges

class Connections(Record):
    internet_exchange_point = InternetExchanges
    router =  Routers
