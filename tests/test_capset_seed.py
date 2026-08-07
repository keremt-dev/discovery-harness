"""problems/capset seed_solver testleri (P4.3: tohum solver).

seed_solver.py: evrim dongusunun baslangic genomu. Strateji (CLAUDE.md
§5 P4.3): rastgele-greedy kurulum + extend + swap hill-climb + random-
restart (anytime). Kendi kendine yeten tek dosya; anytime + atomik
yazim (os.replace). Deterministik --seed argumani.

Cozum formati (spec.py): '# size K' beyani + her satir n adet bitisik
{0,1,2}. Tohum yalnizca KENDI buldugu cap'i ciktilar; rekor solver'a
SIZDIRILMAZ (§0.5).

Boyut esikleri "meşru saf greedy gucu" (P4.0 olcumlerine dayali),
"kasitli zayiflatma" DEGIL: n=2>=4, n=3>=9, n=4>=16, n=8>=200.
"""

import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

from problems.capset.io import parse_instance
from problems.capset.objective import evaluate_text
from problems.capset.seed_solver import solve

SEED_SOLVER = Path(__file__).resolve().parent.parent / "problems" / "capset" / "seed_solver.py"


def inst_for(tmp_path, n):
    f = tmp_path / f"capset-n{n}.cap"
    f.write_text(f"dimension {n}\n", encoding="utf-8")
    return f


def assert_is_feasible_cap(inst, cap, min_size=1):
    sol = "\n".join("".join(str(c) for c in v) for v in cap)
    v = evaluate_text(inst, sol)
    assert v["feasible"] is True, f"tohum cap degil! violations={v['violations']}"
    assert v["cost"] == len(cap)
    assert v["cost"] >= min_size


class TestSolveCore:
    def test_returns_nonempty_cap(self, tmp_path):
        f = inst_for(tmp_path, 3)
        inst = parse_instance(f)
        cap = solve(inst, time_budget_s=1.0, seed=42)
        assert isinstance(cap, list)
        assert len(cap) > 0
        assert_is_feasible_cap(inst, cap)

    def test_deterministic_pure_functions(self, tmp_path):
        # Determinizmi saf fonksiyonlar uzerinden sına (zaman YOK -> flake'siz).
        # Ayni seed ile uretilmis ayni order icin _greedy_construct + _extend
        # ciktisi birebir esit olmali.
        import itertools
        import random as _random
        from problems.capset.seed_solver import _greedy_construct, _extend, _powers
        n = 4
        pw = _powers(n)
        all_vecs = list(itertools.product((0, 1, 2), repeat=n))
        order1 = list(all_vecs); _random.Random(7).shuffle(order1)
        order2 = list(all_vecs); _random.Random(7).shuffle(order2)
        assert order1 == order2  # RNG deterministik
        cap1, blk1 = _greedy_construct(n, order1, pw)
        cap1, blk1 = _extend(n, cap1, blk1, pw, all_vecs)
        cap2, blk2 = _greedy_construct(n, order2, pw)
        cap2, blk2 = _extend(n, cap2, blk2, pw, all_vecs)
        assert sorted(cap1) == sorted(cap2)  # ayni order -> ayni cap

    def test_deterministic_solve_saturated_n2(self, tmp_path):
        # n=2'de bol butceyle tohum optimuma (4) doyar -> restart sayisindan
        # bagimsiz deterministik sonuc (flake'siz: doygunluk garantili).
        f = inst_for(tmp_path, 2)
        inst = parse_instance(f)
        cap1 = solve(inst, time_budget_s=1.0, seed=3)
        cap2 = solve(inst, time_budget_s=1.0, seed=99)  # farkli seed bile
        assert len(cap1) == 4  # a(2)=4 optimuma doymus
        assert len(cap2) == 4
        # her ikisi de gecerli cap
        assert_is_feasible_cap(inst, cap1)
        assert_is_feasible_cap(inst, cap2)

    def test_more_time_not_worse(self, tmp_path):
        # Anytime: daha uzun sure -> en az kadar iyi (monoton en iyi korunur).
        f = inst_for(tmp_path, 5)
        inst = parse_instance(f)
        short = len(solve(inst, time_budget_s=0.3, seed=1))
        long_ = len(solve(inst, time_budget_s=3.0, seed=1))
        assert long_ >= short

    @pytest.mark.parametrize("n,min_size", [
        (2, 4),   # a(2)=4 optimum; greedy bulabilmeli
        (3, 9),   # a(3)=9 optimum; greedy+restart bulabilmeli
        (4, 16),  # a(4)=20 optimum; saf greedy ~16-20 (evrim baslangici)
    ])
    def test_seed_meets_natural_greedy_floor(self, tmp_path, n, min_size):
        # Strawman DEGIL: meşru saf greedy'nin dogal gucu. P4.0 olcumleri.
        f = inst_for(tmp_path, n)
        inst = parse_instance(f)
        cap = solve(inst, time_budget_s=2.0, seed=123)
        assert_is_feasible_cap(inst, cap, min_size=min_size)

    def test_n8_has_gradient_room(self, tmp_path):
        # n=8: tohum 512'den uzak olmali (gradyan kaynagi, headroom turnusolu).
        # Alt sinir: 200 (saf greedy gucu); ust sinir: 512'den cok asagida.
        f = inst_for(tmp_path, 8)
        inst = parse_instance(f)
        cap = solve(inst, time_budget_s=3.0, seed=99)
        size = len(cap)
        assert size >= 200, f"n=8 tohum {size} cok dusuk (strawman?)"
        assert size < 512, f"n=8 tohum {size} tavanda (gradyan yok)"


