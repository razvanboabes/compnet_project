from src.traceroute import TraceResult, PROTOCOLS


def format_rtt(rtt):
    if rtt is None:
        return "*"
    return f"{rtt:.3f} ms"


def format_trace_result(result):
    lines = []
    lines.append(f"Traceroute to {result.target}, {len(result.hops)} hops discovered")
    lines.append("=" * 80)
    lines.append("")

    for hop in result.hops:
        lines.append(f"Hop {hop.ttl}:")
        for protocol in PROTOCOLS:
            probes = hop.get_probes_by_protocol(protocol)
            addr = hop.get_responding_addr(protocol)
            if addr is None:
                addr_str = "*"
                name_str = ""
            else:
                hostname = result.hostnames.get(addr)
                addr_str = addr
                name_str = f"  ({hostname})" if hostname else ""

            rtts = "  ".join(format_rtt(p.rtt) for p in probes)
            lines.append(f"  {protocol.upper():<6} {addr_str:<16}{name_str:<30} {rtts}")
        lines.append("")

    return "\n".join(lines)


def write_results(results, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        for i, result in enumerate(results):
            if i > 0:
                f.write("\n" + "=" * 80 + "\n\n")
            f.write(format_trace_result(result))
