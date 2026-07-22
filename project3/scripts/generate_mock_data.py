"""Regenerate lightweight mock data for the first visual milestone.

The checked-in mock files are intentionally small so the app can serve without
external API keys. Replace these outputs with real Oregon/FIRMS/RAPID-derived
files as the ingestion scripts mature.
"""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "public" / "data" / "processed"


def main() -> None:
    PROCESSED.mkdir(parents=True, exist_ok=True)
    print(f"Mock data already lives in {PROCESSED}")
    print("Use the dedicated fetch/process scripts to replace it with real data.")


if __name__ == "__main__":
    main()
