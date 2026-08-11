"""problems/covering seed_solver testleri (P5 Faz D: tohum solver).

seed_solver.py: evrim dongusunun baslangic genomu — greedy kurulum
(orneklenmis aday paneli) + redundancy removal + ruin-and-recreate,
anytime + atomik yazim, deterministik --seed. Kendi kendine yeten tek
dosya; arsiv degerleri SIZDIRILMAZ (§0.5).

Boyut esikleri "mesru saf greedy gucu": kucuk hucrelerde kanitli optimuma
yakin (Fano <= 8), buyuklerde yalnizca feasibility + Schoenheim alt sinir
tutarliligi denetlenir — sayisal ustunluk iddiasi baseline.py'nin isi.
"""

import os
import subprocess
import sys
from pathlib import Path

from problems.covering.io import parse_instance
from problems.covering.objective import evaluate_text
from problems.covering.seed_solver import (format_solution,
                                           parse_instance_file, solve)
from problems.covering.spec import schoenheim

SEED_SOLVER = (Path(__file__).resolve().parent.parent
               / "problems" / "covering" / "seed_solver.py")


def inst_file(tmp_path, v, k, t):
    f = tmp_path / f"cover-v{v}-k{k}-t{t}.cover"
    f.write_text(f"v {v}\nk {k}\nt {t}\n", encoding="utf-8")
    return f


def assert_feasible(tmp_path, v, k, t, blocks):
    inst = parse_instance(inst_file(tmp_path, v, k, t))
    verdict = evaluate_text(inst, format_solution(blocks))
    assert verdict["feasible"] is True, f"violations={verdict['violations']}"
    assert verdict["cost"] == len(blocks)
    assert len(blocks) >= schoenheim(v, k, t)
    return verdict


class TestSolveCore:
    def test_fano_feasible_near_optimal(self, tmp_path):
        blocks = solve(7, 3, 2, time_budget_s=1.0, seed=42)
        assert_feasible(tmp_path, 7, 3, 2, blocks)
        assert len(blocks) <= 8  # kanitli optimum 7; greedy+RR yakin kalmali

    def test_sts13_feasible(self, tmp_path):
        blocks = solve(13, 3, 2, time_budget_s=1.0, seed=42)
        assert_feasible(tmp_path, 13, 3, 2, blocks)
        assert len(blocks) <= 32  # kanitli optimum 26; makul greedy bandi

    def test_medium_cell_feasible(self, tmp_path):
        # Hedef ailesinin kucuk temsilcisi: C(28,9,3) (arsiv 56).
        blocks = solve(28, 9, 3, time_budget_s=2.0, seed=1)
        assert_feasible(tmp_path, 28, 9, 3, blocks)

    def test_deterministic_same_seed(self):
        # Determinizm zaman bagimliligi olmadan: butce 0 -> yalniz ilk
        # greedy + redundancy (RR dongusu deadline'da hic kosmaz).
        b1 = solve(9, 3, 2, time_budget_s=0.0, seed=7)
        b2 = solve(9, 3, 2, time_budget_s=0.0, seed=7)
        assert b1 == b2

    def test_different_seed_may_differ_but_feasible(self, tmp_path):
        b1 = solve(9, 3, 2, time_budget_s=0.0, seed=1)
        b2 = solve(9, 3, 2, time_budget_s=0.0, seed=2)
        assert_feasible(tmp_path, 9, 3, 2, b1)
        assert_feasible(tmp_path, 9, 3, 2, b2)


class TestFormatAndParse:
    def test_format_has_honesty_header(self):
        text = format_solution([(1, 2, 3), (1, 2, 4)])
        assert text.startswith("# size 2\n")
        assert "1 2 3" in text

    def test_parse_instance_file(self, tmp_path):
        f = inst_file(tmp_path, 32, 8, 4)
        assert parse_instance_file(f) == (32, 8, 4)


class TestCli:
    def test_cli_writes_feasible_solution(self, tmp_path):
        inst = inst_file(tmp_path, 7, 3, 2)
        out = tmp_path / "out.txt"
        env = dict(os.environ, COVERING_SEED_TIME_S="1")
        subprocess.run(
            [sys.executable, str(SEED_SOLVER), str(inst), str(out),
             "--seed", "3"],
            check=True, env=env, timeout=30)
        verdict = evaluate_text(parse_instance(inst), out.read_text())
        assert verdict["feasible"] is True
        assert verdict["info"]["reported_size_matches"] is True

    def test_cli_tiny_budget_still_writes(self, tmp_path):
        # Anytime sozlesmesi: butce cok kucuk olsa bile ilk greedy tamam-
        # landiginda dosya yazilmis olmali (runner kurtarabilsin).
        inst = inst_file(tmp_path, 9, 3, 2)
        out = tmp_path / "out.txt"
        env = dict(os.environ, COVERING_SEED_TIME_S="0")
        subprocess.run(
            [sys.executable, str(SEED_SOLVER), str(inst), str(out)],
            check=True, env=env, timeout=30)
        assert out.exists()
        verdict = evaluate_text(parse_instance(inst), out.read_text())
        assert verdict["feasible"] is True
