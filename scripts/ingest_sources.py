"""CLI entry point for loading approved first-aid sources into the retrieval pipeline."""

from pathlib import Path


def list_raw_sources() -> list[Path]:
    # Reads the raw document folder that will eventually contain approved PDFs and exports.
    raw_dir = Path(__file__).resolve().parents[1] / "data" / "raw"
    return sorted(path for path in raw_dir.iterdir() if path.is_file())


if __name__ == "__main__":
    for source in list_raw_sources():
        print(source.name)
