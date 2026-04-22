#!/usr/bin/env python3
"""
Chapter quality checker for fiction writing pipeline.
Extends check_wordcount.py with em-dash density + English leakage scanning.
Minimal, zero-dependency (stdlib only), sandbox-safe.

Usage:
  python check_chapter_quality.py <file> [--min-words N] [--max-em-dash-density N] [--lang auto|zh|en]

Output (JSON):
  {
    "file": "chapter.md",
    "word_count": {"count": 3200, "lang": "zh", "min": 3000, "pass": true},
    "em_dash": {"count": 12, "density": 4.0, "max_density": 5, "pass": true},
    "english_leakage": {"words": [], "count": 0, "pass": true},
    "overall": "PASS"
  }

Exit code: 0 = all PASS, 1 = any FAIL/error.
"""

import json
import re
import sys
from pathlib import Path


# ── Text processing (reused from check_wordcount.py) ──────────────────

def strip_markdown(text: str) -> str:
    """Strip markdown syntax, keep prose only."""
    text = re.sub(r'#{1,6}\s+', '', text)                       # headings
    text = re.sub(r'\*{1,3}(.*?)\*{1,3}', r'\1', text)         # bold/italic
    text = re.sub(r'~~(.*?)~~', r'\1', text)                    # strikethrough
    text = re.sub(r'`{1,3}[^`]*`{1,3}', '', text, flags=re.S)  # code spans/blocks
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)             # links
    text = re.sub(r'^\s*[-*+>]\s', '', text, flags=re.M)       # list/blockquote markers
    text = re.sub(r'^\s*\d+\.\s', '', text, flags=re.M)        # ordered lists
    text = re.sub(r'\|[^\n]*\|', '', text)                      # tables
    text = re.sub(r'-{3,}', '', text)                           # horizontal rules
    return text


def count_zh(text: str) -> int:
    """Count CJK characters (Unified Ideographs + Extension A)."""
    return len(re.findall(r'[\u4e00-\u9fff\u3400-\u4dbf]', text))


def count_en(text: str) -> int:
    """Count English words (tokens containing a letter)."""
    return sum(1 for t in text.split() if re.search(r'[a-zA-Z]', t))


def detect_lang(text: str) -> str:
    return 'zh' if count_zh(text) > count_en(text) else 'en'


# ── Quality checks ────────────────────────────────────────────────────

def count_em_dash(text: str) -> int:
    """Count em-dash '——' occurrences in text."""
    return text.count("——")


def calc_em_dash_density(em_dash_count: int, zh_char_count: int) -> float:
    """Calculate em-dash density per 1000 Chinese chars."""
    if zh_char_count == 0:
        return 0.0
    return em_dash_count / (zh_char_count / 1000)


def scan_english_leakage(text: str) -> list:
    """Find isolated English words (>=3 letters) embedded in Chinese prose.

    Common Claude artifacts: 'additional', 'beige', 'handwriting', 'scheme'.
    Only matches words surrounded by Chinese characters (not in headers, code, etc.).
    """
    # Match English words (3+ letters) that appear between CJK characters
    matches = re.findall(
        r'(?<=[\u4e00-\u9fff\u3400-\u4dbf])\s*([a-zA-Z]{3,})\s*(?=[\u4e00-\u9fff\u3400-\u4dbf])',
        text
    )
    # Filter out common false positives (units, abbreviations commonly used in Chinese)
    false_positives = {'app', 'APP', 'DNA', 'GPS', 'CEO', 'pdf', 'PDF', 'USB', 'wifi', 'WiFi'}
    return [w for w in matches if w not in false_positives and not w.isupper()]


# ── Main ──────────────────────────────────────────────────────────────

def check_file(file_path: str, min_words: int = 3000, max_em_dash_density: float = 5.0, lang: str = 'auto') -> dict:
    """Run all quality checks on a single file. Returns result dict."""
    path = Path(file_path)
    if not path.exists():
        return {
            "file": file_path,
            "error": f"file not found: {file_path}",
            "overall": "ERROR",
        }

    raw_text = path.read_text(encoding='utf-8')
    text = strip_markdown(raw_text)

    if lang == 'auto':
        lang = detect_lang(text)

    # Word count
    wc = count_zh(text) if lang == 'zh' else count_en(text)
    wc_pass = wc >= min_words

    # Em-dash density (always uses raw text — markdown stripping shouldn't affect "——")
    em_count = count_em_dash(raw_text)
    zh_chars = count_zh(raw_text)
    density = calc_em_dash_density(em_count, zh_chars)
    em_pass = density <= max_em_dash_density

    # English leakage (only meaningful for Chinese text)
    eng_words = scan_english_leakage(raw_text) if lang == 'zh' else []
    eng_pass = len(eng_words) == 0

    overall = "PASS" if (wc_pass and em_pass and eng_pass) else "FAIL"

    return {
        "file": file_path,
        "word_count": {
            "count": wc,
            "lang": lang,
            "min": min_words,
            "pass": wc_pass,
        },
        "em_dash": {
            "count": em_count,
            "density": round(density, 1),
            "max_density": max_em_dash_density,
            "pass": em_pass,
        },
        "english_leakage": {
            "words": eng_words[:20],  # cap at 20 to avoid huge output
            "count": len(eng_words),
            "pass": eng_pass,
        },
        "overall": overall,
    }


def main():
    args = sys.argv[1:]
    if not args or args[0] in ('-h', '--help'):
        print(__doc__.strip())
        sys.exit(0)

    file_path = args[0]
    min_words = 3000
    max_em_dash_density = 5.0
    lang = 'auto'

    # Simple flag parsing — no argparse needed
    i = 1
    while i < len(args):
        if args[i] == '--min-words' and i + 1 < len(args):
            min_words = int(args[i + 1]); i += 2
        elif args[i] == '--max-em-dash-density' and i + 1 < len(args):
            max_em_dash_density = float(args[i + 1]); i += 2
        elif args[i] == '--lang' and i + 1 < len(args):
            lang = args[i + 1]; i += 2
        else:
            i += 1

    result = check_file(file_path, min_words, max_em_dash_density, lang)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result["overall"] == "PASS" else 1)


if __name__ == '__main__':
    main()
