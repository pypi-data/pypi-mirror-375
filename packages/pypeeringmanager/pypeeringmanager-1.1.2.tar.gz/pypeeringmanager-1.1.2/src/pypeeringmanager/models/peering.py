from pynetbox.core.response import Record


class Routers(Record):
    pass


class RoutingPolicies(Record):
    pass


class Communities(Record):
    pass


class AutonomousSystems(Record):
    import_routing_policies = RoutingPolicies
    export_routing_policies = RoutingPolicies


class BGPGroups(Record):
    import_routing_policies = RoutingPolicies
    export_routing_policies = RoutingPolicies
    communities = Communities


class InternetExchanges(Record):
    import_routing_policies = RoutingPolicies
    export_routing_policies = RoutingPolicies
    communities = Communities


class DirectPeeringSessions(Record):
    autonomous_system = AutonomousSystems
    bgp_group = BGPGroups
    import_routing_policies = RoutingPolicies
    export_routing_policies = RoutingPolicies
    router =  Routers

    def __str__(self):
        return self.ip_address


class InternetExchangePeeringSessions(Record):
    autonomous_system = AutonomousSystems
    internet_exchange = InternetExchanges

    def __str__(self):
        return self.ip_address
