"""Build a 5-minute, diagram-first PPTX on tokenizer fairness + SuperBPE."""

from __future__ import annotations

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.oxml.ns import nsmap
from pptx.util import Emu, Inches, Pt

ROOT = Path(__file__).resolve().parents[1]
SUPER = Path(r"c:\Users\aryan\projects\supergigatoken")
OUT = Path(__file__).resolve().parent / "tokenizer_fairness_5min.pptx"

# Palette — clean navy / coral (not purple-default)
NAVY = RGBColor(0x0F, 0x2A, 0x44)
INK = RGBColor(0x1A, 0x1A, 0x1A)
MUTED = RGBColor(0x5A, 0x67, 0x72)
CORAL = RGBColor(0xE0, 0x6C, 0x4F)
TEAL = RGBColor(0x2A, 0x9D, 0x8F)
CREAM = RGBColor(0xF7, 0xF4, 0xEF)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
SOFT = RGBColor(0xE8, 0xEE, 0xF2)
BPE_C = RGBColor(0x26, 0x4B, 0x6E)
SBP_C = RGBColor(0xE0, 0x6C, 0x4F)


def _set_run(run, text, size=18, bold=False, color=INK, font="Calibri"):
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = font


def _fill(shape, color):
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()


def _box(slide, left, top, width, height, fill=SOFT, line=None):
    sh = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    _fill(sh, fill)
    if line is not None:
        sh.line.color.rgb = line
        sh.line.width = Pt(1.5)
    else:
        sh.line.fill.background()
    try:
        sh.adjustments[0] = 0.08
    except Exception:
        pass
    return sh


def _txt(slide, left, top, width, height, text, size=18, bold=False, color=INK, align=PP_ALIGN.LEFT):
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    _set_run(p.add_run(), text, size=size, bold=bold, color=color)
    return box


def _title_bar(slide, title, subtitle=None):
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.95))
    _fill(bar, NAVY)
    _txt(slide, Inches(0.5), Inches(0.22), Inches(12), Inches(0.5), title, size=28, bold=True, color=WHITE)
    if subtitle:
        _txt(slide, Inches(0.5), Inches(1.05), Inches(12), Inches(0.4), subtitle, size=16, color=MUTED)


def _blank(prs):
    return prs.slides.add_slide(prs.slide_layouts[6])


def _arrow(slide, left, top, width, height, fill=CORAL):
    sh = slide.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, left, top, width, height)
    _fill(sh, fill)
    return sh


def _chip(slide, left, top, width, height, label, fill, text_color=WHITE):
    sh = _box(slide, left, top, width, height, fill=fill)
    tf = sh.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    _set_run(p.add_run(), label, size=14, bold=True, color=text_color)
    return sh


def slide_title(prs):
    s = _blank(prs)
    bg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    _fill(bg, NAVY)
    accent = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, Inches(5.6), Inches(13.333), Inches(1.9))
    _fill(accent, RGBColor(0x15, 0x3A, 0x58))
    _txt(s, Inches(0.8), Inches(2.0), Inches(11.5), Inches(1.2),
         "Who pays the token tax?", size=40, bold=True, color=WHITE)
    _txt(s, Inches(0.8), Inches(3.3), Inches(11.5), Inches(0.8),
         "Fertility inequality, SuperBPE, and a 100M → 1B bake-off", size=22, color=RGBColor(0xC8, 0xD6, 0xE0))
    _txt(s, Inches(0.8), Inches(5.9), Inches(11.5), Inches(0.4),
         "Aryan Verma  ·  Frank Gonzalez", size=16, color=RGBColor(0xC8, 0xD6, 0xE0))
    _txt(s, Inches(0.8), Inches(6.4), Inches(11.5), Inches(0.4),
         "5-minute overview", size=14, color=RGBColor(0x9A, 0xB0, 0xC0))


