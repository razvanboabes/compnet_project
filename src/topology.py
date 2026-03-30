import socket
from dataclasses import dataclass, field

from src.traceroute import TraceResult, PROTOCOLS


@dataclass
class TopoNode:
    ip: str
    hostname: str = None
    is_source: bool = False
    is_target: bool = False
    targets: set = field(default_factory=set)


@dataclass
class TopoEdge:
    src_ip: str
    dst_ip: str
    protocol: str
    rtt_values: list = field(default_factory=list)
    loss_count: int = 0
    total_probes: int = 0
    packet_size: int = 64

    @property
    def avg_rtt(self):
        valid = [r for r in self.rtt_values if r is not None]
        return sum(valid) / len(valid) if valid else None

    @property
    def loss_rate(self):
        return self.loss_count / self.total_probes if self.total_probes > 0 else 0.0

    @property
    def throughput(self):
        if self.avg_rtt and self.avg_rtt > 0:
            return (self.packet_size * 8) / (self.avg_rtt / 1000)
        return None


class TopologyGraph:
    def __init__(self):
        self.nodes = {}
        self.edges = {}
        self.source_ip = None

    def _get_source_ip(self):
        if self.source_ip is None:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                self.source_ip = s.getsockname()[0]
                s.close()
            except OSError:
                self.source_ip = "127.0.0.1"
            self._ensure_node(self.source_ip, is_source=True)
            self.nodes[self.source_ip].hostname = socket.gethostname()
        return self.source_ip

    def _ensure_node(self, ip, hostname=None, is_source=False, is_target=False):
        if ip not in self.nodes:
            self.nodes[ip] = TopoNode(ip=ip, hostname=hostname,
                                       is_source=is_source, is_target=is_target)
        node = self.nodes[ip]
        if hostname and not node.hostname:
            node.hostname = hostname
        if is_target:
            node.is_target = True
        if is_source:
            node.is_source = True
        return node

    def _ensure_edge(self, src_ip, dst_ip, protocol, packet_size):
        key = (src_ip, dst_ip, protocol)
        if key not in self.edges:
            self.edges[key] = TopoEdge(
                src_ip=src_ip, dst_ip=dst_ip,
                protocol=protocol, packet_size=packet_size
            )
        return self.edges[key]

    def add_trace_result(self, result):
        source = self._get_source_ip()

        for protocol in PROTOCOLS:
            prev_ip = source
            for hop in result.hops:
                addr = hop.get_responding_addr(protocol)
                if addr is None:
                    continue

                hostname = result.hostnames.get(addr)
                is_target = (addr == result.target)
                node = self._ensure_node(addr, hostname=hostname, is_target=is_target)
                node.targets.add(result.target)

                probes = hop.get_probes_by_protocol(protocol)
                edge = self._ensure_edge(prev_ip, addr, protocol, probes[0].packet_size if probes else 64)
                for p in probes:
                    edge.total_probes += 1
                    if p.rtt is not None:
                        edge.rtt_values.append(p.rtt)
                    else:
                        edge.loss_count += 1

                prev_ip = addr

    def get_layers(self):
        if not self.source_ip:
            return {}

        layers = {}
        visited = set()
        queue = [(self.source_ip, 0)]
        visited.add(self.source_ip)

        children_map = {}
        for (src, dst, proto) in self.edges:
            children_map.setdefault(src, set()).add(dst)

        while queue:
            ip, depth = queue.pop(0)
            layers.setdefault(depth, []).append(ip)
            for child in children_map.get(ip, []):
                if child not in visited:
                    visited.add(child)
                    queue.append((child, depth + 1))

        return layers
