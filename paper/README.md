# Multilingual Token-Tax Paper

LangMAP-style manuscript reporting Study A (frontier FLORES token tax),
Study B (equal-byte SuperBPE vs BPE), and Study C (Phase 0 100M LM pilot +
deferred 1B UniMax BPB placeholders).

**1B training handoff:** see [`../HANDOFF_1B.md`](../HANDOFF_1B.md) (points at `edullm-data` branch `handoff/plan-b-1b`).

## Deliverable

- [`main.pdf`](main.pdf) — compiled paper
- [`main.tex`](main.tex) — source
- [`references.bib`](references.bib) — bibliography
- [`figures/`](figures/) — plots copied from `../Results/figures/`

## Build

Place a `tectonic` binary on `PATH`, or download the Windows release into
`tools/tectonic.exe` (gitignored), then:

```powershell
cd paper
.\tools\tectonic.exe -X compile main.tex
# or: latexmk -pdf main.tex
```
