#!/usr/bin/env python3
"""Extract plain text from a PDF, page by page.

Used by ``fetch_paper.py`` and also runnable standalone:

    python scripts/pdf_extract.py paper.pdf --out paper.txt

Extraction relies on pypdf and is intentionally lightweight. Formulas,
tables, and figures are NOT reliably extracted; the output carries explicit
warnings instead of pretending otherwise.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from pathlib import Path

try:
    from pypdf import PdfReader
except ImportError:
    sys.exit("error: pypdf is not installed. Run: pip install -r requirements.txt")

HEADER_NOTE = (
    "[NOTE: Text extracted with pypdf. Formula/table/figure extraction may be "
    "incomplete. Verify critical details against the original PDF.]"
)

# Pages yielding fewer characters than this are flagged as suspicious.
MIN_PAGE_CHARS = 20


@dataclass
class ExtractionResult:
    """Page-by-page extraction output."""

    text: str
    warnings: list[str] = field(default_factory=list)
    num_pages: int = 0


def extract_pdf_pages(pdf_path: Path) -> ExtractionResult:
    """Extract text from every page of *pdf_path*.

    The returned ``text`` uses the format::

        === Page 1 ===
        ...

        === Page 2 ===
        ...

    Pages with no (or almost no) extractable text produce an inline
    ``[WARNING: ...]`` line and an entry in ``warnings``.

    Raises:
        FileNotFoundError: if *pdf_path* does not exist.
        ValueError: if the file cannot be opened as a PDF.
    """
    if not pdf_path.is_file():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    try:
        reader = PdfReader(str(pdf_path))
    except Exception as exc:
        raise ValueError(f"Could not open '{pdf_path}' as a PDF: {exc}") from exc

    if reader.is_encrypted:
        try:
            reader.decrypt("")
        except Exception as exc:
            raise ValueError(
                f"'{pdf_path}' is encrypted and could not be opened: {exc}"
            ) from exc

    warnings: list[str] = []
    parts: list[str] = [HEADER_NOTE, ""]

    for page_num, page in enumerate(reader.pages, start=1):
        parts.append(f"=== Page {page_num} ===")
        try:
            page_text = (page.extract_text() or "").strip()
        except Exception as exc:
            page_text = ""
            warnings.append(f"Page {page_num}: text extraction failed ({exc}).")

        if len(page_text) < MIN_PAGE_CHARS:
            message = (
                f"Page {page_num}: little or no extractable text "
                f"({len(page_text)} chars). The page may be scanned, image-only, "
                "or heavy on figures/formulas."
            )
            warnings.append(message)
            parts.append(f"[WARNING: {message}]")

        if page_text:
            parts.append(page_text)
        parts.append("")

    return ExtractionResult(
        text="\n".join(parts),
        warnings=warnings,
        num_pages=len(reader.pages),
    )


def extract_pdf_text(pdf_path: Path) -> str:
    """Convenience wrapper returning only the extracted text."""
    return extract_pdf_pages(pdf_path).text


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Extract plain text from a PDF, page by page."
    )
    parser.add_argument("pdf", type=Path, help="Path to the PDF file.")
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Write text to this file instead of stdout.",
    )
    args = parser.parse_args(argv)

    try:
        result = extract_pdf_pages(args.pdf)
    except (FileNotFoundError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    for warning in result.warnings:
        print(f"warning: {warning}", file=sys.stderr)

    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(result.text, encoding="utf-8")
        print(f"Wrote {result.num_pages} page(s) to {args.out}")
    else:
        print(result.text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