def slide_agenda(prs):
    s = _blank(prs)
    _title_bar(s, "Roadmap", "Five minutes")
    items = [
        ("1", "The problem", "Same meaning → different token counts"),
        ("2", "What we measured", "FLORES premiums & fertility"),
        ("3", "A candidate fix", "SuperBPE + our Rust trainers"),
        ("4", "Does it help LMs?", "100M done · 1B running"),
    ]
    for i, (n, h, d) in enumerate(items):
        left = Inches(0.6 + i * 3.1)
        _box(s, left, Inches(2.0), Inches(2.9), Inches(3.6), fill=CREAM, line=SOFT)
        _chip(s, left + Inches(0.95), Inches(2.3), Inches(1.0), Inches(0.7), n, CORAL)
        _txt(s, left + Inches(0.15), Inches(3.3), Inches(2.6), Inches(0.6), h, size=18, bold=True, color=NAVY, align=PP_ALIGN.CENTER)
        _txt(s, left + Inches(0.15), Inches(4.0), Inches(2.6), Inches(1.2), d, size=14, color=MUTED, align=PP_ALIGN.CENTER)


def slide_fertility_problem(prs):
    s = _blank(prs)
    _title_bar(s, "Same sentence. Different bill.", "Token fertility is unequal across languages")
    # Three language cards showing "token stacks"
    langs = [
        ("English", "few tokens", 3, TEAL),
        ("Hindi / Amharic", "many tokens", 7, CORAL),
        ("Agglutinative\n(e.g. Hungarian)", "more pieces", 5, RGBColor(0xE9, 0xA8, 0x2C)),
    ]
    for i, (name, label, n, color) in enumerate(langs):
        left = Inches(0.7 + i * 4.1)
        _box(s, left, Inches(1.7), Inches(3.7), Inches(4.8), fill=CREAM)
        _txt(s, left + Inches(0.2), Inches(1.9), Inches(3.3), Inches(0.9), name, size=20, bold=True, color=NAVY, align=PP_ALIGN.CENTER)
        # token bars
        for j in range(n):
            bar = s.shapes.add_shape(
                MSO_SHAPE.ROUNDED_RECTANGLE,
                left + Inches(0.4),
                Inches(3.0 + j * 0.35),
                Inches(2.9),
                Inches(0.28),
            )
            _fill(bar, color)
        _txt(s, left + Inches(0.2), Inches(5.8), Inches(3.3), Inches(0.4), label, size=14, bold=True, color=color, align=PP_ALIGN.CENTER)
    _txt(s, Inches(0.7), Inches(6.7), Inches(12), Inches(0.4),
         "API cost, context window, and training budget all track token count — not characters.",
         size=14, color=MUTED)


def slide_flores_findings(prs):
    s = _blank(prs)
    _title_bar(s, "Our FLORES findings", "English-relative token premium on parallel text")
    fig = ROOT / "paper" / "figures" / "efficiency_token_premium_heatmap.png"
    if fig.exists():
        s.shapes.add_picture(str(fig), Inches(0.4), Inches(1.3), height=Inches(5.5))
    else:
        _txt(s, Inches(0.5), Inches(2), Inches(12), Inches(1), "heatmap missing", size=18, color=MUTED)
    callouts = [
        ("Target scripts", "Amharic, Odia,\ndialectal Arabic"),
        ("Controls", "Swahili, Hausa\n(Latin African)"),
        ("Signal", "Premium ≥ 2 on\n≥2 frontier BPEs"),
    ]
    for i, (h, d) in enumerate(callouts):
        top = Inches(1.5 + i * 1.7)
        _box(s, Inches(9.6), top, Inches(3.3), Inches(1.5), fill=CREAM)
        _txt(s, Inches(9.75), top + Inches(0.15), Inches(3.0), Inches(0.4), h, size=14, bold=True, color=CORAL)
        _txt(s, Inches(9.75), top + Inches(0.55), Inches(3.0), Inches(0.8), d, size=13, color=INK)


