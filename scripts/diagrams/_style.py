"""
Shared design system for all Quantum Grid Intelligence diagrams.
Professional palette · transparent background · light/dark compatible.
Four domain families (classical=blue, quantum=violet, execution=teal,
grid=green/amber/gray) plus one reserved alarm color (red, edges only).
"""

# ── Background ─────────────────────────────────────────────────────────────
BGCOLOR = "transparent"

# ── Typography ─────────────────────────────────────────────────────────────
FONT   = "Helvetica"
T_DARK = "#1E2A38"   # slate-900 — primary text
T_MED  = "#5B6B7C"   # slate-600 — secondary / edge labels
T_LITE = "#94A3B3"   # slate-400 — minor annotations

# ── Node fills — light "card" look, readable on any background ─────────────
F_DEFAULT    = "#F8FAFC"   # slate-50   — general / neutral nodes
F_CLASSICAL  = "#E7F0FA"   # blue-50    — classical baselines / data
F_QUANTUM    = "#EFE8FB"   # violet-50  — QAOA / quantum circuit
F_EXEC       = "#E3F6F2"   # teal-50    — Guppy / HUGR / Nexus execution
F_HYDRO      = "#DCEFE3"   # green-50   — hydroelectric (renewable)
F_GEOTHERMAL = "#C9E6D3"   # green-100  — geothermal (renewable, deeper shade)
F_THERMAL    = "#FBEBD9"   # amber-50   — thermal (non-renewable)
F_SUBSTATION = "#EDEFF2"   # gray-100   — substation (infrastructure)
F_LOAD       = "#DCE7FA"   # blue-50    — load center (demand side)
F_SUCCESS    = "#E4F6E9"   # green-50   — success / terminal / optimal result

# ── Borders ──────────────────────────────────────────────────────────────────
B_DEFAULT    = "#8A93A0"   # slate-400
B_CLASSICAL  = "#2E6FA7"   # blue-600
B_QUANTUM    = "#6C3FC6"   # violet-600
B_EXEC       = "#1A9C8A"   # teal-600
B_GRID       = "#3B7A57"   # green-700  — shared border for all grid-domain nodes
B_SUBSTATION = "#8A93A0"   # muted slate — substation isn't generation
B_SUCCESS    = "#2E9E52"   # green-600

# ── Edges ────────────────────────────────────────────────────────────────────
E_DEFAULT   = "#B8C2CC"   # slate-300
E_CLASSICAL = "#2E6FA7"   # blue-600
E_QUANTUM   = "#6C3FC6"   # violet-600
E_EXEC      = "#1A9C8A"   # teal-600
E_FAULT     = "#D6455A"   # red — reserved for cut edges / fault highlighting only


def render(g, name: str, out: str) -> None:
    """Render graph to both SVG and PNG."""
    from pathlib import Path
    Path(out).mkdir(parents=True, exist_ok=True)
    svg = g.pipe(format="svg")
    png = g.pipe(format="png")
    Path(f"{out}/{name}.svg").write_bytes(svg)
    Path(f"{out}/{name}.png").write_bytes(png)
    print(f"  ✓ {name}  →  {out}  (.svg + .png)")


def base_graph_attr(**extra):
    return {
        "bgcolor": BGCOLOR,
        "fontname": FONT,
        "fontsize": "13",
        "fontcolor": T_DARK,
        "labelloc": "t",
        "labeljust": "l",
        "pad": "0.6",
        "nodesep": "0.45",
        "ranksep": "0.75",
        "dpi": "200",
        **extra,
    }


def base_node_attr(**extra):
    return {
        "shape": "box",
        "style": "filled,rounded",
        "fillcolor": F_DEFAULT,
        "color": B_DEFAULT,
        "fontname": FONT,
        "fontsize": "11",
        "fontcolor": T_DARK,
        "margin": "0.2,0.12",
        "penwidth": "1.6",
        **extra,
    }


def base_edge_attr(**extra):
    return {
        "color": E_DEFAULT,
        "fontname": FONT,
        "fontsize": "10",
        "fontcolor": T_MED,
        "arrowsize": "0.8",
        "penwidth": "1.3",
        **extra,
    }


def _escape(text: str) -> str:
    """Escape special HTML characters in label text content."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def hl(title: str, subtitle: str = "", subtitle2: str = "") -> str:
    """HTML label: bold title + optional smaller subtitle lines. Keeps node text short."""
    s = f"<B>{_escape(title)}</B>"
    if subtitle:
        s += f'<BR/><FONT POINT-SIZE="9" COLOR="{T_MED}">{_escape(subtitle)}</FONT>'
    if subtitle2:
        s += f'<BR/><FONT POINT-SIZE="9" COLOR="{T_LITE}">{_escape(subtitle2)}</FONT>'
    return f"<{s}>"


def cluster_attr(label: str, color: str, subtitle: str = "") -> dict:
    lbl = f"<<B>{_escape(label)}</B>"
    if subtitle:
        lbl += f'<BR/><FONT POINT-SIZE="9" COLOR="{T_MED}">{_escape(subtitle)}</FONT>'
    lbl += ">"
    return {
        "label": lbl,
        "style": "rounded",
        "color": color,
        "fontcolor": color,
        "fontname": FONT,
        "fontsize": "12",
        "penwidth": "2.2",
        "margin": "16",
    }
