"""Faz D baseline rapor araci testi."""

from pathlib import Path

from problems.kofn.baseline import build_report

REPO = Path(__file__).resolve().parent.parent
ROUTER = REPO / "data" / "kofn" / "instances" / "router-n10-k20.kofn"


def test_report_contains_gap_row_for_router(tmp_path):
    out = tmp_path / "rapor.md"
    build_report([ROUTER], out, seed_time_s=2)
    text = out.read_text(encoding="utf-8")
    assert "router-n10-k20" in text
    # enumere edilebilir instance'ta kanitli optimum ve gap kolonu dolu olmali
    assert "gap" in text.lower()
    assert "0.999853" in text  # kanitli optimum R (6 hane)
