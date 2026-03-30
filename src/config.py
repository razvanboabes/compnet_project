from dataclasses import dataclass, field


@dataclass
class TracerouteConfig:
    first_ttl: int = 1
    max_ttl: int = 30
    num_series: int = 3
    udp_port: int = 33434
    tcp_port: int = 80
    packet_size: int = 64
    timeout: float = 5.0
    wait_between: float = 0.0
    resolve_dns: bool = True
    targets: list = field(default_factory=list)
    output_file: str = "results.txt"
