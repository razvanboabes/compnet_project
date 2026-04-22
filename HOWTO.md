# How to Install and Run

## Instructions for Windows:
### Prerequisites

- **Windows 10/11**
- **Python 3.13.2** (or compatible 3.x version)
- **Npcap** (required by Scapy for packet capture on Windows)
- **Administrator privileges** (required for sending raw packets)

### Step 1: Install Npcap

Download and install Npcap from https://npcap.com/

During installation, check the option **"Install Npcap in WinPcap API-compatible Mode"**.

### Step 2: Install Python Dependencies

Open a terminal and navigate to the project directory:

```
cd compnet_project
pip install -r requirements.txt
```

### Step 3: Prepare Target List

Create a text file with one IP address per line, or use the provided example:

```
targets/example.txt
```

Note that lines starting with `#` are treated like comments and ignored. CSV files are also supported (the first column is used as the IP address).

### Step 4: Run the Program

Open a terminal **as Administrator** (right-click > Run as administrator) and run:

```
python -m src.main targets/example.txt
```

# See Instructions shared by Mac and Windows OS for continued instructions

## Instructions for Mac:
### Prerequisites

- **macOS 15 or later**
- **Python 3.13.2** (or compatible 3.x version)
- **Tkinter** (required for the visualizer, usually included in the universal python installer)
- **Sudoer privileges** (required for sending raw packets)


### Step 1: Install Tkinter
Open a terminal and run:

 ```brew install python-tk@3.14```

### Step 2: Install Python Dependencies:

Open a terminal and navigate to the project directory:

```
cd compnet_project
pip install -r requirements.txt
```

### Step 3: Prepare Target List

Create a text file with one IP address per line, or use the provided example:

```
targets/example.txt
```

Note that lines starting with `#` are treated like comments and ignored. CSV files are also supported (the first column is used as the IP address).

### Step 4: Run the program

```sudo python -m src.main targets/example.txt  ```

# See Instructions shared by Mac and Windows OS for continued instructions

## Instructions shared by Mac & Windows
### Command-Line Options

| Option | Description | Default |
|---|---|---|
| `targets_file` | Path to target IP file (required) | - |
| `-f`, `--first-ttl` | Starting TTL value | 1 |
| `-m`, `--max-ttl` | Maximum TTL value | 30 |
| `-s`, `--series` | Number of probe series per hop | 3 |
| `-p`, `--udp-port` | UDP destination port | 33434 |
| `-P`, `--tcp-port` | TCP destination port | 80 |
| `-S`, `--packet-size` | Probe packet size in bytes | 64 |
| `-w`, `--timeout` | Timeout per probe (seconds) | 5.0 |
| `-z`, `--wait` | Wait between consecutive probes (seconds) | 0.0 |
| `-n`, `--no-dns` | Disable DNS resolution | Off (DNS enabled) |
| `-o`, `--output` | Output text file path | results.txt |
| `--no-gui` | Skip GUI, only write text results | Off (GUI enabled) |

## Examples

Basic usage with defaults:
```
python -m src.main targets/example.txt
```

Custom TTL range and 5 series per hop:
```
python -m src.main targets/example.txt -f 1 -m 20 -s 5
```

Large packet size, custom ports, no DNS:
```
python -m src.main targets/example.txt -S 128 -p 53 -P 443 -n
```

Text output only (no GUI):
```
python -m src.main targets/example.txt --no-gui -o my_results.txt
```

Add wait time between probes:
```
python -m src.main targets/example.txt -z 0.1
```

## Output

### Text File
Results are written to `results.txt` (or the path specified with `-o`). Each target gets a section showing per-hop, per-protocol results including IP addresses, hostnames, and RTT measurements.

### GUI Visualizer
An interactive Tkinter window opens showing the discovered topology:
- **Left-click** a node or edge to see details in the right panel
- **Scroll wheel** to zoom in/out
- **Click and drag** to pan the view
- **Reset View** button to restore original layout
- Edge colors indicate protocol: red (ICMP), blue (UDP), green (TCP)
- Dashed edges indicate packet loss on that link

## Troubleshooting

**"This program requires administrator privileges"**
Right-click your terminal and select "Run as administrator".

**"No module named 'scapy'"**
Run `pip install -r requirements.txt`.

**"ModuleNotFoundError: No module named '_tkinter'"**
Run `brew install python-tk@3.14`

**No responses from any hop**
If you're on windows, ensure Npcap is installed with WinPcap compatibility mode. Some firewalls may block raw packet sending.

**All hops show asterisks (\*)**
The target or intermediate routers may be filtering probe packets. Try different ports or protocols. If you're on mac, note that macOS can silently block some packets, especially ICMP or uncommon UDP ports.