class TestSeedSizeDeclaration:
    def test_solution_has_size_header(self, tmp_path):
        f = inst_for(tmp_path, 3)
        inst = parse_instance(f)
        cap = solve(inst, time_budget_s=1.0, seed=5)
        # cozum metnini kur, '# size K' header'i evaluate_text sensorunde
        from problems.capset.seed_solver import format_solution
        text = format_solution(cap)
        assert "# size" in text
        v = evaluate_text(inst, text)
        assert v["info"]["reported_size"] == len(cap)
        assert v["info"]["reported_size_matches"] is True


class TestCLI:
    def test_main_writes_valid_solution_file(self, tmp_path):
        # Sozlesme (kofn/cvrp deseni): python seed_solver.py <instance> <cikti>.
        # env GERCEKTEN geçirilir (Görev 2: env_time eskiden tanimli ama geçilmiyordu).
        f = inst_for(tmp_path, 4)
        out = tmp_path / "sol.txt"
        t0 = time.perf_counter()
        proc = subprocess.run(
            [sys.executable, str(SEED_SOLVER), str(f), str(out),
             "--seed", "11"],
            capture_output=True, text=True, timeout=30,
            env={**os.environ, "CAPSET_SEED_TIME_S": "2"},
        )
        wall = time.perf_counter() - t0
        assert proc.returncode == 0, f"stderr: {proc.stderr}"
        assert wall < 8.0, f"2 sn bütçe {wall:.1f} sn sürdü (env geçmiyor?)"
        assert out.exists(), "cikti dosyasi olusmadi"
        text = out.read_text(encoding="utf-8")
        # atomik yazim: dosya hep gecerli format (yarim satir yok)
        inst = parse_instance(f)
        v = evaluate_text(inst, text)
        assert v["feasible"] is True, f"cikti feasible degil: {v['violations']}"
        assert v["cost"] > 0

    def test_main_atomic_no_partial_lines(self, tmp_path):
        # Anytime: her zaman gecerli cozum (timeout aninda bile). Ciktiyi
        # oku — her vektor satiri tam n uzunlugunda {0,1,2} olmali.
        f = inst_for(tmp_path, 3)
        out = tmp_path / "sol.txt"
        proc = subprocess.run(
            [sys.executable, str(SEED_SOLVER), str(f), str(out),
             "--seed", "3"],
            capture_output=True, text=True, timeout=30,
            env={**os.environ, "CAPSET_SEED_TIME_S": "1"},
        )
        assert proc.returncode == 0
        for line in out.read_text(encoding="utf-8").splitlines():
            body = line.split("#", 1)[0].strip()
            if not body:
                continue
            assert len(body) == 3, f"yarim satir: {line!r}"
            assert all(c in "012" for c in body)

    def test_main_writes_early_anytime(self, tmp_path):
        # Görev 1: ilk yazım greedy+extend'ten HEMEN sonra (hill-climb oncesi)
        # gelmeli. n=6'da hill-climb bütçeyi tüketsin; ilk yarida dosya olmali.
        # Polling: subprocess'i baslat, ~1 sn sonra dosyanin varligini kontrol et.
        f = inst_for(tmp_path, 6)
        out = tmp_path / "sol.txt"
        proc = subprocess.Popen(
            [sys.executable, str(SEED_SOLVER), str(f), str(out), "--seed", "2"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            env={**os.environ, "CAPSET_SEED_TIME_S": "4"},
        )
        try:
            # bütçenin ilk yarisi (~2 sn) icinde dosya olusmali; toleransli bekle
            appeared = False
            for _ in range(20):  # 20 x 0.15 sn = 3 sn pencere
                time.sleep(0.15)
                if out.exists():
                    appeared = True
                    break
            assert appeared, "cikti bütçenin ilk yarisinda olusmadi (anytime degil?)"
            # olusan dosya gecerli cozum olmali
            text = out.read_text(encoding="utf-8")
            inst = parse_instance(f)
            v = evaluate_text(inst, text)
            assert v["feasible"] is True
            assert v["cost"] >= 1
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()
