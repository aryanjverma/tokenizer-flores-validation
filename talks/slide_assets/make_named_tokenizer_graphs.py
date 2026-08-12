"""Metric graphs with tokenizer names — who fragments badly is obvious."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
METRICS = ROOT / "results" / "metrics.json"
HEATMAP = ROOT / "results" / "figures" / "efficiency_token_premium_heatmap.png"

# Friendly names for slide audience
TOK_LABEL = {
    "o200k": "GPT-4o\n(o200k)",
    "llama": "Llama 3.1",
    "qwen": "Qwen 2.5",
    "glm": "GLM-4",
    "multi": "mT5\n(multi)",
    "superbpe": "SuperBPE\n(released)",
    "unigram": "Unigram",
    "wordpiece": "WordPiece",
}

# Highlight languages where tax is worst + controls
LANG_ORDER = [
    "eng_Latn",
    "swh_Latn",
    "hau_Latn",
    "hun_Latn",
    "amh_Ethi",
    "ory_Orya",
    "arz_Arab",
    "ary_Arab",
    "ukr_Cyrl",
    "zho_Hans",
]
LANG_LABEL = {
    "eng_Latn": "English",
    "swh_Latn": "Swahili",
    "hau_Latn": "Hausa",
    "hun_Latn": "Hungarian",
    "amh_Ethi": "Amharic",
    "ory_Orya": "Odia",
    "arz_Arab": "Egyptian Arabic",
    "ary_Arab": "Moroccan Arabic",
    "ukr_Cyrl": "Ukrainian",
    "zho_Hans": "Mandarin",
}

# Order tokenizers roughly "better → worse" by mean premium on non-English
TOK_ORDER = ["superbpe", "llama", "qwen", "glm", "o200k", "multi", "unigram", "wordpiece"]


def heatmap(df, metric, title, out_path, cmap="lower", omit_cjk_null=False, vmax_label="", *, hide_lang_tok_labels: bool = False):
    toks = [t for t in TOK_ORDER if t in set(df.tokenizer_id)]
    langs = [l for l in LANG_ORDER if l in set(df.language)]
    mat = np.full((len(langs), len(toks)), np.nan)
    for i, lang in enumerate(langs):
        for j, tok in enumerate(toks):
            hit = df[(df.language == lang) & (df.tokenizer_id == tok)]
            if hit.empty:
                continue
            val = hit.iloc[0][metric]
            if val is None or (isinstance(val, float) and np.isnan(val)):
                continue
            mat[i, j] = float(val)

    fig, ax = plt.subplots(figsize=(12.5, 6.8), dpi=200)
    if cmap == "lower":
        # high = bad
        cmap_name = "YlOrRd"
    else:
        # high = good (STRR)
        cmap_name = "YlGn"

    im = ax.imshow(mat, aspect="auto", cmap=cmap_name)
    ax.set_xticks(range(len(toks)))
    ax.set_yticks(range(len(langs)))
    if hide_lang_tok_labels:
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        ax.tick_params(length=0)
        ax.set_xlabel("")
        ax.set_ylabel("")
    else:
        ax.set_xticklabels([TOK_LABEL.get(t, t) for t in toks], fontsize=10)
        ax.set_yticklabels([LANG_LABEL.get(l, l) for l in langs], fontsize=11)
        ax.set_xlabel("Tokenizer", fontsize=12, labelpad=8)
        ax.set_ylabel("Language (FLORES-200)", fontsize=12)
    ax.set_title(title, fontsize=15, fontweight="bold", pad=14)

    # annotate cells
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            v = mat[i, j]
            if np.isnan(v):
                txt = "—"
                color = "#888"
            else:
                txt = f"{v:.2f}"
                # contrast
                color = "black" if (cmap == "lower" and v < np.nanmax(mat) * 0.65) or (
                    cmap == "higher" and v > np.nanmax(mat) * 0.35
                ) else "white"
            ax.text(j, i, txt, ha="center", va="center", fontsize=9, color=color, fontweight="bold")

    cbar = fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
    cbar.set_label(vmax_label or metric, fontsize=10)
    fig.text(
        0.5, 0.01,
        "Study A · FLORES-200 devtest · cell = metric value · redder = worse (except STRR: greener = better)",
        ha="center", fontsize=9, color="#5A6772",
    )
    fig.tight_layout(rect=[0, 0.03, 1, 1])
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote {out_path}")


def grouped_worst(df, metric, title, out_path, higher_better=False, langs=None, *, hide_lang_tok_labels: bool = False):
    """Bar chart: for selected hard languages, every tokenizer named."""
    langs = langs or ["amh_Ethi", "ory_Orya", "arz_Arab", "hun_Latn", "swh_Latn"]
    toks = [t for t in TOK_ORDER if t in set(df.tokenizer_id)]
    labels = [TOK_LABEL.get(t, t).replace("\n", " ") for t in toks]

    n_lang = len(langs)
    fig, axes = plt.subplots(1, n_lang, figsize=(14, 5.2), dpi=200, sharey=True)
    if n_lang == 1:
        axes = [axes]

    colors = plt.cm.tab10(np.linspace(0, 0.9, len(toks)))
    for ax, lang in zip(axes, langs):
        vals = []
        for t in toks:
            hit = df[(df.language == lang) & (df.tokenizer_id == t)]
            v = hit.iloc[0][metric] if not hit.empty else np.nan
            vals.append(float(v) if v is not None and not (isinstance(v, float) and np.isnan(v)) else np.nan)
        bars = ax.barh(range(len(toks)), vals, color=colors, zorder=3)
        ax.set_yticks(range(len(toks)))
        if hide_lang_tok_labels:
            ax.set_yticklabels([])
            ax.tick_params(axis="y", length=0)
            ax.set_title("")
        else:
            ax.set_yticklabels(labels, fontsize=8)
            ax.set_title(LANG_LABEL[lang], fontsize=11, fontweight="bold")
        ax.xaxis.grid(True, color="#E8EEF2", zorder=0)
        ax.set_axisbelow(True)
        # highlight worst
        finite = [(i, v) for i, v in enumerate(vals) if not np.isnan(v)]
        if finite:
            worst_i = max(finite, key=lambda iv: iv[1])[0] if not higher_better else min(finite, key=lambda iv: iv[1])[0]
            bars[worst_i].set_edgecolor("#C0392B")
            bars[worst_i].set_linewidth(2.5)

    fig.suptitle(title, fontsize=14, fontweight="bold", y=1.02)
    fig.text(0.5, -0.02, "Red outline = worst tokenizer on that language", ha="center", fontsize=9, color="#5A6772")
    fig.tight_layout()
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote {out_path}")


def main():
    df = pd.DataFrame(json.loads(METRICS.read_text(encoding="utf-8")))

    heatmap(
        df, "token_premium",
        "Token premium by tokenizer × language  (English = 1.0 · higher = worse)",
        OUT / "premium_by_tokenizer_heatmap.png",
        cmap="lower",
        vmax_label="Premium vs English",
    )
    heatmap(
        df, "fertility",
        "Token fertility by tokenizer × language  (tokens/word · higher = worse)",
        OUT / "fertility_by_tokenizer_heatmap.png",
        cmap="lower",
        vmax_label="Fertility",
        hide_lang_tok_labels=True,
    )
    # STRR: drop Mandarin (null)
    df_strr = df[df.language != "zho_Hans"].copy()
    heatmap(
        df_strr, "strr",
        "STRR by tokenizer × language  (share of words kept as 1 token · higher = better)",
        OUT / "strr_by_tokenizer_heatmap.png",
        cmap="higher",
        vmax_label="STRR",
        hide_lang_tok_labels=True,
    )

    grouped_worst(
        df, "token_premium",
        "Who overcharges? Token premium — named tokenizers",
        OUT / "premium_by_tokenizer_bars.png",
        higher_better=False,
    )
    grouped_worst(
        df, "fertility",
        "Who fragments? Fertility — named tokenizers",
        OUT / "fertility_by_tokenizer_bars.png",
        higher_better=False,
        hide_lang_tok_labels=True,
    )
    grouped_worst(
        df_strr, "strr",
        "Who keeps whole words? STRR — named tokenizers (higher better)",
        OUT / "strr_by_tokenizer_bars.png",
        higher_better=True,
        hide_lang_tok_labels=True,
    )

    # also copy paper heatmap with frontier names if present
    if HEATMAP.exists():
        dest = OUT / "premium_frontier_heatmap_paper.png"
        dest.write_bytes(HEATMAP.read_bytes())
        print(f"Copied {dest}")

    print(f"\nAll named-tokenizer graphs in: {OUT}")


if __name__ == "__main__":
    main()
