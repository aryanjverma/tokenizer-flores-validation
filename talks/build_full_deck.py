"""One copy-paste-ready deck: fertility intro + all charts + bibliography."""

from __future__ import annotations

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Inches, Pt

ASSETS = Path(__file__).resolve().parent / "slide_assets"
USER_IMG = Path(
    r"C:\Users\aryan\.cursor\projects\c-Users-aryan-projects-edullm-data"
    r"\assets\c__Users_aryan_AppData_Roaming_Cursor_User_workspaceStorage_"
    r"empty-window_images_image-8596a6e0-25f7-4b4b-a333-1910b497c5aa.png"
)
# fallback shorter path if copied
USER_IMG_LOCAL = ASSETS / "token_tax_fertility_accuracy.png"
OUT = Path(__file__).resolve().parent / "tokenizer_fairness_full.pptx"

NAVY = RGBColor(0x0F, 0x2A, 0x44)
INK = RGBColor(0x1A, 0x1A, 0x1A)
MUTED = RGBColor(0x5A, 0x67, 0x72)
CORAL = RGBColor(0xE0, 0x6C, 0x4F)
CREAM = RGBColor(0xF7, 0xF4, 0xEF)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
SOFT = RGBColor(0xE8, 0xEE, 0xF2)


def _fill(shape, color):
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()


def _run(p, text, size=16, bold=False, color=INK, italic=False):
    r = p.add_run()
    r.text = text
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.italic = italic
    r.font.color.rgb = color
    r.font.name = "Calibri"
    return r


def _txt(slide, left, top, width, height, text, size=16, bold=False, color=INK,
         align=PP_ALIGN.LEFT, italic=False):
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    _run(p, text, size=size, bold=bold, color=color, italic=italic)
    return box


def _title_bar(slide, title, subtitle=None):
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(0.9))
    _fill(bar, NAVY)
    _txt(slide, Inches(0.45), Inches(0.22), Inches(12.4), Inches(0.5),
         title, size=26, bold=True, color=WHITE)
    if subtitle:
        _txt(slide, Inches(0.45), Inches(0.98), Inches(12.4), Inches(0.35),
             subtitle, size=14, color=MUTED)


def _blank(prs):
    return prs.slides.add_slide(prs.slide_layouts[6])


def _fit_picture(slide, path, left, top, max_w, max_h):
    """Place picture fitting inside box, preserving aspect ratio."""
    from PIL import Image

    with Image.open(path) as im:
        w, h = im.size
    aspect = w / h
    box_aspect = max_w / max_h
    if aspect > box_aspect:
        pw, ph = max_w, max_w / aspect
    else:
        ph, pw = max_h, max_h * aspect
    # center in box
    left_c = left + (max_w - pw) / 2
    top_c = top + (max_h - ph) / 2
    return slide.shapes.add_picture(str(path), int(left_c), int(top_c), int(pw), int(ph))


def slide_title(prs):
    s = _blank(prs)
    bg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    _fill(bg, NAVY)
    _txt(s, Inches(0.7), Inches(2.2), Inches(12), Inches(1.0),
         "Token fertility, SuperBPE, and the token tax",
         size=34, bold=True, color=WHITE)
    _txt(s, Inches(0.7), Inches(3.4), Inches(12), Inches(0.6),
         "Why some languages pay more tokens for the same meaning",
         size=20, color=RGBColor(0xC8, 0xD6, 0xE0))
    _txt(s, Inches(0.7), Inches(5.8), Inches(12), Inches(0.4),
         "Aryan Verma  ·  Frank Gonzalez", size=16, color=RGBColor(0xC8, 0xD6, 0xE0))


def slide_fertility_intro(prs, quote_img: Path):
    s = _blank(prs)
    _title_bar(s, "What is token fertility?", "Tokens per word — higher means more fragmentation")

    # definition card
    card = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.4), Inches(1.15), Inches(12.5), Inches(1.35))
    _fill(card, CREAM)
    _txt(s, Inches(0.65), Inches(1.3), Inches(12), Inches(0.4),
         "Fertility = (number of tokens) / (number of words)",
         size=20, bold=True, color=NAVY)
    _txt(s, Inches(0.65), Inches(1.8), Inches(12), Inches(0.5),
         "Same meaning, more tokens → higher API cost, less context, harder modeling.",
         size=15, color=INK)

    # quote
    qbox = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.4), Inches(2.7), Inches(12.5), Inches(1.35))
    _fill(qbox, SOFT)
    accent = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.4), Inches(2.7), Inches(0.12), Inches(1.35))
    _fill(accent, CORAL)
    _txt(s, Inches(0.75), Inches(2.85), Inches(11.9), Inches(0.9),
         '"Tokenization inefficiency imposes structural disadvantages on morphologically '
         'complex, low-resource languages, inflating compute resources and depressing accuracy."',
         size=14, italic=True, color=INK)
    _txt(s, Inches(0.75), Inches(3.65), Inches(11.9), Inches(0.3),
         "— Lundin et al., The Token Tax (arXiv:2509.05486)",
         size=12, color=MUTED)

    # figure
    if quote_img.exists():
        _fit_picture(s, quote_img, Inches(0.35), Inches(4.2), Inches(12.6), Inches(3.1))
    _txt(s, Inches(0.4), Inches(7.15), Inches(12.5), Inches(0.3),
         "Higher fertility → lower accuracy across AfriMMLU subjects (Lundin et al., 2025).",
         size=11, color=MUTED, align=PP_ALIGN.CENTER)


