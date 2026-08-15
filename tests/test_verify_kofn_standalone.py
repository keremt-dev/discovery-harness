"""Bagimsiz kofn dogrulayicisi (data/kofn/reference/verify_kofn.py) testi.

Dogrulayici KENDI KENDINE YETEN tek dosyadir (yalniz stdlib): alicinin
depo olmadan calistirabilmesi sozlesmenin parcasi. Kanonik kopya depoda
durur; yazar temas paketi (gitignore'lu outreach/) ayni dosyanin kopyasini
tasir. Bu test, onun kesin aritmetigini depodaki kanonik
objective.system_reliability'ye karsi dogrular (ayni Fraction, birebir
esitlik) ve CSV denetim modunu sinar.
"""

import importlib.util
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

import pytest

from problems.kofn.generate import generate_instance
from problems.kofn.io import parse_instance
from problems.kofn.objective import system_reliability

REPO = Path(__file__).resolve().parent.parent
VERIFIER = REPO / "data" / "kofn" / "reference" / "verify_kofn.py"


@pytest.fixture(scope="module")
def vk():
    spec = importlib.util.spec_from_file_location("verify_kofn", VERIFIER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture()
def inst_file(tmp_path):
    f = tmp_path / "gen-router-n12-m3-s1.kofn"
    f.write_text(generate_instance(12, 3, 1, profile="router"),
                 encoding="utf-8")
    return f


class TestExactArithmetic:
    def test_matches_canonical_reliability(self, vk, inst_file):
        # Ayni tahsis icin Fraction sonucu kanonik hesapla BIREBIR esit.
        canon = parse_instance(inst_file)
        own = vk.parse_instance(inst_file)
        for alloc in [(12, 0, 0), (0, 12, 0), (4, 4, 4), (10, 1, 1)]:
            assert vk.system_reliability(alloc, own) == \
                system_reliability(alloc, canon)

    def test_r12_formatting(self, vk):
        assert vk.r12(Fraction(9, 10)) == "0.900000000000"
        assert vk.r12(Fraction(1)) == "1.000000000000"
        assert vk.r12(Fraction(1, 3)) == "0.333333333333"


class TestFeasibility:
    def test_feasible_allocation(self, vk, inst_file):
        inst = vk.parse_instance(inst_file)
        cheapest = min(range(inst.m), key=lambda j: inst.costs[j])
        alloc = [0] * inst.m
        alloc[cheapest] = inst.n_total
        verdict = vk.check(inst, tuple(alloc))
        assert verdict["feasible"] is True
        assert verdict["violations"] == []

    def test_wrong_total_and_budget(self, vk, inst_file):
        inst = vk.parse_instance(inst_file)
        v1 = vk.check(inst, tuple([1] * inst.m))  # toplam != N
        assert v1["feasible"] is False
        assert any("toplam" in s for s in v1["violations"])
        expensive = max(range(inst.m), key=lambda j: inst.costs[j])
        alloc = [0] * inst.m
        alloc[expensive] = inst.n_total * 100  # butce + toplam ihlali
        v2 = vk.check(inst, tuple(alloc))
        assert v2["feasible"] is False
        assert any("butce" in s.lower() or "bütçe" in s.lower()
                   for s in v2["violations"])

    def test_negative_count(self, vk, inst_file):
        inst = vk.parse_instance(inst_file)
        alloc = [-1] + [0] * (inst.m - 2) + [inst.n_total + 1]
        v = vk.check(inst, tuple(alloc))
        assert v["feasible"] is False


class TestCsvMode:
    def test_csv_ok_and_tampered(self, vk, inst_file, tmp_path):
        inst = vk.parse_instance(inst_file)
        cheapest = min(range(inst.m), key=lambda j: inst.costs[j])
        alloc = [0] * inst.m
        alloc[cheapest] = inst.n_total
        r_ok = vk.r12(vk.system_reliability(tuple(alloc), inst))
        alloc_s = " ".join(str(c) for c in alloc)
        header = ("instance,n,m,k,budget,solver,allocation,money,"
                  "R_exact_12dp")
        csv_f = tmp_path / "sertifikalar.csv"
        csv_f.write_text(
            f"{header}\n"
            f"{inst_file.stem},{inst.n_total},{inst.m},{inst.k},"
            f"{inst.budget},test,{alloc_s},0,{r_ok}\n"
            f"{inst_file.stem},{inst.n_total},{inst.m},{inst.k},"
            f"{inst.budget},test,{alloc_s},0,0.999999999999\n",
            encoding="utf-8")
        results = vk.verify_csv(csv_f, inst_file.parent)
        assert [r["ok"] for r in results] == [True, False]

class TestEnumMode:
    """--enum: kucuk instance'ta exhaustive tarama ile kanitli optimum.

    Alicinin "sizin brute-force'unuzla ayni sonuc" iddiasini paket icinden
    tek komutla gorebilmesi icin. Depo enumeratoruyle ayni beraberlik
    kurali: R max -> maliyet min -> leksikografik.
    """

    def test_matches_canonical_enumerator(self, vk, inst_file):
        from problems.kofn.enumerate import enumerate_optimum as canon_enum
        canon = canon_enum(parse_instance(inst_file))
        own = vk.enumerate_optimum(vk.parse_instance(inst_file))
        assert own["r"] == canon["reliability"]  # Fraction birebir
        assert tuple(own["alloc"]) == tuple(canon["alloc"])

    def test_size_guard_refuses_large(self, vk, tmp_path):
        # C(65,5) ~ 8.3M kompozisyon > varsayilan limit -> ValueError
        f = tmp_path / "big.kofn"
        f.write_text(generate_instance(60, 6, 1, profile="router"),
                     encoding="utf-8")
        with pytest.raises(ValueError, match="limit"):
            vk.enumerate_optimum(vk.parse_instance(f))

    def test_cli_enum(self, inst_file):
        from problems.kofn.enumerate import enumerate_optimum as canon_enum
        canon = canon_enum(parse_instance(inst_file))
        proc = subprocess.run(
            [sys.executable, str(VERIFIER), "--enum", str(inst_file)],
            capture_output=True, text=True, timeout=120)
        assert proc.returncode == 0, proc.stderr
        i = round(canon["reliability"] * 10**12)
        assert f"{i // 10**12}.{i % 10**12:012d}" in proc.stdout
        assert " ".join(map(str, canon["alloc"])) in proc.stdout


class TestCli:
    def test_cli_single_allocation(self, inst_file, tmp_path):
        # CLI duman testi: fizibil tahsis -> exit 0 ve 12 haneli R basar.
        inst = parse_instance(inst_file)
        cheapest = min(range(inst.m), key=lambda j: inst.costs[j])
        alloc = " ".join(str(inst.n_total if j == cheapest else 0)
                         for j in range(inst.m))
        proc = subprocess.run(
            [sys.executable, str(VERIFIER), str(inst_file), alloc],
            capture_output=True, text=True, timeout=60)
        assert proc.returncode == 0, proc.stderr
        expected = system_reliability(
            tuple(inst.n_total if j == cheapest else 0
                  for j in range(inst.m)), inst)
        i = round(expected * 10**12)
        assert f"{i // 10**12}.{i % 10**12:012d}" in proc.stdout
