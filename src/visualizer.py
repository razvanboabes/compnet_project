import tkinter as tk
from tkinter import ttk
import math

from src.topology import TopologyGraph

PROTOCOL_COLORS_DEFAULT = {
    "icmp": "#e74c3c",
    "udp": "#3498db",
    "tcp": "#2ecc71",
}

# Okabe-Ito palette: distinguishable for deuteranopia, protanopia, and tritanopia.
PROTOCOL_COLORS_CB = {
    "icmp": "#D55E00",  # vermillion
    "udp":  "#0072B2",  # blue
    "tcp":  "#F0E442",  # yellow
}

NODE_RADIUS = 20
LAYER_SPACING_Y = 120
NODE_SPACING_X = 180
EDGE_OFFSET = 6


class TopologyVisualizer(tk.Tk):
    def __init__(self, topology):
        super().__init__()
        self.topology = topology
        self.title("Traceroute Topology Visualizer")
        self.geometry("1200x800")
        self.configure(bg="#2b2b2b")

        self.node_positions = {}
        self.canvas_items = {}
        self.tooltip = None
        self.drag_data = {"x": 0, "y": 0}
        self.scale_factor = 1.0
        self.colorblind_mode = False
        self.protocol_colors = PROTOCOL_COLORS_DEFAULT

        self._build_ui()
        self._compute_layout()
        self._draw_topology()

    def _build_ui(self):
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(
            main_frame, bg="#1e1e1e", highlightthickness=0
        )
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.detail_panel = tk.Frame(main_frame, bg="#2b2b2b", width=140)
        self.detail_panel.pack(side=tk.RIGHT, fill=tk.Y)
        self.detail_panel.pack_propagate(False)

        controls = tk.Frame(self.detail_panel, bg="#2b2b2b")
        controls.pack(fill=tk.X, padx=10, pady=10)

        tk.Button(
            controls, text="Reset View", command=self._reset_view,
            bg="#444444", fg="#ffffff", font=("Consolas", 10),
            relief=tk.FLAT, padx=10, pady=4
        ).pack(fill=tk.X, pady=(0, 6))

        self.cb_button = tk.Button(
            controls, text="Colorblind: Off",
            command=self._toggle_colorblind,
            bg="#444444", fg="#ffffff", font=("Consolas", 10),
            relief=tk.FLAT, padx=10, pady=4
        )
        self.cb_button.pack(fill=tk.X)

        self.canvas.bind("<ButtonPress-1>", self._on_drag_start)
        self.canvas.bind("<B1-Motion>", self._on_drag_move)
        self.canvas.bind("<MouseWheel>", self._on_scroll)
        self.canvas.bind("<Motion>", self._on_hover)

    def _compute_layout(self):
        layers = self.topology.get_layers()
        if not layers:
            return

        max_layer_width = max(len(nodes) for nodes in layers.values()) if layers else 1
        canvas_center_x = max(600, max_layer_width * NODE_SPACING_X // 2 + 100)

        children_map = {}
        for (src, dst, proto) in self.topology.edges:
            children_map.setdefault(src, set()).add(dst)

        for depth in sorted(layers.keys()):
            nodes = layers[depth]
            if depth > 0:
                def parent_avg(node_ip):
                    parents = []
                    for (src, dst, proto) in self.topology.edges:
                        if dst == node_ip and src in self.node_positions:
                            parents.append(self.node_positions[src][0])
                    return sum(parents) / len(parents) if parents else 0
                nodes.sort(key=parent_avg)

            n = len(nodes)
            total_width = (n - 1) * NODE_SPACING_X
            start_x = canvas_center_x - total_width / 2

            y = 60 + depth * LAYER_SPACING_Y
            for i, ip in enumerate(nodes):
                x = start_x + i * NODE_SPACING_X
                self.node_positions[ip] = (x, y)

    def _draw_topology(self):
        self.canvas.delete("all")
        self.canvas_items = {}

        drawn_edges = set()
        for (src_ip, dst_ip, protocol), edge in self.topology.edges.items():
            if src_ip not in self.node_positions or dst_ip not in self.node_positions:
                continue

            x1, y1 = self.node_positions[src_ip]
            x2, y2 = self.node_positions[dst_ip]

            proto_list = ["icmp", "udp", "tcp"]
            idx = proto_list.index(protocol) if protocol in proto_list else 0
            offset = (idx - 1) * EDGE_OFFSET

            dx = x2 - x1
            dy = y2 - y1
            length = math.sqrt(dx * dx + dy * dy)
            if length == 0:
                continue
            nx_val = -dy / length
            ny_val = dx / length

            lx1 = x1 + nx_val * offset
            ly1 = y1 + ny_val * offset
            lx2 = x2 + nx_val * offset
            ly2 = y2 + ny_val * offset

            color = self.protocol_colors.get(protocol, "#888888")
            throughput = edge.throughput
            width = 1.5
            if throughput is not None:
                width = max(1, min(6, throughput / 50000))

            dash = ()
            if edge.loss_rate > 0.5:
                dash = (4, 4)
            elif edge.loss_rate > 0:
                dash = (8, 3)

            line = self.canvas.create_line(
                lx1, ly1, lx2, ly2,
                fill=color, width=width, dash=dash,
                tags=("edge", f"edge_{src_ip}_{dst_ip}_{protocol}")
            )
            self.canvas_items[line] = {
                "type": "edge", "edge": edge, "protocol": protocol
            }

        for ip, (x, y) in self.node_positions.items():
            node = self.topology.nodes.get(ip)
            if node is None:
                continue

            fill = "#3a3a3a"
            outline = "#888888"
            if node.is_source:
                fill = "#1a5276"
                outline = "#5dade2"
            elif node.is_target:
                fill = "#1e8449"
                outline = "#58d68d"

            oval = self.canvas.create_oval(
                x - NODE_RADIUS, y - NODE_RADIUS,
                x + NODE_RADIUS, y + NODE_RADIUS,
                fill=fill, outline=outline, width=2,
                tags=("node", f"node_{ip}")
            )
            self.canvas_items[oval] = {"type": "node", "ip": ip, "node": node}

            label = node.hostname if node.hostname else ip
            if len(label) > 20:
                label = label[:17] + "..."
            self.canvas.create_text(
                x, y + NODE_RADIUS + 12,
                text=label, fill="#cccccc",
                font=("Consolas", 8), tags=("label",)
            )
            self.canvas.create_text(
                x, y,
                text=ip.split(".")[-1], fill="#ffffff",
                font=("Consolas", 8, "bold"), tags=("label",)
            )

    def _toggle_colorblind(self):
        self.colorblind_mode = not self.colorblind_mode
        if self.colorblind_mode:
            self.protocol_colors = PROTOCOL_COLORS_CB
            self.cb_button.config(text="Colorblind: On")
        else:
            self.protocol_colors = PROTOCOL_COLORS_DEFAULT
            self.cb_button.config(text="Colorblind: Off")
        self._draw_topology()

    def _on_drag_start(self, event):
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def _on_drag_move(self, event):
        dx = event.x - self.drag_data["x"]
        dy = event.y - self.drag_data["y"]
        self.canvas.move("all", dx, dy)
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def _on_scroll(self, event):
        factor = 1.1 if event.delta > 0 else 0.9
        self.scale_factor *= factor
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        self.canvas.scale("all", x, y, factor, factor)

    def _on_hover(self, event):
        item = self.canvas.find_closest(event.x, event.y)
        if self.tooltip:
            self.canvas.delete(self.tooltip)
            self.tooltip = None

        if not item or item[0] not in self.canvas_items:
            return

        info = self.canvas_items[item[0]]
        text = ""
        if info["type"] == "node":
            node = info["node"]
            text = f"{node.ip}"
            if node.hostname:
                text += f" ({node.hostname})"
        elif info["type"] == "edge":
            edge = info["edge"]
            rtt_str = f"{edge.avg_rtt:.2f} ms" if edge.avg_rtt else "N/A"
            text = f"{info['protocol'].upper()} RTT: {rtt_str}"

        if text:
            self.tooltip = self.canvas.create_text(
                event.x + 15, event.y - 10,
                text=text, fill="#ffff00", anchor=tk.W,
                font=("Consolas", 9), tags=("tooltip",)
            )

    def _reset_view(self):
        self.scale_factor = 1.0
        self.canvas.delete("all")
        self._draw_topology()


def launch_visualizer(topology):
    app = TopologyVisualizer(topology)
    app.mainloop()