def slide_metrics_plain(prs):
    s = _blank(prs)
    _title_bar(s, "Three plain-language meters", "What the numbers mean")
    cards = [
        ("Token premium", "How many more tokens\nthan English for the\nsame meaning?", "1.0 = fair\n2.0 = 2× English cost", CORAL),
        ("Fertility", "How many tokens per\nword (or character\nunit)?", "Lower = packs more\nmeaning per token", TEAL),
        ("Bits / byte (BPB)", "How hard is the text\nto predict, per byte?", "Fairer than bits/token\nwhen tokens differ in length", BPE_C),
    ]
    for i, (title, q, note, color) in enumerate(cards):
        left = Inches(0.5 + i * 4.2)
        _box(s, left, Inches(1.6), Inches(3.9), Inches(5.0), fill=CREAM)
        accent = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, Inches(1.6), Inches(0.18), Inches(5.0))
        _fill(accent, color)
        _txt(s, left + Inches(0.4), Inches(1.9), Inches(3.3), Inches(0.5), title, size=22, bold=True, color=NAVY)
        _txt(s, left + Inches(0.4), Inches(2.7), Inches(3.3), Inches(1.6), q, size=16, color=INK)
        _txt(s, left + Inches(0.4), Inches(4.8), Inches(3.3), Inches(1.2), note, size=14, color=MUTED)


