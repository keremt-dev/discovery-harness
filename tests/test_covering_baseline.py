"""problems/covering baseline testleri: rapor uretimi + alan sozlesmesi.

Gercek butceli koşu CLI isidir (dakikalar); test kucuk hucre + kisa
butce ile yalnizca boru hattinin dogrulugunu sabitler.
"""

from problems.covering.baseline import build_rows, write_report


def test_build_rows_small_cell(tmp_path):
    inst_dir = tmp_path / "instances"
    inst_dir.mkdir()
    (inst_dir / "cover-v7-k3-t2.cover").write_text(
        "v 7\nk 3\nt 2\n", encoding="utf-8")
    rows = build_rows(inst_dir, budget_s=0.2)
    assert len(rows) == 1
    r = rows[0]
    assert r["feasible"] is True
    assert r["ref_kind"] == "kanitli-opt"
    assert r["ref"] == 7                      # bagimsiz kanit
    assert r["seed_cost"] >= r["schoenheim"] == 7
    assert r["gap"] == r["seed_cost"] - 7


def test_write_report(tmp_path):
    inst_dir = tmp_path / "instances"
    inst_dir.mkdir()
    (inst_dir / "cover-v7-k3-t2.cover").write_text(
        "v 7\nk 3\nt 2\n", encoding="utf-8")
    rows = build_rows(inst_dir, budget_s=0.2)
    out = tmp_path / "rapor.md"
    write_report(rows, out, 0.2)
    text = out.read_text(encoding="utf-8")
    assert "Faz D baseline" in text
    assert "cover-v7-k3-t2" in text
