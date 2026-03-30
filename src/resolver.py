import socket


class DNSResolver:
    def __init__(self):
        self._cache = {}

    def resolve(self, ip_address):
        if ip_address in self._cache:
            return self._cache[ip_address]
        try:
            hostname = socket.gethostbyaddr(ip_address)[0]
        except (socket.herror, socket.gaierror, OSError):
            hostname = None
        self._cache[ip_address] = hostname
        return hostname
