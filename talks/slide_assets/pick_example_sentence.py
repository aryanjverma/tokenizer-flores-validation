from pathlib import Path
import sys

from tokenizers import Tokenizer

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.load_flores import load_flores_sentences

roots = [
    Path(r"c:\Users\aryan\projects\tokenizer-flores-validation\artifacts\plan_a\scale\tokenizers\bpe"),
    Path(r"c:\Users\aryan\projects\edullm-data\artifacts\public\gigatoken-bpe\files"),
]
tok_path = next(r / "tokenizer.json" for r in roots if (r / "tokenizer.json").exists())
print("tokenizer:", tok_path)
tok = Tokenizer.from_file(str(tok_path))

data = load_flores_sentences(["eng_Latn", "hin_Deva", "hun_Latn"], "devtest")
eng, hin, hun = data["eng_Latn"], data["hin_Deva"], data["hun_Latn"]

candidates = []
for i, (e, h, u) in enumerate(zip(eng, hin, hun)):
    te, th, tu = tok.encode(e), tok.encode(h), tok.encode(u)
    if not (6 <= len(te.ids) <= 18):
        continue
    if len(e) > 120:
        continue
    # want clear inflation
    if len(th.ids) < len(te.ids) * 1.05 and len(tu.ids) < len(te.ids) * 1.05:
        continue
    score = (len(th.ids) / len(te.ids)) + (len(tu.ids) / len(te.ids))
    # prefer readable, not too many tokens overall
    if max(len(th.ids), len(tu.ids)) > 40:
        continue
    candidates.append((score, -len(te.ids), i, e, h, u, te.tokens, th.tokens, tu.tokens))

candidates.sort(reverse=True)
for rank, c in enumerate(candidates[:8]):
    score, _, i, e, h, u, te, th, tu = c
    print(f"\n#{rank} idx={i} score={score:.2f} n=({len(te)},{len(th)},{len(tu)})")
    print("ENG:", e)
    print("  ", te)
    print("HIN:", h)
    print("  ", th)
    print("HUN:", u)
    print("  ", tu)
