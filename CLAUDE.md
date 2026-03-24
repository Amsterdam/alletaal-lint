# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

Simplified Dutch text readability assessment tool based on the LiNT (Leesbaarheidsinstrument voor Nederlandse Teksten) methodology. Scores Dutch text on a 0-100 scale (higher = more readable) using three active linguistic features: word frequency, syntactic complexity (dependency distance), and content word density. The fourth LiNT feature (concrete noun proportion) is not implemented — see "T-Scan Comparison" below. Requires spaCy Dutch model `nl_core_news_sm`.

## Commands

```bash
# Setup (one command)
make setup                    # installs package, dev deps, and spaCy model

# Tests
pytest tests/ -v                              # all tests
pytest tests/test_core.py -v                  # single file
pytest tests/test_core.py::TestSentence -v    # single class

# Code quality
make lint          # flake8 + black --check + isort --check
make format        # black + isort
make type-check    # mypy src/alletaal_lint/
make check         # lint + type-check + test

# Run
alletaal-lint sentence "De kat zit op de mat."
alletaal-lint score --text "Dutch text" --format json --detailed
alletaal-lint server --host 0.0.0.0 --port 8000
alletaal-lint openapi --output openapi.json
```

## Architecture

```
src/alletaal_lint/
├── core.py    # Scoring engine — WordStats, LintScorer, Sentence, Document
├── api.py     # FastAPI REST API (factory: create_app())
├── cli.py     # Typer CLI (commands: score, sentence, server, openapi, install-model, version)
└── __init__.py
```

**Core scoring pipeline** (`core.py`):
- `WordStats` — wraps a spaCy token, extracts POS, morphology, dependency distance, word frequency (via `wordfreq` zipf scale)
- `Sentence` — processes text through spaCy, computes LiNT features, calculates score
- `Document` — splits text into sentences via spaCy's sentence tokenizer, averages sentence scores
- `LintScorer` — static methods for the LiNT formula and difficulty level mapping

**LiNT formula**:
```
raw = 3.204 + (15.845 × freq_log) - (1.331 × max_dep) - (3.829 × content_words) + (13.096 × concrete_nouns)
final = clamp(100 - raw, 0, 100)
```
Note: `concrete_nouns` always returns 0.0 (see T-Scan Comparison below).

**API** (`api.py`): Strips markdown from input before scoring. Endpoints: `/score-sentence`, `/score-document`, `/analyze-document`, `/health`, `/methodology`. Docs at `/docs`. OpenAPI spec available at root as `openapi.json`.

**CLI** (`cli.py`): Rich table and JSON output. The `server` command launches uvicorn. The `openapi` command exports the OpenAPI spec.

## Testing

Tests use `pytest` with `--cov=alletaal_lint` (configured in `pyproject.toml`). API tests use `FastAPI.TestClient` (requires `httpx`). CLI tests use `typer.testing.CliRunner`. All tests require the spaCy model to be installed.

## Code Style

- **black** (line-length 88), **isort** (profile: black), **flake8**, **mypy** (strict mode in CI)
- Python 3.10+ compatibility required

## Scoring Direction

Higher score = more readable. Difficulty levels: **1 = easy** (score > 61.5), **4 = very difficult** (score <= 36). The `100 - raw` inversion is deliberate — the raw formula produces higher values for easier text, so the inversion maps to a 0-100 readability scale.

## T-Scan Comparison

This tool is a **deliberate simplification** of [T-Scan](https://github.com/CentreForDigitalHumanities/tscan). The formula coefficients are identical to T-Scan's `lint_score_2`, but feature extraction differs:

| Feature | alletaal-lint | T-Scan | Impact |
|---------|--------------|--------|--------|
| Word frequency | `wordfreq` (zipf scale) | `log10(freq/billion)` from SUBTLEX-NL | Different scale ranges |
| Dependency distance | spaCy neural parser | Alpino rule-based parser | Different parse trees |
| Content word density | Per-sentence (clause count = 1) | Per-clause with full clause detection | Overestimates for multi-clause sentences |
| Concrete nouns | **Not implemented** (returns 0.0) | Cornetto semantic lexicon | Formula term zeroed out |
| Difficulty thresholds | 36 / 51 / 61.5 | 34 / 46 / 60 | Minor, design choice |

**Scores are not directly comparable to T-Scan.** This is by design — the goal is a practical, easy-to-integrate readability tool, not a 1:1 T-Scan port.