def slide_image(prs, title, subtitle, path: Path, caption=None):
    s = _blank(prs)
    _title_bar(s, title, subtitle)
    if path.exists():
        _fit_picture(s, path, Inches(0.35), Inches(1.25), Inches(12.6), Inches(5.7))
    else:
        _txt(s, Inches(1), Inches(3), Inches(11), Inches(1), f"Missing: {path.name}", size=18, color=CORAL)
    if caption:
        _txt(s, Inches(0.4), Inches(7.05), Inches(12.5), Inches(0.35),
             caption, size=11, color=MUTED, align=PP_ALIGN.CENTER)


def slide_two_images(prs, title, subtitle, left_path, right_path, left_cap="", right_cap=""):
    s = _blank(prs)
    _title_bar(s, title, subtitle)
    if left_path.exists():
        _fit_picture(s, left_path, Inches(0.25), Inches(1.3), Inches(6.3), Inches(5.5))
    if right_path.exists():
        _fit_picture(s, right_path, Inches(6.7), Inches(1.3), Inches(6.3), Inches(5.5))
    if left_cap or right_cap:
        _txt(s, Inches(0.3), Inches(6.95), Inches(6.2), Inches(0.35), left_cap, size=11, color=MUTED, align=PP_ALIGN.CENTER)
        _txt(s, Inches(6.75), Inches(6.95), Inches(6.2), Inches(0.35), right_cap, size=11, color=MUTED, align=PP_ALIGN.CENTER)


def slide_bib(prs):
    s = _blank(prs)
    _title_bar(s, "Bibliography", "Papers cited in this talk")
    refs = [
        ("Lundin et al. (2025)",
         "The Token Tax: Systematic Bias in Multilingual Tokenization.",
         "https://arxiv.org/abs/2509.05486"),
        ("Petrov et al. (2023)",
         "Language Model Tokenizers Introduce Unfairness Between Languages. NeurIPS 2023.",
         "https://arxiv.org/abs/2305.15425"),
        ("Somide (2026)",
         "The African Language Tax.",
         "https://arxiv.org/abs/2606.24460"),
        ("Arnett, Chang, Biderman, Bergen (2025)",
         "Explaining and Mitigating Crosslingual Tokenizer Inequities.",
         "https://arxiv.org/abs/2510.21909"),
        ("Nayeem et al. (2025)",
         "Beyond Fertility: Analyzing STRR as a Metric for Multilingual Tokenization Evaluation.",
         "https://arxiv.org/abs/2510.09947"),
        ("Liu et al. (2025)",
         "SuperBPE: Space Travel for Language Models.",
         "https://arxiv.org/abs/2503.13423"),
    ]
    for i, (authors, title, url) in enumerate(refs):
        top = Inches(1.2 + i * 0.95)
        num = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(0.45), top + Inches(0.1), Inches(0.45), Inches(0.45))
        _fill(num, CORAL if i == 0 else NAVY)
        tf = num.text_frame
        tf.paragraphs[0].alignment = PP_ALIGN.CENTER
        _run(tf.paragraphs[0], str(i + 1), size=12, bold=True, color=WHITE)
        _txt(s, Inches(1.1), top, Inches(11.7), Inches(0.35), authors, size=14, bold=True, color=NAVY)
        _txt(s, Inches(1.1), top + Inches(0.3), Inches(11.7), Inches(0.3), title, size=13, color=INK)
        _txt(s, Inches(1.1), top + Inches(0.55), Inches(11.7), Inches(0.28), url, size=11, color=MUTED)


def main():
    # ensure quote figure is in assets
    if USER_IMG.exists() and not USER_IMG_LOCAL.exists():
        USER_IMG_LOCAL.write_bytes(USER_IMG.read_bytes())
    quote_img = USER_IMG_LOCAL if USER_IMG_LOCAL.exists() else USER_IMG

    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    slide_title(prs)
    slide_fertility_intro(prs, quote_img)

    slide_image(
        prs,
        "Our fertility results — BPE vs SuperBPE",
        "FLORES-200 · matched equal-byte 6-language tokenizers · lower is better",
        ASSETS / "fertility_bpe_vs_superbpe.png",
    )
    slide_image(
        prs,
        "STRR — single-token retention rate",
        "Share of whitespace words encoded as exactly one token · higher is better",
        ASSETS / "strr_bpe_vs_superbpe.png",
        caption="Metric from Nayeem et al. (arXiv:2510.09947). Mandarin omitted (whitespace words N/A).",
    )
    slide_image(
        prs,
        "English-relative token premium",
        "tokens_ℓ / tokens_English on parallel FLORES text · lower is fairer",
        ASSETS / "token_premium_bpe_vs_superbpe.png",
    )
    slide_image(
        prs,
        "BPE training time on supergigatoken",
        "50k vocab · 100 MB OpenWebText · train_bpe vs HuggingFace BpeTrainer",
        ASSETS / "bpe_train_time_supergigatoken.png",
    )
    slide_two_images(
        prs,
        "Phase 0 LM eval — bits/token and approx BPB",
        "olmo2_100M @ step7629 · lower is better · bold in table = better arm",
        ASSETS / "table_bits_per_token.png",
        ASSETS / "table_approx_bpb.png",
        "Bits / token",
        "Approx BPB (fertility-normalized)",
    )
    # also full-bleed versions for easy reading
    slide_image(prs, "Table — bits/token by language", "Phase 0 · BPE vs SuperBPE", ASSETS / "table_bits_per_token.png")
    slide_image(prs, "Table — approx BPB by language", "bits/token ÷ FLORES UTF-8 bytes/token", ASSETS / "table_approx_bpb.png")
    slide_bib(prs)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(OUT))
    print(f"Wrote {OUT} ({len(prs.slides)} slides)")


if __name__ == "__main__":
    main()
