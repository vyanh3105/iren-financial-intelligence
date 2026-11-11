"""One consistent chart style for every notebook.

Call `set_style()` once at the top of a notebook. Colours follow a fixed
order: the same asset always gets the same colour in every chart.
"""
import matplotlib.pyplot as plt

# Colour-blind-checked categorical order (blue, orange, aqua, yellow, magenta, green, violet, red)
PALETTE = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
INK = "#0b0b0b"
INK_2 = "#52514e"
GRID = "#e4e3df"

# Fixed colour per asset, so IREN is always blue, BTC always orange, etc.
ASSET_COLORS = {"IREN": PALETTE[0], "BTC-USD": PALETTE[1], "QQQ": PALETTE[2],
                "AI peers": PALETTE[3], "Miners": PALETTE[4]}


def set_style():
    plt.rcParams.update({
        "figure.figsize": (10, 4.5),
        "figure.dpi": 110,
        "axes.prop_cycle": plt.cycler(color=PALETTE),
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.edgecolor": INK_2,
        "axes.labelcolor": INK_2,
        "axes.titlesize": 13,
        "axes.titleweight": "semibold",
        "axes.titlelocation": "left",
        "axes.grid": True,
        "grid.color": GRID,
        "grid.linewidth": 0.8,
        "xtick.color": INK_2,
        "ytick.color": INK_2,
        "lines.linewidth": 1.6,
        "legend.frameon": False,
        "savefig.bbox": "tight",
    })


def save(fig, name: str):
    """Save into reports/figures/ so the README can show it."""
    from .config import FIGURES
    FIGURES.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURES / f"{name}.png", dpi=150)
