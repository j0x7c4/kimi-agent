#!/usr/bin/env python3
"""
Word count checker for general-writing skills.
Minimal, zero-dependency (stdlib only), sandbox-safe.

Usage:
  python check_wordcount.py <file> [--min N] [--lang zh|en|auto]

Output (single line, machine-readable):
  PASS 3200 zh chars
  FAIL 2800 zh chars (min: 3000)

Exit code: 0 = PASS, 1 = FAIL/error.
"""

import re
import sys
from pathlib import Path


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


def main():
    args = sys.argv[1:]
    if not args or args[0] in ('-h', '--help'):
        print(__doc__.strip())
        sys.exit(0)

    file_path = args[0]
    min_words = 3000
    lang = 'auto'

    # simple flag parsing — no argparse needed
    i = 1
    while i < len(args):
        if args[i] == '--min' and i + 1 < len(args):
            min_words = int(args[i + 1]); i += 2
        elif args[i] == '--lang' and i + 1 < len(args):
            lang = args[i + 1]; i += 2
        else:
            i += 1

    path = Path(file_path)
    if not path.exists():
        print(f'ERROR file not found: {file_path}')
        sys.exit(1)

    text = strip_markdown(path.read_text(encoding='utf-8'))

    if lang == 'auto':
        lang = detect_lang(text)

    count = count_zh(text) if lang == 'zh' else count_en(text)
    unit = 'chars' if lang == 'zh' else 'words'

    if count >= min_words:
        print(f'PASS {count} {lang} {unit}')
        sys.exit(0)
    else:
        print(f'FAIL {count} {lang} {unit} (min: {min_words})')
        sys.exit(1)


if __name__ == '__main__':
    main()
