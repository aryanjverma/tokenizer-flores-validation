"""SuperBPE (original) vs supergigatoken — train + encode throughput diagram."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

OUT_DIR = Path(__file__).resolve().parent
PNG = OUT_DIR / "superbpe_vs_supergigatoken_throughput.png"
PPTX = OUT_DIR / "superbpe_vs_supergigatoken_throughput.pptx"

# Numbers from benchmarks/superbpe/{results_parity,results_throughput}.json
REF_TRAIN_S = 223.44
OURS_TRAIN_S = 28.069
TRAIN_SPEEDUP = 7.96

# Encode SuperBPE 50k: HF path (what original stack uses) vs gigatoken Superword
HF_MB_S = 6.27
SGT_MB_S = 730.0
ENC_SPEEDUP = 116.43

# Also show released 128k for context
REL_SGT_MB_S = 310.55
REL_HF_MB_S = 4.9

NAVY = "#0F2A44"
CORAL = "#E06C4F"
TEAL = "#2A9D8F"
MUTED = "#5A6772"
CREAM = "#F7F4EF"
SOFT = "#E8EEF2"


def make_png():
    fig = plt.figure(figsize=(13.333, 7.5), dpi=200, facecolor="white")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    # Title bar
    ax.add_patch(FancyBboxPatch((0, 88), 100, 12, boxstyle="square,pad=0",
                                facecolor=NAVY, edgecolor="none"))
    ax.text(50, 95.5, "Original SuperBPE  vs  supergigatoken",
            ha="center", va="center", fontsize=22, fontweight="bold", color="white")
    ax.text(50, 90.5, "Matched 50k vocab · 100 MB train / 100 MB encode · OpenWebText",
            ha="center", va="center", fontsize=11, color="#C8D6E0")

    # Two columns headers
    for x, title, color in [(25, "Original SuperBPE", CORAL), (75, "supergigatoken", TEAL)]:
        ax.add_patch(FancyBboxPatch((x - 20, 76), 40, 8, boxstyle="round,pad=0.3,rounding_size=1.2",
                                    facecolor=color, edgecolor="none"))
        ax.text(x, 80, title, ha="center", va="center", fontsize=14, fontweight="bold", color="white")

    # TRAIN panel
    ax.add_patch(FancyBboxPatch((4, 42), 92, 30, boxstyle="round,pad=0.4,rounding_size=1.5",
                                facecolor=CREAM, edgecolor=SOFT, linewidth=2))
    ax.text(50, 69, "TRAIN  ·  train_superbpe", ha="center", va="center",
            fontsize=13, fontweight="bold", color=NAVY)

    # Train bars
    max_t = REF_TRAIN_S
    bar_max_w = 28
    for x, val, label, color in [
        (25, REF_TRAIN_S, f"{REF_TRAIN_S:.0f} s", CORAL),
        (75, OURS_TRAIN_S, f"{OURS_TRAIN_S:.0f} s", TEAL),
    ]:
        w = bar_max_w * (val / max_t)
        ax.add_patch(FancyBboxPatch((x - w / 2, 52), w, 10, boxstyle="round,pad=0.2,rounding_size=0.8",
                                    facecolor=color, edgecolor="none"))
        ax.text(x, 57, label, ha="center", va="center", fontsize=18, fontweight="bold", color="white")
        ax.text(x, 48, "wall-clock train time", ha="center", va="center", fontsize=10, color=MUTED)

    ax.text(50, 44.5, f"{TRAIN_SPEEDUP:.0f}× faster training",
            ha="center", va="center", fontsize=16, fontweight="bold", color=TEAL)

    # THROUGHPUT panel
    ax.add_patch(FancyBboxPatch((4, 6), 92, 32, boxstyle="round,pad=0.4,rounding_size=1.5",
                                facecolor=CREAM, edgecolor=SOFT, linewidth=2))
    ax.text(50, 35, "ENCODE THROUGHPUT  ·  SuperBPE 50k (same tokenizer.json)",
            ha="center", va="center", fontsize=13, fontweight="bold", color=NAVY)

    # Throughput bars — log-ish visual: HF tiny, SGT huge
    # Use sqrt scale for display so both readable
    max_mb = SGT_MB_S
    for x, val, label, sub, color in [
        (25, HF_MB_S, f"{HF_MB_S:.1f} MB/s", "HuggingFace encode", CORAL),
        (75, SGT_MB_S, f"{SGT_MB_S:.0f} MB/s", "supergigatoken Superword", TEAL),
    ]:
        # display width uses sqrt so small bar still visible
        w = 6 + 26 * np.sqrt(val / max_mb)
        ax.add_patch(FancyBboxPatch((x - w / 2, 18), w, 10, boxstyle="round,pad=0.2,rounding_size=0.8",
                                    facecolor=color, edgecolor="none"))
        ax.text(x, 23, label, ha="center", va="center", fontsize=16, fontweight="bold", color="white")
        ax.text(x, 14.5, sub, ha="center", va="center", fontsize=10, color=MUTED)

    ax.text(50, 9.5, f"{ENC_SPEEDUP:.0f}× faster encoding",
            ha="center", va="center", fontsize=16, fontweight="bold", color=TEAL)

    fig.savefig(PNG, dpi=200, facecolor="white", bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote {PNG}")


def make_pptx():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    s = prs.slides.add_slide(prs.slide_layouts[6])
    # full-bleed the PNG
    s.shapes.add_picture(str(PNG), 0, 0, width=Inches(13.333), height=Inches(7.5))
    prs.save(str(PPTX))
    print(f"Wrote {PPTX}")


if __name__ == "__main__":
    make_png()
    make_pptx()
