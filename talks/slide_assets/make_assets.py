"""Generate copy-paste slide assets: fertility, STRR, BPE train time, LM tables."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyBboxPatch

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
COMP = ROOT / "artifacts" / "plan_a" / "scale" / "flores_compression" / "metrics.json"
BPB = Path(r"c:\Users\aryan\projects\edullm-data\artifacts\plan_b_gpu\eval\approx_bpb.json")
TRAINER = Path(r"c:\Users\aryan\projects\supergigatoken\benchmarks\superbpe\results_trainer.json")

LANG_ORDER = ["eng_Latn", "hat_Latn", "hin_Deva", "hun_Latn", "swh_Latn", "zho_Hans"]
LANG_LABEL = {
    "eng_Latn": "English",
    "hat_Latn": "Haitian Creole",
    "hin_Deva": "Hindi",
    "hun_Latn": "Hungarian",
    "swh_Latn": "Swahili",
    "zho_Hans": "Mandarin",
}

BPE_C = "#264B6E"
SBP_C = "#E06C4F"
HF_C = "#8A9099"
INK = "#1A1A1A"
MUTED = "#5A6772"


def _style():
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.edgecolor": "#C5CDD4",
            "axes.labelcolor": INK,
            "xtick.color": INK,
            "ytick.color": INK,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "axes.titlesize": 16,
            "axes.labelsize": 12,
            "xtick.labelsize": 11,
            "ytick.labelsize": 11,
        }
    )


def _load_metrics():
    rows = json.loads(COMP.read_text(encoding="utf-8"))["metrics"]
    return pd.DataFrame(rows)


def grouped_bars(df, metric, title, ylabel, out_path, omit_cjk=False, higher_better=False):
    data = df.copy()
    if omit_cjk:
        data = data[data["language"] != "zho_Hans"]
    langs = [l for l in LANG_ORDER if l in set(data["language"])]
    labels = [LANG_LABEL[l] for l in langs]
    bpe = [float(data[(data.language == l) & (data.tokenizer_id == "bpe")][metric].iloc[0]) for l in langs]
    sbp = [float(data[(data.language == l) & (data.tokenizer_id == "superbpe")][metric].iloc[0]) for l in langs]

    x = np.arange(len(langs))
    w = 0.36
    fig, ax = plt.subplots(figsize=(10.5, 5.2), dpi=200)
    ax.bar(x - w / 2, bpe, w, label="gigatoken (BPE)", color=BPE_C, zorder=3)
    ax.bar(x + w / 2, sbp, w, label="supergigatoken (SuperBPE)", color=SBP_C, zorder=3)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=20, ha="right")
    ax.set_ylabel(ylabel)
    ax.set_title(title, pad=12, color=INK, fontweight="bold")
    ax.legend(frameon=False, loc="upper right")
    ax.yaxis.grid(True, color="#E8EEF2", zorder=0)
    ax.set_axisbelow(True)
    note = "Higher is better" if higher_better else "Lower is better"
    ax.text(0.0, -0.18, f"FLORES-200 devtest · matched equal-byte 6-lang tokenizers · {note}",
            transform=ax.transAxes, fontsize=9, color=MUTED)
    fig.tight_layout()
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote {out_path}")


def train_time_chart():
    d = json.loads(TRAINER.read_text(encoding="utf-8"))
    gt = d["engines"]["gigatoken"]["train_s"]
    hf = d["engines"]["hf"]["train_s"]
    speedup = d["speedup_vs_hf"]

    fig, ax = plt.subplots(figsize=(8.5, 5.0), dpi=200)
    names = ["HuggingFace\nBpeTrainer", "supergigatoken\ntrain_bpe\n(gigatoken)"]
    vals = [hf, gt]
    colors = [HF_C, BPE_C]
    bars = ax.bar(names, vals, color=colors, width=0.55, zorder=3)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.25, f"{v:.1f} s",
                ha="center", va="bottom", fontsize=14, fontweight="bold", color=INK)
    ax.set_ylabel("Train time (seconds)")
    ax.set_title("BPE training time — 50k vocab on 100 MB OpenWebText", pad=12, fontweight="bold")
    ax.set_ylim(0, max(vals) * 1.25)
    ax.yaxis.grid(True, color="#E8EEF2", zorder=0)
    ax.set_axisbelow(True)
    ax.text(0.5, 0.92, f"{speedup:.1f}× faster than HuggingFace",
            transform=ax.transAxes, ha="center", fontsize=13, color=BPE_C, fontweight="bold")
    ax.text(0.0, -0.14, "Source: supergigatoken/benchmarks/superbpe/results_trainer.json (min of 3)",
            transform=ax.transAxes, fontsize=9, color=MUTED)
    fig.tight_layout()
    out = OUT / "bpe_train_time_supergigatoken.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote {out}")


def bits_bpb_tables():
    bits = {
        "eng_Latn": (5.5677, 6.7157, +1.1480),
        "hat_Latn": (5.9132, 7.1050, +1.1917),
        "hin_Deva": (4.2699, 5.2702, +1.0003),
        "hun_Latn": (5.1323, 5.9935, +0.8611),
        "swh_Latn": (5.3161, 6.1749, +0.8588),
        "zho_Hans": (6.5212, 6.4756, -0.0456),
    }
    bpb = json.loads(BPB.read_text(encoding="utf-8"))["languages"]
    micro = json.loads(BPB.read_text(encoding="utf-8"))["micro_non_cjk"]

    # Markdown tables
    md_bits = ["# Phase 0 bits/token (olmo2_100M @ step7629)", "",
               "| Language | BPE | SuperBPE | Δ (S−B) |",
               "|---|---:|---:|---:|"]
    md_bpb = ["# Phase 0 approx BPB = bits/token ÷ FLORES UTF-8 bytes/token", "",
              "| Language | BPE | SuperBPE | Δ (S−B) |",
              "|---|---:|---:|---:|"]
    for lang in LANG_ORDER:
        name = LANG_LABEL[lang]
        b, s, d = bits[lang]
        md_bits.append(f"| {name} | {b:.4f} | {s:.4f} | {d:+.4f} |")
        row = bpb[lang]
        md_bpb.append(
            f"| {name} | {row['bpe']:.4f} | {row['superbpe']:.4f} | {row['delta']:+.4f} |"
        )
    md_bits += ["", "| **Micro** | **5.4534** | **6.2891** | **+0.8357** |",
                "", "Lower is better. Negative Δ favors SuperBPE."]
    md_bpb += [
        "",
        f"| **Micro (non-CJK)** | **{micro['bpe']:.4f}** | **{micro['superbpe']:.4f}** | **{micro['delta']:+.4f}** |",
        "",
        "Lower is better. Negative Δ favors SuperBPE.",
        "Approx BPB uses FLORES fertility denominator (domain caveat).",
    ]
    (OUT / "table_bits_per_token.md").write_text("\n".join(md_bits) + "\n", encoding="utf-8")
    (OUT / "table_approx_bpb.md").write_text("\n".join(md_bpb) + "\n", encoding="utf-8")

    # PNG tables (easy paste into Slides)
    def render_table(path, title, rows, footnote):
        fig, ax = plt.subplots(figsize=(10.5, 4.8), dpi=200)
        ax.axis("off")
        ax.set_title(title, fontsize=15, fontweight="bold", color=INK, pad=18)
        col_labels = ["Language", "BPE", "SuperBPE", "Δ (S−B)"]
        table = ax.table(
            cellText=rows,
            colLabels=col_labels,
            loc="center",
            cellLoc="center",
            colColours=["#0F2A44"] * 4,
        )
        table.auto_set_font_size(False)
        table.set_fontsize(12)
        table.scale(1.2, 1.55)
        for (r, c), cell in table.get_celld().items():
            cell.set_edgecolor("#D5DCE2")
            if r == 0:
                cell.get_text().set_color("white")
                cell.get_text().set_fontweight("bold")
            else:
                cell.set_facecolor("#FFFFFF" if r % 2 else "#F7F4EF")
                # bold better (lower) value in BPE/SuperBPE cols
                if c in (1, 2) and r > 0 and r < len(rows):
                    try:
                        b_val = float(rows[r - 1][1])
                        s_val = float(rows[r - 1][2])
                        better_col = 1 if b_val <= s_val else 2
                        if c == better_col:
                            cell.get_text().set_fontweight("bold")
                            cell.get_text().set_color(BPE_C if better_col == 1 else SBP_C)
                    except ValueError:
                        pass
                if c == 3 and r > 0:
                    txt = rows[r - 1][3]
                    if txt.startswith("-"):
                        cell.get_text().set_color("#2A9D8F")
                        cell.get_text().set_fontweight("bold")
        ax.text(0.5, 0.02, footnote, transform=ax.transAxes, ha="center", fontsize=9, color=MUTED)
        fig.savefig(path, bbox_inches="tight")
        plt.close(fig)
        print(f"Wrote {path}")

    bits_rows = []
    for lang in LANG_ORDER:
        b, s, d = bits[lang]
        bits_rows.append([LANG_LABEL[lang], f"{b:.4f}", f"{s:.4f}", f"{d:+.4f}"])
    bits_rows.append(["Micro", "5.4534", "6.2891", "+0.8357"])
    render_table(
        OUT / "table_bits_per_token.png",
        "Phase 0 bits/token — BPE vs SuperBPE (olmo2_100M)",
        bits_rows,
        "Lower is better · bold = better arm · negative Δ favors SuperBPE",
    )

    bpb_rows = []
    for lang in LANG_ORDER:
        row = bpb[lang]
        bpb_rows.append(
            [LANG_LABEL[lang], f"{row['bpe']:.4f}", f"{row['superbpe']:.4f}", f"{row['delta']:+.4f}"]
        )
    bpb_rows.append(
        ["Micro (non-CJK)", f"{micro['bpe']:.4f}", f"{micro['superbpe']:.4f}", f"{micro['delta']:+.4f}"]
    )
    render_table(
        OUT / "table_approx_bpb.png",
        "Phase 0 approx BPB — bits/token ÷ FLORES UTF-8 bytes/token",
        bpb_rows,
        "Lower is better · bold = better arm · fertility from FLORES (domain caveat)",
    )

    # Also CSV for Sheets paste
    pd.DataFrame(
        [{"language": LANG_LABEL[l], "bpe": bits[l][0], "superbpe": bits[l][1], "delta": bits[l][2]}
         for l in LANG_ORDER]
        + [{"language": "Micro", "bpe": 5.4534, "superbpe": 6.2891, "delta": 0.8357}]
    ).to_csv(OUT / "table_bits_per_token.csv", index=False)
    pd.DataFrame(
        [{"language": LANG_LABEL[l], "bpe": bpb[l]["bpe"], "superbpe": bpb[l]["superbpe"], "delta": bpb[l]["delta"]}
         for l in LANG_ORDER]
        + [{"language": "Micro (non-CJK)", "bpe": micro["bpe"], "superbpe": micro["superbpe"], "delta": micro["delta"]}]
    ).to_csv(OUT / "table_approx_bpb.csv", index=False)


def copy_existing():
    # keep originals alongside for convenience
    src = ROOT / "artifacts" / "plan_a" / "scale" / "flores_suite" / "plots" / "fertility.png"
    if src.exists():
        dest = OUT / "fertility_existing_plan_a.png"
        dest.write_bytes(src.read_bytes())
        print(f"Copied {dest}")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    _style()
    df = _load_metrics()

    grouped_bars(
        df,
        "fertility",
        "Token fertility (tokens / whitespace word)",
        "Fertility",
        OUT / "fertility_bpe_vs_superbpe.png",
        omit_cjk=True,
        higher_better=False,
    )
    # with Mandarin on a separate note chart (log-ish / separate)
    grouped_bars(
        df,
        "fertility",
        "Token fertility — all six languages (Mandarin not tokens/word)",
        "Fertility",
        OUT / "fertility_bpe_vs_superbpe_with_mandarin.png",
        omit_cjk=False,
        higher_better=False,
    )
    grouped_bars(
        df,
        "strr",
        "STRR — single-token retention rate",
        "STRR (share of words → exactly 1 token)",
        OUT / "strr_bpe_vs_superbpe.png",
        omit_cjk=True,  # Mandarin STRR is null
        higher_better=True,
    )
    grouped_bars(
        df,
        "token_premium",
        "English-relative token premium",
        "Premium (tokens_ℓ / tokens_English)",
        OUT / "token_premium_bpe_vs_superbpe.png",
        omit_cjk=False,
        higher_better=False,
    )

    train_time_chart()
    bits_bpb_tables()
    copy_existing()

    # also dump STRR/fertility CSVs next to charts
    wide_dir = ROOT / "artifacts" / "plan_a" / "scale" / "flores_compression"
    for name in ("fertility_wide.csv", "strr_wide.csv", "token_premium_wide.csv"):
        src = wide_dir / name
        if src.exists():
            (OUT / name).write_bytes(src.read_bytes())
            print(f"Copied {OUT / name}")

    readme = """# Slide assets (copy-paste)

Drop these PNGs straight into Google Slides.

## Charts
- `fertility_bpe_vs_superbpe.png` — fertility, no Mandarin (recommended)
- `fertility_bpe_vs_superbpe_with_mandarin.png` — includes Mandarin
- `strr_bpe_vs_superbpe.png` — STRR (higher = better; Mandarin N/A)
- `token_premium_bpe_vs_superbpe.png` — English-relative premium
- `bpe_train_time_supergigatoken.png` — HF 10.4s vs train_bpe 2.8s

## Tables (PNG + CSV + MD)
- `table_bits_per_token.png` / `.csv` / `.md`
- `table_approx_bpb.png` / `.csv` / `.md`

Sources: Plan A scale FLORES compression; Phase 0 eval; supergigatoken results_trainer.json.
"""
    (OUT / "README.md").write_text(readme, encoding="utf-8")
    print(f"\nAll assets in: {OUT}")


if __name__ == "__main__":
    main()
