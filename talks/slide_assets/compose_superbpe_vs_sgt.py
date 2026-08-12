"""Three-panel figure: train / quality / encoding (50k SuperBPE only).

Aspect ~1:2 (height:width). Style matches plot_readme.py.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

SGT = Path(r"c:\Users\aryan\projects\supergigatoken")
HERE = SGT / "benchmarks" / "superbpe"
OUT_SLIDES = Path(__file__).resolve().parent / "superbpe_vs_supergigatoken_with_throughput.png"
OUT_REPO = SGT / "assets" / "superbpe_vs_original_with_throughput.png"

BLUE = "#2563eb"
RED = "#dc2626"
GRAY = "#9aa3af"
DARK = "#111827"
SUB = "#4b5563"


def load(name: str) -> dict:
    return json.loads((HERE / name).read_text(encoding="utf-8"))


def main() -> None:
    par = load("results_parity.json")
    thr = load("results_throughput.json")
    ours = par["sides"]["ours"]
    ref = par["sides"]["reference"]
    meta = par.get("meta") or {}
    settings = meta.get("settings") or {}
    thr_meta = thr.get("meta") or {}

    # 1:2 height:width
    fig, (axA, axB, axC) = plt.subplots(1, 3, figsize=(12.0, 6.0))

    labels = ["supergigatoken", "original\nSuperBPE"]
    colors = [BLUE, RED]

    # ---- A: training time -------------------------------------------------
    times = [ours["train_time_s"], ref["train_time_s"]]
    bars = axA.bar(labels, times, color=colors, edgecolor="white", linewidth=1.0, zorder=3, width=0.62)
    for rect, v in zip(bars, times):
        axA.text(
            rect.get_x() + rect.get_width() / 2,
            v + max(times) * 0.02,
            f"{v:.0f}s",
            ha="center",
            va="bottom",
            fontsize=11,
            fontweight="bold",
        )
    axA.set_ylim(0, max(times) * 1.24)
    axA.set_ylabel("training wall-clock, seconds  (lower = faster)")
    axA.set_title("Training time", fontweight="bold")
    axA.grid(True, axis="y", alpha=0.25)
    axA.annotate(
        f"{ref['train_time_s'] / ours['train_time_s']:.1f}× faster",
        (0, times[0]),
        textcoords="offset points",
        xytext=(10, 28),
        ha="center",
        fontsize=13,
        fontweight="bold",
        color=BLUE,
    )

    # ---- B: quality -------------------------------------------------------
    bpt = [ours["bytes_per_token"], ref["bytes_per_token"]]
    bars = axB.bar(labels, bpt, color=colors, edgecolor="white", linewidth=1.0, zorder=3, width=0.62)
    for rect, v in zip(bars, bpt):
        axB.text(
            rect.get_x() + rect.get_width() / 2,
            v + 0.02,
            f"{v:.2f}",
            ha="center",
            va="bottom",
            fontsize=11,
            fontweight="bold",
        )
    axB.set_ylim(0, max(bpt) * 1.22)
    axB.set_ylabel("bytes / token  (higher = more efficient)")
    axB.set_title("Tokenizer quality", fontweight="bold")
    axB.grid(True, axis="y", alpha=0.25)
    axB.annotate(
        "no quality traded away",
        (0.5, max(bpt) * 1.1),
        xycoords=("axes fraction", "data"),
        ha="center",
        fontsize=10,
        fontweight="bold",
        color=DARK,
    )

    # ---- C: encoding speed — SuperBPE 50k only (116×) ---------------------
    eng = thr["tokenizers"]["supergigatoken"]["engines"]
    giga = eng["gigatoken"]["mb_per_s"]
    hf = eng["hf"]["mb_per_s"]
    enc_labels = ["supergigatoken", "HuggingFace"]
    enc_vals = [giga, hf]
    enc_colors = [BLUE, GRAY]
    bars = axC.bar(enc_labels, enc_vals, color=enc_colors, edgecolor="white", linewidth=1.0, zorder=3, width=0.62)
    for rect, v in zip(bars, enc_vals):
        axC.text(
            rect.get_x() + rect.get_width() / 2,
            v + max(enc_vals) * 0.02,
            f"{v:.1f}",
            ha="center",
            va="bottom",
            fontsize=11,
            fontweight="bold",
        )
    axC.set_ylim(0, max(enc_vals) * 1.28)
    axC.set_ylabel("MB / s  (higher = faster)")
    axC.set_title("Encoding speed  (SuperBPE 50k)", fontweight="bold")
    axC.grid(True, axis="y", alpha=0.25)
    axC.annotate(
        f"{giga / hf:.1f}× faster",
        (0, giga),
        textcoords="offset points",
        xytext=(10, 28),
        ha="center",
        fontsize=13,
        fontweight="bold",
        color=BLUE,
    )

    # ---- Shared title + subtitle ------------------------------------------
    mb = meta.get("train_mb")
    mb = f"{mb:g}" if isinstance(mb, (int, float)) else "?"
    vocab = settings.get("vocab")
    vocab = f"{vocab // 1000}k" if isinstance(vocab, int) and vocab >= 1000 else str(vocab)
    trans = settings.get("transition")
    trans = f"{trans // 1000}k" if isinstance(trans, int) and trans >= 1000 else str(trans)
    pretok = settings.get("pretokenizer", "?")
    cpu = thr_meta.get("cpu") or meta.get("cpu") or "?"
    cpu_short = "Intel 8-core" if "Intel" in str(cpu) else str(cpu)
    eval_mb = thr_meta.get("eval_mb", "?")
    if isinstance(eval_mb, float):
        eval_mb = f"{eval_mb:g}"

    fig.suptitle(
        "supergigatoken vs the original SuperBPE",
        fontsize=15,
        fontweight="bold",
        y=0.985,
    )
    fig.text(
        0.5,
        0.925,
        f"same {mb} MB OpenWebText slice · vocab {vocab} · transition {trans} · "
        f"identical stage-1 regex ({pretok})  ·  "
        f"encoding: same tokenizer, OWT {eval_mb} MB held-out, {cpu_short}",
        ha="center",
        fontsize=10,
        color=SUB,
    )

    fig.tight_layout(rect=(0, 0, 1, 0.90))
    for path in (OUT_SLIDES, OUT_REPO):
        path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(path, dpi=140)
        print(f"wrote {path}")
    plt.close(fig)


if __name__ == "__main__":
    main()
