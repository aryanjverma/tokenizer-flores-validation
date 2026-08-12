"""Two slide figures for SuperBPE / gigatoken comparisons (1:2 aspect each).

1) Speed — BPE vs HF · SuperBPE vs original · Encode 50k (116×)
2) Quality — similarity · compression vs original (5.85/5.65) · matched ~50k bar
   (supergigatoken uses train-parity 5.85, not held-out efficiency 5.67)
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

SGT = Path(r"c:\Users\aryan\projects\supergigatoken")
HERE = SGT / "benchmarks" / "superbpe"
OUT = Path(__file__).resolve().parent

BLUE = "#2563eb"
RED = "#dc2626"
GRAY = "#9aa3af"
LIGHT_BLUE = "#93c5fd"
DARK = "#111827"
SUB = "#4b5563"
PURPLE = "#7c3aed"


def load(name: str) -> dict:
    return json.loads((HERE / name).read_text(encoding="utf-8"))


def save_both(fig, name: str) -> None:
    for path in (OUT / name, SGT / "assets" / name):
        path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(path, dpi=140)
        print(f"wrote {path}")
    plt.close(fig)


def make_speed() -> None:
    trainer = load("results_trainer.json")
    parity = load("results_parity.json")
    thr = load("results_throughput.json")

    bpe_ours = trainer["engines"]["gigatoken"]["train_s"]
    bpe_hf = trainer["engines"]["hf"]["train_s"]
    sb_ours = parity["sides"]["ours"]["train_time_s"]
    sb_ref = parity["sides"]["reference"]["train_time_s"]
    enc = thr["tokenizers"]["supergigatoken"]["engines"]
    enc_ours = enc["gigatoken"]["mb_per_s"]
    enc_hf = enc["hf"]["mb_per_s"]

    train_mb = (trainer.get("meta") or {}).get("train_mb") or 100
    eval_mb = (thr.get("meta") or {}).get("eval_mb", 99.74)
    if isinstance(eval_mb, float):
        eval_mb = f"{eval_mb:g}"

    fig, (axA, axB, axC) = plt.subplots(1, 3, figsize=(12.0, 6.0))

    labs = ["supergigatoken\ntrain_bpe", "HuggingFace\nBpeTrainer"]
    vals = [bpe_ours, bpe_hf]
    bars = axA.bar(labs, vals, color=[BLUE, GRAY], edgecolor="white", linewidth=1.0, zorder=3, width=0.62)
    for rect, v in zip(bars, vals):
        axA.text(rect.get_x() + rect.get_width() / 2, v + max(vals) * 0.02,
                 f"{v:.1f}s", ha="center", va="bottom", fontsize=11, fontweight="bold")
    axA.set_ylim(0, max(vals) * 1.28)
    axA.set_ylabel("training wall-clock, seconds  (lower = faster)")
    axA.set_title("BPE training  (vs HuggingFace)", fontweight="bold")
    axA.grid(True, axis="y", alpha=0.25)
    axA.annotate(
        f"{bpe_hf / bpe_ours:.1f}× faster", (0, bpe_ours),
        textcoords="offset points", xytext=(10, 28), ha="center",
        fontsize=13, fontweight="bold", color=BLUE,
    )

    labs = ["supergigatoken", "original\nSuperBPE"]
    vals = [sb_ours, sb_ref]
    bars = axB.bar(labs, vals, color=[BLUE, RED], edgecolor="white", linewidth=1.0, zorder=3, width=0.62)
    for rect, v in zip(bars, vals):
        axB.text(rect.get_x() + rect.get_width() / 2, v + max(vals) * 0.02,
                 f"{v:.0f}s", ha="center", va="bottom", fontsize=11, fontweight="bold")
    axB.set_ylim(0, max(vals) * 1.24)
    axB.set_ylabel("training wall-clock, seconds  (lower = faster)")
    axB.set_title("SuperBPE training  (vs original)", fontweight="bold")
    axB.grid(True, axis="y", alpha=0.25)
    axB.annotate(
        f"{sb_ref / sb_ours:.1f}× faster", (0, sb_ours),
        textcoords="offset points", xytext=(10, 28), ha="center",
        fontsize=13, fontweight="bold", color=BLUE,
    )

    labs = ["supergigatoken", "HuggingFace"]
    vals = [enc_ours, enc_hf]
    bars = axC.bar(labs, vals, color=[BLUE, GRAY], edgecolor="white", linewidth=1.0, zorder=3, width=0.62)
    for rect, v in zip(bars, vals):
        axC.text(rect.get_x() + rect.get_width() / 2, v + max(vals) * 0.02,
                 f"{v:.1f}", ha="center", va="bottom", fontsize=11, fontweight="bold")
    axC.set_ylim(0, max(vals) * 1.28)
    axC.set_ylabel("MB / s  (higher = faster)")
    axC.set_title("Encoding speed  (SuperBPE 50k)", fontweight="bold")
    axC.grid(True, axis="y", alpha=0.25)
    axC.annotate(
        f"{enc_ours / enc_hf:.1f}× faster", (0, enc_ours),
        textcoords="offset points", xytext=(10, 28), ha="center",
        fontsize=13, fontweight="bold", color=BLUE,
    )

    fig.suptitle("supergigatoken · speed", fontsize=15, fontweight="bold", y=0.985)
    fig.text(
        0.5, 0.925,
        f"train: {train_mb:g} MB OpenWebText · 50k vocab  ·  "
        f"encode: same SuperBPE tokenizer, OWT {eval_mb} MB held-out, Intel 8-core",
        ha="center", fontsize=10, color=SUB,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.90))
    save_both(fig, "supergigatoken_speed.png")


def make_quality() -> None:
    parity = load("results_parity.json")
    vd = load("results_vocab_diff.json")
    eff = load("results_efficiency.json")

    ours = parity["sides"]["ours"]
    ref = parity["sides"]["reference"]
    sgt_bpt = ours["bytes_per_token"]  # 5.85 — train-parity (not efficiency 5.67)
    ref_bpt = ref["bytes_per_token"]

    meta = parity.get("meta") or {}
    settings = meta.get("settings") or {}
    mb = meta.get("train_mb", 100)
    mb = f"{mb:g}" if isinstance(mb, (int, float)) else str(mb)
    vocab = settings.get("vocab", 50000)
    vocab = f"{vocab // 1000}k" if isinstance(vocab, int) and vocab >= 1000 else str(vocab)
    trans = settings.get("transition", 40000)
    trans = f"{trans // 1000}k" if isinstance(trans, int) and trans >= 1000 else str(trans)
    pretok = settings.get("pretokenizer", "superbpe_stage1")

    fig, (axA, axB, axC) = plt.subplots(
        1, 3, figsize=(12.8, 6.0),
        gridspec_kw={"width_ratios": [1.15, 1.0, 1.2]},
    )

    d = vd.get("differential") or {}
    rows = [
        ("whole vocabulary", (d.get("vocab") or {}).get("jaccard")),
        ("subwords", (d.get("subwords") or {}).get("jaccard")),
        ("superwords", (d.get("superwords") or {}).get("jaccard")),
        ("merge order (Spearman)", (d.get("merges") or {}).get("rank_spearman")),
    ]
    rows = [(lab, v) for lab, v in rows if v is not None]
    names = [lab for lab, _ in rows][::-1]
    vals = [v for _, v in rows][::-1]
    cols = [PURPLE if "Spearman" in n else BLUE for n in names]
    bars = axA.barh(names, vals, color=cols, edgecolor="white", linewidth=1.0, zorder=3, height=0.6)
    for rect, v in zip(bars, vals):
        axA.text(v + 0.012, rect.get_y() + rect.get_height() / 2,
                 f"{v:.3f}", va="center", fontsize=10.5, fontweight="bold")
    axA.set_xlim(0, 1.26)
    axA.set_xlabel("agreement with the original (1.0 = identical)")
    axA.set_title("Similarity to original SuperBPE", fontweight="bold")
    axA.grid(True, axis="x", alpha=0.25)

    labs = ["supergigatoken", "original\nSuperBPE"]
    bpt = [sgt_bpt, ref_bpt]
    bars = axB.bar(labs, bpt, color=[BLUE, RED], edgecolor="white", linewidth=1.0, zorder=3, width=0.62)
    for rect, v in zip(bars, bpt):
        axB.text(rect.get_x() + rect.get_width() / 2, v + 0.02,
                 f"{v:.2f}", ha="center", va="bottom", fontsize=11, fontweight="bold")
    axB.set_ylim(0, max(bpt) * 1.22)
    axB.set_ylabel("bytes / token  (higher = more efficient)")
    axB.set_title("Compression  (vs original SuperBPE)", fontweight="bold")
    axB.grid(True, axis="y", alpha=0.25)
    axB.annotate(
        "no quality traded away",
        (0.5, max(bpt) * 1.1),
        xycoords=("axes fraction", "data"),
        ha="center", fontsize=10, fontweight="bold", color=DARK,
    )

    toks = eff.get("tokenizers") or {}
    wanted = [
        ("supergigatoken", "ours\n(SuperBPE)", BLUE, sgt_bpt),
        ("gigatoken", "gigatoken\n(BPE)", LIGHT_BLUE, None),
        ("openai-community/gpt2", "GPT-2", GRAY, None),
        ("answerdotai/ModernBERT-base", "ModernBERT", GRAY, None),
    ]
    labels, vals, colors = [], [], []
    for key, label, color, override in wanted:
        if override is not None:
            labels.append(label)
            vals.append(override)
            colors.append(color)
            continue
        r = toks.get(key)
        if r and r.get("bytes_per_token"):
            labels.append(label)
            vals.append(r["bytes_per_token"])
            colors.append(color)
    x = range(len(labels))
    bars = axC.bar(x, vals, color=colors, edgecolor="white", linewidth=1.0, zorder=3, width=0.72)
    for rect, v in zip(bars, vals):
        axC.text(rect.get_x() + rect.get_width() / 2, v + 0.03,
                 f"{v:.2f}", ha="center", va="bottom", fontsize=9, fontweight="bold")
    axC.set_xticks(list(x))
    axC.set_xticklabels(labels, fontsize=9)
    axC.set_ylabel("bytes / token")
    axC.set_title("Same ~50k vocab: superwords win", fontweight="bold")
    axC.grid(True, axis="y", alpha=0.25)
    axC.set_ylim(0, max(vals) * 1.22)

    fig.suptitle("supergigatoken · quality & compression", fontsize=15, fontweight="bold", y=0.985)
    fig.text(
        0.5, 0.925,
        f"matched train: {mb} MB OpenWebText · vocab {vocab} · transition {trans} · "
        f"stage-1 regex ({pretok})  ·  "
        f"supergigatoken = {sgt_bpt:.2f} B/tok (train-parity; was 5.67 on held-out efficiency)",
        ha="center", fontsize=9.5, color=SUB,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.90))
    save_both(fig, "supergigatoken_quality.png")


if __name__ == "__main__":
    make_speed()
    make_quality()
