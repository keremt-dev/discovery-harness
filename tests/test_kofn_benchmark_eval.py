"""Benchmark v1 degerlendirme araci testi (Iz-2 yayin paketi)."""

from pathlib import Path

from problems.kofn.benchmark_eval import build_report

REPO = Path(__file__).resolve().parent.parent
SEED = REPO / "problems" / "kofn" / "seed_solver.py"


def test_report_row_with_enum_and_solver(tmp_path):
    from problems.kofn.generate import generate_instance
    inst = tmp_path / "gen-router-n12-m3-s1.kofn"
    inst.write_text(generate_instance(12, 3, 1, profile="router"),
                    encoding="utf-8")
    out = tmp_path / "rapor.md"
    build_report([inst], out, solvers={"tohum": SEED},
                 seed_time_s=3, timeout_s=30)
    text = out.read_text(encoding="utf-8")
    assert "gen-router-n12-m3-s1" in text
    assert "tohum" in text
    assert "kanıtlı opt" in text  # kucuk katman enum kolonu dolu olmali