def slide_bpe_unfair(prs):
    s = _blank(prs)
    _title_bar(s, "Why BPE overcharges some languages", "Frequency + UTF-8 conspire")
    # Flow diagram
    steps = [
        ("Train on\nEnglish-heavy web", BPE_C),
        ("Merges favor\nfrequent Latin pieces", TEAL),
        ("Rare scripts stay\nas tiny fragments", CORAL),
    ]
    for i, (label, color) in enumerate(steps):
        left = Inches(0.6 + i * 4.2)
        _box(s, left, Inches(2.0), Inches(3.6), Inches(2.2), fill=color)
        _txt(s, left + Inches(0.2), Inches(2.5), Inches(3.2), Inches(1.2), label, size=18, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        if i < 2:
            _arrow(s, left + Inches(3.65), Inches(2.75), Inches(0.45), Inches(0.55), fill=MUTED)

    bullets = [
        "BPE learns what it sees often — English digraphs win the vocab lottery.",
        "UTF-8: non-Latin characters already cost more bytes before merges even start.",
        "Whitespace pretok keeps one token = one word-ish unit — no multi-word packing.",
    ]
    for i, b in enumerate(bullets):
        _txt(s, Inches(0.7), Inches(4.6 + i * 0.55), Inches(12), Inches(0.5), f"→  {b}", size=16, color=INK)


def slide_superbpe_mod(prs):
    s = _blank(prs)
    _title_bar(s, "SuperBPE: lift the word fence", "Liu et al., 2025")
    # Two stage diagram
    _box(s, Inches(0.5), Inches(1.6), Inches(5.8), Inches(4.8), fill=CREAM)
    _chip(s, Inches(2.1), Inches(1.85), Inches(2.6), Inches(0.55), "Stage 1 — ordinary BPE", BPE_C)
    _txt(s, Inches(0.8), Inches(2.7), Inches(5.2), Inches(1.2),
         "Whitespace-pretokenized\nLearn subwords inside words", size=16, color=INK, align=PP_ALIGN.CENTER)
    # example chips
    for i, t in enumerate(["of", "the", "United", "States"]):
        _chip(s, Inches(0.9 + i * 1.3), Inches(4.2), Inches(1.15), Inches(0.5), t, SOFT, INK)
    _txt(s, Inches(0.8), Inches(5.2), Inches(5.2), Inches(0.6), "4 tokens", size=14, bold=True, color=MUTED, align=PP_ALIGN.CENTER)

    _arrow(s, Inches(6.4), Inches(3.5), Inches(0.6), Inches(0.55), fill=CORAL)

    _box(s, Inches(7.1), Inches(1.6), Inches(5.8), Inches(4.8), fill=CREAM)
    _chip(s, Inches(8.5), Inches(1.85), Inches(3.0), Inches(0.55), "Stage 2 — superwords", CORAL)
    _txt(s, Inches(7.4), Inches(2.7), Inches(5.2), Inches(1.2),
         "Whitespace restriction lifted\nLearn multi-word tokens", size=16, color=INK, align=PP_ALIGN.CENTER)
    _chip(s, Inches(8.6), Inches(4.2), Inches(2.8), Inches(0.5), "of the United States", CORAL)
    _txt(s, Inches(7.4), Inches(5.2), Inches(5.2), Inches(0.6), "1 token  ·  same meaning", size=14, bold=True, color=CORAL, align=PP_ALIGN.CENTER)


def slide_matched_flores(prs):
    s = _blank(prs)
    _title_bar(s, "Matched BPE vs SuperBPE on FLORES", "Equal-byte 6-language train · same vocab size")
    fig = ROOT / "paper" / "figures" / "plan_a_flores_suite_summary.png"
    if fig.exists():
        s.shapes.add_picture(str(fig), Inches(0.3), Inches(1.25), height=Inches(5.6))
    # Side callouts
    _box(s, Inches(9.5), Inches(1.6), Inches(3.5), Inches(2.2), fill=CREAM)
    _txt(s, Inches(9.7), Inches(1.8), Inches(3.1), Inches(0.4), "Fertility ↓", size=18, bold=True, color=TEAL)
    _txt(s, Inches(9.7), Inches(2.4), Inches(3.1), Inches(1.1),
         "Fewer tokens/word for every whitespace language (Haitian, Hindi, …)", size=13, color=INK)

    _box(s, Inches(9.5), Inches(4.1), Inches(3.5), Inches(2.4), fill=CREAM)
    _txt(s, Inches(9.7), Inches(4.3), Inches(3.1), Inches(0.4), "Premium mixed", size=18, bold=True, color=CORAL)
    _txt(s, Inches(9.7), Inches(4.9), Inches(3.1), Inches(1.3),
         "Mandarin & Hungarian get worse vs English — choice is language-conditional", size=13, color=INK)


def slide_100m_setup(prs):
    s = _blank(prs)
    _title_bar(s, "Does it help language models?", "Phase 0 · 100M OLMo pilot")
    steps = [
        ("Data", "Equal-token FineWeb\n6 languages", BPE_C),
        ("Model", "olmo2_100M\nmatched steps", TEAL),
        ("Tokenizers", "gigatoken BPE\nsupergigatoken SuperBPE", CORAL),
        ("Readout", "bits/token\n+ approx BPB", RGBColor(0xE9, 0xA8, 0x2C)),
    ]
    for i, (h, d, c) in enumerate(steps):
        left = Inches(0.5 + i * 3.2)
        _box(s, left, Inches(2.2), Inches(2.95), Inches(3.2), fill=CREAM)
        _chip(s, left + Inches(0.55), Inches(2.5), Inches(1.85), Inches(0.55), h, c)
        _txt(s, left + Inches(0.2), Inches(3.4), Inches(2.55), Inches(1.5), d, size=15, color=INK, align=PP_ALIGN.CENTER)
        if i < 3:
            _arrow(s, left + Inches(2.95), Inches(3.5), Inches(0.3), Inches(0.4), fill=MUTED)
    _txt(s, Inches(0.5), Inches(5.8), Inches(12), Inches(0.8),
         "Caveat: equal-token matching + bits/token bias against longer SuperBPE tokens → we also report fertility-normalized approx BPB.",
         size=14, color=MUTED)


def slide_100m_results(prs):
    s = _blank(prs)
    _title_bar(s, "100M results — the gap shrinks when fair", "Raw bits/token vs fertility-normalized approx BPB")

    # Left: raw
    _box(s, Inches(0.4), Inches(1.5), Inches(6.1), Inches(5.2), fill=CREAM)
    _txt(s, Inches(0.7), Inches(1.75), Inches(5.5), Inches(0.4), "Raw bits / token", size=20, bold=True, color=NAVY)
    _txt(s, Inches(0.7), Inches(2.3), Inches(5.5), Inches(0.4), "Favors shorter tokens", size=13, color=MUTED)

    # bars
    _txt(s, Inches(0.9), Inches(3.1), Inches(1.5), Inches(0.4), "BPE", size=14, bold=True, color=BPE_C)
    bar1 = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(2.4), Inches(3.1), Inches(3.2), Inches(0.45))
    _fill(bar1, BPE_C)
    _txt(s, Inches(2.5), Inches(3.15), Inches(3.0), Inches(0.4), "5.45", size=16, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

    _txt(s, Inches(0.9), Inches(3.9), Inches(1.5), Inches(0.4), "SuperBPE", size=14, bold=True, color=CORAL)
    bar2 = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(2.4), Inches(3.9), Inches(3.7), Inches(0.45))
    _fill(bar2, CORAL)
    _txt(s, Inches(2.5), Inches(3.95), Inches(3.5), Inches(0.4), "6.29   (+0.84)", size=16, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

    _txt(s, Inches(0.7), Inches(5.0), Inches(5.5), Inches(1.2),
         "BPE wins on 5/6 languages.\nChinese ≈ tie.", size=15, color=INK)

    # Right: approx BPB
    _box(s, Inches(6.8), Inches(1.5), Inches(6.1), Inches(5.2), fill=CREAM)
    _txt(s, Inches(7.1), Inches(1.75), Inches(5.5), Inches(0.4), "Approx BPB (fairer)", size=20, bold=True, color=NAVY)
    _txt(s, Inches(7.1), Inches(2.3), Inches(5.5), Inches(0.4), "bits/token ÷ UTF-8 bytes/token", size=13, color=MUTED)

    _txt(s, Inches(7.3), Inches(3.1), Inches(1.5), Inches(0.4), "BPE", size=14, bold=True, color=BPE_C)
    bar3 = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.8), Inches(3.1), Inches(3.2), Inches(0.45))
    _fill(bar3, BPE_C)
    _txt(s, Inches(8.9), Inches(3.15), Inches(3.0), Inches(0.4), "1.061", size=16, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

    _txt(s, Inches(7.3), Inches(3.9), Inches(1.5), Inches(0.4), "SuperBPE", size=14, bold=True, color=CORAL)
    bar4 = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.8), Inches(3.9), Inches(3.35), Inches(0.45))
    _fill(bar4, CORAL)
    _txt(s, Inches(8.9), Inches(3.95), Inches(3.2), Inches(0.4), "1.085   (+0.025)", size=16, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

    _txt(s, Inches(7.1), Inches(5.0), Inches(5.5), Inches(1.2),
         "Gap mostly collapses.\nHaitian Creole: SuperBPE slightly better.", size=15, color=INK)


def slide_1b(prs):
    s = _blank(prs)
    _title_bar(s, "Next: 1B equal-bytes / equal-FLOPs", "True BPB — the decision metric")
    _box(s, Inches(0.5), Inches(1.7), Inches(12.3), Inches(2.0), fill=CREAM)
    _txt(s, Inches(0.8), Inches(2.0), Inches(11.7), Inches(0.5),
         "Phase 0 is a pilot — not a cancel signal.", size=22, bold=True, color=NAVY)
    _txt(s, Inches(0.8), Inches(2.7), Inches(11.7), Inches(0.6),
         "Raw bits/token looked bleak; fertility-normalized BPB says “keep going.”", size=16, color=INK)

    items = [
        ("Scale", "olmo2_1B · ~20B tokens"),
        ("Match", "Equal bytes → equal FLOPs"),
        ("Metric", "True UTF-8 BPB on val / FLORES"),
        ("Status", "Training in progress"),
    ]
    for i, (h, d) in enumerate(items):
        left = Inches(0.5 + i * 3.2)
        _box(s, left, Inches(4.2), Inches(3.0), Inches(2.0), fill=NAVY if i == 3 else CREAM)
        tc = WHITE if i == 3 else NAVY
        dc = RGBColor(0xC8, 0xD6, 0xE0) if i == 3 else MUTED
        _txt(s, left + Inches(0.2), Inches(4.4), Inches(2.6), Inches(0.4), h, size=16, bold=True, color=tc, align=PP_ALIGN.CENTER)
        _txt(s, left + Inches(0.2), Inches(5.0), Inches(2.6), Inches(0.8), d, size=14, color=dc, align=PP_ALIGN.CENTER)


def slide_sgt_methods(prs):
    s = _blank(prs)
    _title_bar(s, "supergigatoken — how we train & encode", "Rust fork of gigatoken · native SuperBPE")
    # Architecture diagram
    _box(s, Inches(0.4), Inches(1.5), Inches(4.0), Inches(5.2), fill=CREAM)
    _txt(s, Inches(0.6), Inches(1.7), Inches(3.6), Inches(0.4), "Trainers", size=18, bold=True, color=NAVY)
    _chip(s, Inches(0.7), Inches(2.4), Inches(3.4), Inches(0.7), "train_bpe  (gigatoken)", BPE_C)
    _chip(s, Inches(0.7), Inches(3.4), Inches(3.4), Inches(0.7), "train_superbpe  (fork)", CORAL)
    _txt(s, Inches(0.6), Inches(4.5), Inches(3.6), Inches(1.5),
         "Two-stage: subwords → superwords\nSame vocab target as BPE", size=14, color=MUTED)

    _box(s, Inches(4.7), Inches(1.5), Inches(4.0), Inches(5.2), fill=CREAM)
    _txt(s, Inches(4.9), Inches(1.7), Inches(3.6), Inches(0.4), "Encoder", size=18, bold=True, color=NAVY)
    _chip(s, Inches(5.0), Inches(2.4), Inches(3.4), Inches(0.7), "Level 1 · cached subwords", TEAL)
    _arrow(s, Inches(6.2), Inches(3.3), Inches(0.9), Inches(0.4), fill=MUTED)
    # rotate arrow visually by using down chevron via text
    _chip(s, Inches(5.0), Inches(3.9), Inches(3.4), Inches(0.7), "Level 2 · superword merges", CORAL)
    _txt(s, Inches(4.9), Inches(5.0), Inches(3.6), Inches(1.2),
         "Bit-identical to full byte merge\nRecovers most of BPE speed", size=14, color=MUTED)

    _box(s, Inches(9.0), Inches(1.5), Inches(4.0), Inches(5.2), fill=CREAM)
    _txt(s, Inches(9.2), Inches(1.7), Inches(3.6), Inches(0.4), "Eval suite", size=18, bold=True, color=NAVY)
    for i, t in enumerate(["Encoding efficiency", "Encoding throughput", "Trainer vs HF / original", "Vocab overlap (Jaccard)"]):
        _txt(s, Inches(9.3), Inches(2.5 + i * 0.7), Inches(3.5), Inches(0.5), f"•  {t}", size=14, color=INK)


def slide_sgt_efficiency(prs):
    s = _blank(prs)
    _title_bar(s, "Same vocab: ~21% fewer tokens", "50k SuperBPE vs 50k BPE · OpenWebText held-out")
    fig = SUPER / "assets" / "superbpe_efficiency.png"
    if fig.exists():
        s.shapes.add_picture(str(fig), Inches(0.3), Inches(1.2), height=Inches(5.6))
    _box(s, Inches(9.4), Inches(2.0), Inches(3.6), Inches(3.8), fill=CREAM)
    _txt(s, Inches(9.6), Inches(2.3), Inches(3.2), Inches(0.4), "Matched 50k", size=16, bold=True, color=NAVY)
    _txt(s, Inches(9.6), Inches(2.9), Inches(3.2), Inches(0.8), "SuperBPE  5.67 B/tok\nBPE           4.49 B/tok", size=14, color=INK)
    _txt(s, Inches(9.6), Inches(4.1), Inches(3.2), Inches(1.2),
         "→ 20.7% fewer tokens\nfor the same text", size=16, bold=True, color=CORAL)


def slide_sgt_speed(prs):
    s = _blank(prs)
    _title_bar(s, "Fast enough to ship", "Train & encode vs HuggingFace / original SuperBPE")

    nums = [
        ("8×", "faster SuperBPE train\nvs original impl", CORAL),
        ("116×", "faster SuperBPE encode\nvs HuggingFace", TEAL),
        ("3.8×", "faster plain BPE train\nvs HF BpeTrainer", BPE_C),
    ]
    for i, (n, d, c) in enumerate(nums):
        left = Inches(0.5 + i * 4.2)
        _box(s, left, Inches(1.5), Inches(3.9), Inches(2.6), fill=CREAM)
        _txt(s, left + Inches(0.2), Inches(1.75), Inches(3.5), Inches(1.0), n, size=44, bold=True, color=c, align=PP_ALIGN.CENTER)
        _txt(s, left + Inches(0.2), Inches(2.9), Inches(3.5), Inches(0.9), d, size=14, color=INK, align=PP_ALIGN.CENTER)

    fig = SUPER / "assets" / "superbpe_throughput.png"
    if fig.exists():
        s.shapes.add_picture(str(fig), Inches(1.5), Inches(4.35), height=Inches(2.85))
    else:
        _txt(s, Inches(0.5), Inches(5.0), Inches(12), Inches(0.5),
             "Encode: SuperBPE 730 MB/s · plain BPE 2297 MB/s", size=14, color=MUTED, align=PP_ALIGN.CENTER)


def slide_takeaways(prs):
    s = _blank(prs)
    _title_bar(s, "Takeaways", "")
    items = [
        ("1", "Languages pay unequal token taxes under frontier BPEs.", CORAL),
        ("2", "SuperBPE packs more text per token — but not uniformly fairer.", TEAL),
        ("3", "100M: raw bits/token scared us; approx BPB mostly closed the gap.", BPE_C),
        ("4", "1B equal-FLOPs BPB is the real go/no-go — running now.", NAVY),
    ]
    for i, (n, t, c) in enumerate(items):
        top = Inches(1.5 + i * 1.25)
        _chip(s, Inches(0.6), top, Inches(0.7), Inches(0.7), n, c)
        _box(s, Inches(1.6), top, Inches(11.0), Inches(1.0), fill=CREAM)
        _txt(s, Inches(1.9), top + Inches(0.25), Inches(10.5), Inches(0.55), t, size=18, color=INK)


def slide_bib(prs):
    s = _blank(prs)
    _title_bar(s, "Bibliography", "Key references")
    refs = [
        "Liu et al. (2025). SuperBPE: Space Travel for Language Models. arXiv:2503.13423",
        "Arnett & Bergen (2025). Why do language models perform worse for morphologically complex languages? / token premiums on FLORES.",
        "Goyal et al. (2022); NLLB (2022). FLORES-200 parallel evaluation.",
        "Penedo et al. (2024/2025). FineWeb / FineWeb-2 web corpora.",
        "Chowdhury & Woolf (2026). Benchmarking SuperBPE (BPB evidence on Mandarin/Hungarian).",
        "gigatoken (Roed et al.) — fast Rust BPE; supergigatoken — SuperBPE fork (this work).",
        "OLMo / OLMo-core (Ai2) — training stack for Phase 0 / Plan B.",
    ]
    for i, r in enumerate(refs):
        _txt(s, Inches(0.6), Inches(1.4 + i * 0.7), Inches(12.2), Inches(0.65), f"[{i+1}]  {r}", size=13, color=INK)


def main():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    slide_title(prs)
    slide_agenda(prs)
    slide_fertility_problem(prs)
    slide_flores_findings(prs)
    slide_metrics_plain(prs)
    slide_bpe_unfair(prs)
    slide_superbpe_mod(prs)
    slide_matched_flores(prs)
    slide_sgt_methods(prs)
    slide_sgt_efficiency(prs)
    slide_sgt_speed(prs)
    slide_100m_setup(prs)
    slide_100m_results(prs)
    slide_1b(prs)
    slide_takeaways(prs)
    slide_bib(prs)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(OUT))
    print(f"Wrote {OUT} ({len(prs.slides)} slides)")


if __name__ == "__main__":
    main()
