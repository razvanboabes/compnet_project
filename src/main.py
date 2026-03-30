import argparse
import ctypes
import os
import sys

from src.config import TracerouteConfig
from src.traceroute import run_traceroute
from src.output import write_results, format_trace_result
from src.topology import TopologyGraph
from src.visualizer import launch_visualizer


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except AttributeError:
        return False


def parse_targets(filepath):
    targets = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                targets.append(line.split(",")[0].strip())
    return targets


def build_parser():
    parser = argparse.ArgumentParser(
        prog="traceroute",
        description="Multi-protocol traceroute with topology visualization"
    )
    parser.add_argument(
        "targets_file",
        help="Path to file containing target IP addresses (txt or csv)"
    )
    parser.add_argument(
        "-f", "--first-ttl", type=int, default=1,
        help="Initial TTL value (default: 1)"
    )
    parser.add_argument(
        "-m", "--max-ttl", type=int, default=30,
        help="Maximum TTL value (default: 30)"
    )
    parser.add_argument(
        "-s", "--series", type=int, default=3,
        help="Number of probe series per hop (default: 3)"
    )
    parser.add_argument(
        "-p", "--udp-port", type=int, default=33434,
        help="UDP destination port (default: 33434)"
    )
    parser.add_argument(
        "-P", "--tcp-port", type=int, default=80,
        help="TCP destination port (default: 80)"
    )
    parser.add_argument(
        "-S", "--packet-size", type=int, default=64,
        help="Packet size in bytes (default: 64)"
    )
    parser.add_argument(
        "-w", "--timeout", type=float, default=5.0,
        help="Timeout per probe in seconds (default: 5.0)"
    )
    parser.add_argument(
        "-z", "--wait", type=float, default=0.0,
        help="Wait time between probes in seconds (default: 0.0)"
    )
    parser.add_argument(
        "-n", "--no-dns", action="store_true",
        help="Disable DNS resolution"
    )
    parser.add_argument(
        "-o", "--output", type=str, default="results.txt",
        help="Output file path (default: results.txt)"
    )
    parser.add_argument(
        "--no-gui", action="store_true",
        help="Skip the GUI visualization"
    )
    return parser


def progress_printer(target, ttl, max_ttl, hop):
    addr = hop.get_any_responding_addr()
    addr_str = addr if addr else "*"
    print(f"  [{ttl}/{max_ttl}] {addr_str}")


def main():
    if not is_admin():
        print("ERROR: This program requires administrator privileges.")
        print("Please run as Administrator.")
        sys.exit(1)

    parser = build_parser()
    args = parser.parse_args()

    if not os.path.isfile(args.targets_file):
        print(f"ERROR: File not found: {args.targets_file}")
        sys.exit(1)

    targets = parse_targets(args.targets_file)
    if not targets:
        print("ERROR: No valid targets found in the input file.")
        sys.exit(1)

    config = TracerouteConfig(
        first_ttl=args.first_ttl,
        max_ttl=args.max_ttl,
        num_series=args.series,
        udp_port=args.udp_port,
        tcp_port=args.tcp_port,
        packet_size=args.packet_size,
        timeout=args.timeout,
        wait_between=args.wait,
        resolve_dns=not args.no_dns,
        targets=targets,
        output_file=args.output,
    )

    print(f"Traceroute starting with {len(targets)} target(s)")
    print(f"TTL range: {config.first_ttl}-{config.max_ttl}, "
          f"Series: {config.num_series}, "
          f"Packet size: {config.packet_size}B, "
          f"Timeout: {config.timeout}s")
    print("-" * 60)

    results = []
    topology = TopologyGraph()

    for i, target in enumerate(targets, 1):
        print(f"\n[{i}/{len(targets)}] Tracing route to {target}...")
        result = run_traceroute(target, config, progress_callback=progress_printer)
        results.append(result)
        topology.add_trace_result(result)
        print(f"  Completed: {len(result.hops)} hops discovered")

    print(f"\n{'=' * 60}")
    print(f"Writing results to {config.output_file}...")
    write_results(results, config.output_file)
    print("Done.")

    if not args.no_gui:
        print("Launching topology visualizer...")
        launch_visualizer(topology)


if __name__ == "__main__":
    main()
