# Multi-Protocol Traceroute with Topology Visualizer

A Python-based traceroute tool that probes network paths using ICMP, UDP, and TCP protocols simultaneously, and visualizes the discovered topology in an interactive Tkinter GUI.

## Project Structure

```
comp-net-tengis/
├── src/
│   ├── __init__.py        - Package marker
│   ├── main.py            - CLI entry point and argument parsing
│   ├── config.py          - Configuration dataclass with default values
│   ├── probe.py           - Packet crafting and sending using Scapy (UDP/TCP/ICMP)
│   ├── resolver.py        - DNS reverse lookup with result caching
│   ├── traceroute.py      - Core traceroute engine orchestrating probes per hop
│   ├── output.py          - Text file formatter and writer for raw results
│   ├── topology.py        - Graph builder merging trace results into a tree
│   └── visualizer.py      - Tkinter-based interactive topology visualization
├── targets/
│   └── example.txt        - Example target IP list
├── requirements.txt       - Python dependencies
├── README.md              - This file
└── HOWTO.md               - Installation and usage instructions
```

## Module Descriptions

### main.py
Entry point. Parses command-line arguments, reads the target IP file, runs traceroute for each target sequentially, writes results to a text file, and launches the GUI visualizer.

### config.py
Defines `TracerouteConfig`, a dataclass holding all configurable parameters (TTL range, port numbers, packet size, timeouts, etc.) with standard traceroute defaults.

### probe.py
Uses Scapy to craft and send individual probe packets. Supports three protocols:
- **ICMP** - Echo Request (type 8)
- **UDP** - Datagram to configurable destination port
- **TCP** - SYN packet to configurable destination port

Returns a `ProbeResult` with the responding IP, round-trip time, and whether the destination was reached.

### resolver.py
Performs reverse DNS lookups via `socket.gethostbyaddr()` with an in-memory cache to avoid redundant queries.

### traceroute.py
Orchestrates the traceroute for a single target. For each TTL value, sends the configured number of series (each containing one ICMP, one UDP, and one TCP probe). Stops when the destination is reached or max TTL is exceeded.

### output.py
Formats trace results into a readable text format grouped by hop and protocol, showing RTTs and hostnames. Writes all results to a single output file.

### topology.py
Builds a directed graph from multiple trace results. Nodes represent routers/endpoints identified by IP. Edges carry per-protocol statistics (RTT, loss rate, throughput approximation). Computes hierarchical layers for visualization layout.

### visualizer.py
Tkinter desktop application with:
- Canvas-based topology drawing with hierarchical layout
- Color-coded edges per protocol (red=ICMP, blue=UDP, green=TCP)
- Edge thickness proportional to throughput (packet_size / RTT)
- Dashed lines indicating packet loss
- Click nodes/edges to view details in a side panel
- Mouse wheel zoom, click-drag pan
- Protocol legend and reset view button
