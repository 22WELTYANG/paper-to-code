#!/usr/bin/env python3
"""Fetch a paper (arXiv URL, arXiv ID, or local PDF) and extract its text.

Writes into the --out directory:

    paper.pdf       the source PDF
    paper.txt       page-by-page extracted text
    metadata.json   provenance and extraction info

Usage:

    python scripts/fetch_paper.py 1706.03762 --out runs/1706.03762
    python scripts/fetch_paper.py https://arxiv.org/abs/1706.03762 --out runs/transformer
    python scripts/fetch_paper.py papers/example.pdf --out runs/example
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

try:
    import requests
except ImportError:
    sys.exit("error: requests is not installed. Run: pip install -r requirements.txt")

# Allow running both as `python scripts/fetch_paper.py` (any cwd) and from
# inside scripts/.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from pdf_extract import ExtractionResult, extract_pdf_pages  # noqa: E402

# New-style ID: 1706.03762, 2401.12345v2
ARXIV_NEW_ID = re.compile(r"^(?P<id>\d{4}\.\d{4,5})(?P<ver>v\d+)?$")
# Old-style ID: cs/0301012, math.GT/0309136v1
ARXIV_OLD_ID = re.compile(r"^(?P<id>[a-z][a-z-]*(?:\.[A-Z]{2})?/\d{7})(?P<ver>v\d+)?$")

USER_AGENT = "paper-to-code/0.1 (https://github.com/22WELTYANG/paper-to-code)"
DOWNLOAD_TIMEOUT_SECONDS = 60

INPUT_HELP = (
    "Accepted inputs:\n"
    "  - arXiv ID:   1706.03762  |  2401.12345v2  |  cs/0301012\n"
    "  - arXiv URL:  https://arxiv.org/abs/1706.03762  |  https://arxiv.org/pdf/1706.03762\n"
    "  - local PDF:  papers/example.pdf"
)


@dataclass
class ResolvedInput:
    """Classified user input."""

    source_type: str  # "arxiv_id" | "arxiv_url" | "local_pdf"
    arxiv_id: str | None
    local_path: Path | None


def normalize_arxiv_id(candidate: str) -> str | None:
    """Return a normalized arXiv ID (version kept if present), else None."""
    candidate = candidate.strip()
    for pattern in (ARXIV_NEW_ID, ARXIV_OLD_ID):
        match = pattern.match(candidate)
        if match:
            return match.group("id") + (match.group("ver") or "")
    return None


def arxiv_id_from_url(url: str) -> str | None:
    """Extract an arXiv ID from an arxiv.org /abs/ or /pdf/ URL, else None."""
    parsed = urlparse(url)
    host = parsed.netloc.lower()
    if host != "arxiv.org" and not host.endswith(".arxiv.org"):
        return None
    path = parsed.path.strip("/")
    for prefix in ("abs/", "pdf/"):
        if path.startswith(prefix):
            candidate = path[len(prefix):]
            if candidate.lower().endswith(".pdf"):
                candidate = candidate[: -len(".pdf")]
            return normalize_arxiv_id(candidate)
    return None


def resolve_input(raw: str) -> ResolvedInput:
    """Classify *raw* as a local PDF, an arXiv URL, or an arXiv ID.

    Raises:
        ValueError: if the input matches none of the supported forms.
    """
    path = Path(raw)
    if path.is_file():
        if path.suffix.lower() != ".pdf":
            raise ValueError(
                f"Local file exists but is not a .pdf: {raw}\n{INPUT_HELP}"
            )
        return ResolvedInput("local_pdf", None, path)

    if raw.startswith(("http://", "https://")):
        arxiv_id = arxiv_id_from_url(raw)
        if arxiv_id is None:
            raise ValueError(
                f"Unsupported URL: {raw}\n"
                "Only arxiv.org/abs/<id> and arxiv.org/pdf/<id> URLs are supported.\n"
                "For other sources, download the PDF manually and pass its path."
            )
        return ResolvedInput("arxiv_url", arxiv_id, None)

    arxiv_id = normalize_arxiv_id(raw)
    if arxiv_id is not None:
        return ResolvedInput("arxiv_id", arxiv_id, None)

    if raw.lower().endswith(".pdf"):
        raise ValueError(
            f"Looks like a local PDF path, but the file does not exist: {raw}\n"
            "Check the path, or pass an arXiv ID/URL instead."
        )

    raise ValueError(f"Could not interpret input: {raw}\n{INPUT_HELP}")


def download_arxiv_pdf(arxiv_id: str, dest: Path, force: bool = False) -> None:
    """Download the PDF for *arxiv_id* to *dest*.

    Skips the download if *dest* already exists, unless *force* is True.

    Raises:
        RuntimeError: on network errors, non-200 responses, or non-PDF content.
    """
    if dest.is_file() and not force:
        print(f"Found existing {dest}; skipping download (use --force to re-download).")
        return

    url = f"https://arxiv.org/pdf/{arxiv_id}"
    print(f"Downloading {url} ...")
    try:
        response = requests.get(
            url,
            headers={"User-Agent": USER_AGENT},
            timeout=DOWNLOAD_TIMEOUT_SECONDS,
        )
    except requests.RequestException as exc:
        raise RuntimeError(
            f"Network error while downloading {url}: {exc}\n"
            "If the problem persists, download the PDF manually and pass its "
            "local path instead."
        ) from exc

    if response.status_code != 200:
        raise RuntimeError(
            f"arXiv returned HTTP {response.status_code} for {url}. "
            "Check that the arXiv ID is correct."
        )
    if not response.content.startswith(b"%PDF"):
        content_type = response.headers.get("Content-Type", "unknown")
        raise RuntimeError(
            f"Response from {url} does not look like a PDF "
            f"(Content-Type: {content_type}). Try again later or download manually."
        )

    dest.write_bytes(response.content)
    print(f"Saved {dest} ({len(response.content):,} bytes)")


def write_metadata(
    meta_path: Path,
    raw_input: str,
    resolved: ResolvedInput,
    pdf_path: Path,
    txt_path: Path,
    result: ExtractionResult,
) -> None:
    """Write provenance and extraction info to *meta_path* as JSON."""
    metadata = {
        "input": raw_input,
        "source_type": resolved.source_type,
        "arxiv_id": resolved.arxiv_id,
        "pdf_path": str(pdf_path),
        "txt_path": str(txt_path),
        "num_pages": result.num_pages,
        "extraction_warnings": result.warnings,
        "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    meta_path.write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Fetch a paper (arXiv URL/ID or local PDF) and extract its text.",
        epilog=INPUT_HELP,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("input", help="arXiv URL, arXiv ID, or path to a local PDF.")
    parser.add_argument(
        "--out", type=Path, required=True, help="Output directory (created if missing)."
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-download even if paper.pdf already exists in the output directory.",
    )
    args = parser.parse_args(argv)

    try:
        resolved = resolve_input(args.input)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    out_dir: Path = args.out
    out_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = out_dir / "paper.pdf"
    txt_path = out_dir / "paper.txt"
    meta_path = out_dir / "metadata.json"

    try:
        if resolved.source_type == "local_pdf":
            assert resolved.local_path is not None
            if resolved.local_path.resolve() != pdf_path.resolve():
                shutil.copyfile(resolved.local_path, pdf_path)
                print(f"Copied {resolved.local_path} -> {pdf_path}")
        else:
            assert resolved.arxiv_id is not None
            download_arxiv_pdf(resolved.arxiv_id, pdf_path, force=args.force)

        result = extract_pdf_pages(pdf_path)
    except (RuntimeError, ValueError, FileNotFoundError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    txt_path.write_text(result.text, encoding="utf-8")
    write_metadata(meta_path, args.input, resolved, pdf_path, txt_path, result)

    for warning in result.warnings:
        print(f"warning: {warning}", file=sys.stderr)

    print(f"\nOutputs in {out_dir}:")
    for produced in (pdf_path, txt_path, meta_path):
        print(f"  {produced}")
    if result.warnings:
        print(
            f"\n{len(result.warnings)} extraction warning(s) recorded in "
            "metadata.json. Review paper.txt quality before relying on it."
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
