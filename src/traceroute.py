import time
from dataclasses import dataclass, field

from src.probe import send_probe, ProbeResult
from src.resolver import DNSResolver
from src.config import TracerouteConfig

PROTOCOLS = ["icmp", "udp", "tcp"]


@dataclass
class HopResult:
    ttl: int
    probes: list = field(default_factory=list)

    def get_probes_by_protocol(self, protocol):
        return [p for p in self.probes if p.protocol == protocol]

    def get_responding_addr(self, protocol):
        for p in self.get_probes_by_protocol(protocol):
            if p.addr is not None:
                return p.addr
        return None

    def get_any_responding_addr(self):
        for p in self.probes:
            if p.addr is not None:
                return p.addr
        return None


@dataclass
class TraceResult:
    target: str
    hops: list = field(default_factory=list)
    hostnames: dict = field(default_factory=dict)


def run_traceroute(target, config, progress_callback=None):
    resolver = DNSResolver() if config.resolve_dns else None
    result = TraceResult(target=target)

    for ttl in range(config.first_ttl, config.max_ttl + 1):
        hop = HopResult(ttl=ttl)
        destination_reached = False

        for series_num in range(config.num_series):
            for protocol in PROTOCOLS:
                probe = send_probe(target, ttl, protocol, config)
                hop.probes.append(probe)

                if probe.reached:
                    destination_reached = True

                if config.wait_between > 0:
                    time.sleep(config.wait_between)

        if resolver:
            addr = hop.get_any_responding_addr()
            if addr and addr not in result.hostnames:
                hostname = resolver.resolve(addr)
                if hostname:
                    result.hostnames[addr] = hostname

        result.hops.append(hop)

        if progress_callback:
            progress_callback(target, ttl, config.max_ttl, hop)

        if destination_reached:
            break

    return result
