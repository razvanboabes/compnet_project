# Multi-Protocol Traceroute with Topology Visualizer

A Python-based traceroute tool that probes network paths using ICMP, UDP, and TCP protocols simultaneously, and visualizes the discovered topology in an interactive Tkinter GUI.

## Project Structure

```
compnet_project/
├── src/
│   ├── __init__.py
│   ├── main.py            - Program entry point and CLI
│   ├── config.py          - Provides default values for configuration class
│   ├── probe.py           - Packet crafting and sending using Scapy (UDP/TCP/ICMP)
│   ├── resolver.py        - DNS reverse lookup
│   ├── traceroute.py      - Traces probe packets for every hop
│   ├── output.py          - Text file formatter 
│   ├── topology.py        - Graphs the trace results into a tree
│   └── visualizer.py      - Visualization of network topology
├── targets/
│   └── example.txt        - Example target IP list
├── requirements.txt       - Python dependencies
├── README.md              - Explains program structure
├── Makefile               - Installation for macOS
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
