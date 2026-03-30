import os
import time
from dataclasses import dataclass

from scapy.all import IP, UDP, TCP, ICMP, Raw, sr1, RandShort, conf

conf.verb = 0


@dataclass
class ProbeResult:
    protocol: str
    ttl: int
    rtt: float
    addr: str
    reached: bool
    packet_size: int


def _build_packet(target, ttl, protocol, port_udp, port_tcp, payload_size):
    ip_layer = IP(dst=target, ttl=ttl)
    pad = Raw(b"\x00" * max(0, payload_size - 28))

    if protocol == "udp":
        return ip_layer / UDP(dport=port_udp, sport=int(RandShort())) / pad
    elif protocol == "tcp":
        return ip_layer / TCP(dport=port_tcp, sport=int(RandShort()), flags="S") / pad
    elif protocol == "icmp":
        return ip_layer / ICMP(type=8, id=os.getpid() & 0xFFFF, seq=ttl) / pad
    raise ValueError(f"Unknown protocol: {protocol}")


def _is_destination_reached(reply, protocol):
    if reply is None:
        return False
    if protocol == "icmp":
        return reply.haslayer(ICMP) and reply[ICMP].type == 0
    if protocol == "udp":
        return reply.haslayer(ICMP) and reply[ICMP].type == 3
    if protocol == "tcp":
        return reply.haslayer(TCP)
    return False


def send_probe(target, ttl, protocol, config):
    pkt = _build_packet(
        target, ttl, protocol,
        config.udp_port, config.tcp_port, config.packet_size
    )
    start = time.perf_counter()
    reply = sr1(pkt, timeout=config.timeout, verbose=0)
    rtt = (time.perf_counter() - start) * 1000

    if reply is None:
        return ProbeResult(
            protocol=protocol, ttl=ttl, rtt=None,
            addr=None, reached=False, packet_size=config.packet_size
        )

    return ProbeResult(
        protocol=protocol, ttl=ttl, rtt=round(rtt, 3),
        addr=reply.src, reached=_is_destination_reached(reply, protocol),
        packet_size=config.packet_size
    )
