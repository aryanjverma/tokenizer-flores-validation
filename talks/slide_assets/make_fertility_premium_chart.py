"""Two-panel chart: fertility | premium (Mandarin fertility omitted)."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(r"c:\Users\aryan\projects\tokenizer-flores-validation")
METRICS = ROOT / "artifacts" / "plan_a" / "scale" / "flores_suite" / "metrics.json"
OUT = Path(__file__).resolve().parent / "fertility_premium_by_language.png"

# Fertility panel: no Mandarin
FERT_LANGS = ["eng_Latn", "hat_Latn", "hin_Deva", "hun_Latn", "swh_Latn"]
# Premium panel: all six
PREM_LANGS = ["eng_Latn", "hat_Latn", "hin_Deva", "hun_Latn", "swh_Latn", "zho_Hans"]
LANG_LABEL = {
    "eng_Latn": "English",
    "hat_Latn": "Haitian\nCreole",
    "hin_Deva": "Hindi",
    "hun_Latn": "Hungarian",
    "swh_Latn": "Swahili",
    "zho_Hans": "Mandarin",
}

BPE = "#264B6E"
SBP = "#E06C4F"


def main() -> None:
    rows = json.loads(METRICS.read_text(encoding="utf-8"))["metrics"]
    by = {(r["tokenizer_id"], r["language"]): r for r in rows}

    fig, (axL, axR) = plt.subplots(
        1, 2, figsize=(12.0, 6.0), dpi=160,
        gridspec_kw={"width_ratios": [1.0, 1.15]},
    )
    width = 0.36

    # ---- Left: fertility --------------------------------------------------
    x = np.arange(len(FERT_LANGS))
    bpe_f = [by[("bpe", l)]["fertility"] for l in FERT_LANGS]
    sbp_f = [by[("superbpe", l)]["fertility"] for l in FERT_LANGS]
    bars1 = axL.bar(x - width / 2, bpe_f, width, color=BPE, zorder=3, edgecolor="white")
    bars2 = axL.bar(x + width / 2, sbp_f, width, color=SBP, zorder=3, edgecolor="white")
    for bars in (bars1, bars2):
        for rect in bars:
            v = rect.get_height()
            axL.text(rect.get_x() + rect.get_width() / 2, v + 0.03, f"{v:.2f}",
                     ha="center", va="bottom", fontsize=9, fontweight="bold")
    axL.set_xticks(x)
    axL.set_xticklabels([])
    axL.tick_params(axis="x", length=0)
    axL.set_ylabel("Fertility  (tokens / whitespace word)")
    axL.set_title("Fertility  ·  lower is better", fontweight="bold")
    axL.set_ylim(0, max(bpe_f + sbp_f) * 1.22)
    axL.yaxis.grid(True, color="#E8EEF2", zorder=0)
    axL.set_axisbelow(True)

    # ---- Right: premium ---------------------------------------------------
    x = np.arange(len(PREM_LANGS))
    bpe_p = [by[("bpe", l)]["token_premium"] for l in PREM_LANGS]
    sbp_p = [by[("superbpe", l)]["token_premium"] for l in PREM_LANGS]
    bars1 = axR.bar(x - width / 2, bpe_p, width, label="BPE", color=BPE, zorder=3, edgecolor="white")
    bars2 = axR.bar(x + width / 2, sbp_p, width, label="SuperBPE", color=SBP, zorder=3, edgecolor="white")
    for bars in (bars1, bars2):
        for rect in bars:
            v = rect.get_height()
            axR.text(rect.get_x() + rect.get_width() / 2, v + 0.02, f"{v:.2f}",
                     ha="center", va="bottom", fontsize=9, fontweight="bold")
    axR.axhline(1.0, color="#9AA3AF", linestyle="--", linewidth=1, zorder=1)
    axR.set_xticks(x)
    axR.set_xticklabels([LANG_LABEL[l] for l in PREM_LANGS], fontsize=10)
    axR.set_ylabel("Token premium  (tokensℓ / tokensEnglish)")
    axR.set_title("English-relative premium  ·  lower is fairer", fontweight="bold")
    axR.set_ylim(0, max(bpe_p + sbp_p) * 1.22)
    axR.legend(frameon=False, loc="upper right")
    axR.yaxis.grid(True, color="#E8EEF2", zorder=0)
    axR.set_axisbelow(True)

    fig.suptitle(
        "Matched BPE vs SuperBPE on FLORES-200",
        fontsize=14, fontweight="bold", y=0.98,
    )
    fig.text(
        0.5, 0.02,
        "Equal-byte 6-language train · FLORES-200 devtest  ·  "
        "Mandarin omitted from fertility (tokens/word not meaningful for CJK)",
        ha="center", fontsize=9, color="#5A6772",
    )
    fig.tight_layout(rect=(0, 0.05, 1, 0.94))
    fig.savefig(OUT, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
