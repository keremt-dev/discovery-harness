"""problems/capset objective testleri (P4: F3^n cap set, evaluate_text).

evaluate_text: cap set dogrulayici — SAF TAMSAYI aritmetigi (float YOK),
O(|S|^2) ihlal kontrolu. Cozum tarafı ASLA RAISE ETMEZ: her girdi bir
verdict'e cozumlenir.

Pozitif kontrol verisi data/capset/reference/ altinda (docs/p4-problem-
tanimi.md §4):
  - n=2 (4), n=3 (9), n=4 (20): bagimsiz uretim, optimal
  - n=8 (512): FunSearch / Nature 2024 (indirildi + bagimsiz dogrulandi)
n=5/6/7 BOŞLUK — pozitif kontrol bu n'lerde enumerate/seed ciktisina
dusuyor, bu testte yer almaz (P4.2/P4.3).
"""

from pathlib import Path

import pytest

from problems.capset.io import parse_instance
from problems.capset.objective import evaluate_text
from problems.capset.spec import penalty_scale

REF = Path(__file__).resolve().parent.parent / "data" / "capset" / "reference"


def inst_for(tmp_path, n):
    f = tmp_path / f"capset-n{n}.cap"
    f.write_text(f"# cap set n={n}\ndimension {n}\n", encoding="utf-8")
    return parse_instance(f)


def load_ref(name):
    """Cozum formati: '#' yorum + bitisik {0,1,2} satirlari -> tek metin."""
    lines = REF.joinpath(name).read_text(encoding="utf-8").splitlines()
    return "\n".join(l for l in lines if l.strip() and not l.strip().startswith("#"))


# ----- Pozitif kontroller: indirilen/uretilen cap kumeleri feasible + dogru |S| -----
POSITIVE = [
    ("optimal_n2_size4.txt", 2, 4),
    ("optimal_n3_size9.txt", 3, 9),
    ("optimal_n4_size20.txt", 4, 20),
    ("funsearch_n8_size512.txt", 8, 512),  # ALTIN pozitif kontrol
]


class TestEvaluateFeasible:
    @pytest.mark.parametrize("fn,n,size", POSITIVE)
    def test_known_cap_is_feasible_correct_size(self, tmp_path, fn, n, size):
        inst = inst_for(tmp_path, n)
        v = evaluate_text(inst, load_ref(fn))
        assert v["feasible"] is True, f"{fn} cap olmali"
        assert v["violations"] == {}
        assert v["cost"] == size
        assert isinstance(v["eval_ms"], int)

    @pytest.mark.parametrize("fn,n,size", POSITIVE)
    def test_fitness_is_normalized(self, tmp_path, fn, n, size):
        inst = inst_for(tmp_path, n)
        v = evaluate_text(inst, load_ref(fn))
        assert v["fitness"] == pytest.approx(size / penalty_scale(inst))
        assert 0.0 <= v["fitness"] < 1.0  # fitness [0,1)

    def test_empty_set_is_feasible_zero_fitness(self, tmp_path):
        # Bos kume (yalnizca yorum) -> feasible, |S|=0, fitness=0 (mesru taban).
        inst = inst_for(tmp_path, 4)
        v = evaluate_text(inst, "# bos cozum\n\n")
        assert v["feasible"] is True
        assert v["cost"] == 0
        assert v["fitness"] == 0.0

    def test_comments_ignored(self, tmp_path):
        inst = inst_for(tmp_path, 2)
        v = evaluate_text(inst, "# baslik\n01\n10\n00\n11\n# son\n")
        assert v["feasible"] is True
        assert v["cost"] == 4


class TestViolations:
    def test_bad_length(self, tmp_path):
        inst = inst_for(tmp_path, 4)
        v = evaluate_text(inst, "0001\n00001\n")  # ikinci 5 uzunlugunda
        assert v["feasible"] is False
        assert "bad_vector" in v["violations"]

    def test_bad_alphabet(self, tmp_path):
        inst = inst_for(tmp_path, 4)
        v = evaluate_text(inst, "0003\n")  # 3 alfabe disi
        assert v["feasible"] is False
        assert "bad_vector" in v["violations"]

    def test_duplicate_vector(self, tmp_path):
        # Tekrarlanan vektor -> duplicate_vector (sisme hilesine karsi; affedilmez).
        inst = inst_for(tmp_path, 2)
        v = evaluate_text(inst, "01\n01\n10\n00\n")
        assert v["feasible"] is False
        assert "duplicate_vector" in v["violations"]

    def test_line_found_with_example(self, tmp_path):
        # n=2: 00, 01, 02 bir dogru (line). 00+01+02 = 0 mod 3 bileşen bazli.
        # 0+0+0=0, 0+1+2=3=0 mod3 -> 3-AP. Ucu de farkli.
        inst = inst_for(tmp_path, 2)
        v = evaluate_text(inst, "00\n01\n02\n")
        assert v["feasible"] is False
        assert "line_found" in v["violations"]
        assert v["violations"]["line_found"]["count"] >= 1
        info = v["info"]
        ex = info.get("example_line")
        assert ex is not None
        assert len(ex) == 3  # (x, y, z) ucusu
        assert info.get("line_count", 0) >= 1  # info'da da line sayisi


class TestNeverRaises:
    @pytest.mark.parametrize("garbage", [
        "",                       # bos metin
        "   \n\n  \t  ",          # yalnizca bosluk
        "# sadece yorum\n",       # hic vektor yok (ama feasible empty)
        "merhaba dunya",          # cop
        "0 1 0\n",                # bosluklu (bitisik degil)
        "abc\n",                  # alfabe disi
        "\x00\x01\xff\n",         # cop bayt
        "0" * 10000 + "\n",       # dev satir (yanlis uzunluk ama raise yok)
        "1\n2\n3\n4\n5\n",        # 1 uzunlugunda tek karakter (n=2 icin bad)
    ])
    def test_never_raises(self, tmp_path, garbage):
        inst = inst_for(tmp_path, 2)
        v = evaluate_text(inst, garbage)
        assert isinstance(v, dict)
        assert {"feasible", "cost", "violations", "fitness", "eval_ms", "info"} <= set(v)
        # Cop girdi feasible degildir (empty hariç ama bos degilse)
        # Yalnizca yoruma inen bos kume feasible; cop infeasible.
        assert isinstance(v["feasible"], bool)

    @pytest.mark.parametrize("weird", [None, 42, ["012"], 3.14, ("01", "10"), b"01"])
    def test_non_string_text_does_not_raise(self, tmp_path, weird):
        # None / sayi / liste / tuple / bytes gibi non-str guvenli bilgi:
        # bos olarak ele al (never-raise). Görev 2: eskiden yalnizca None.
        inst = inst_for(tmp_path, 2)
        v = evaluate_text(inst, weird)
        assert isinstance(v, dict)
        assert {"feasible", "cost", "violations", "fitness", "eval_ms", "info"} <= set(v)
        # non-str -> bos kume gibi -> feasible empty, |S|=0
        assert v["feasible"] is True
        assert v["cost"] == 0


class TestFeasibleAboveInfeasible:
    def test_every_infeasible_below_every_feasible(self, tmp_path):
        inst = inst_for(tmp_path, 2)
        # En umutsuz feasible: bos kume (|S|=0, fitness=0)
        worst_feasible = evaluate_text(inst, "# empty\n")["fitness"]
        infeasibles = [
            evaluate_text(inst, "00\n01\n02\n")["fitness"],   # line_found
            evaluate_text(inst, "01\n01\n")["fitness"],        # duplicate
            evaluate_text(inst, "0001\n")["fitness"],          # bad length
            evaluate_text(inst, "33\n")["fitness"],            # bad alphabet
            evaluate_text(inst, "cop\n")["fitness"],           # bad vector
        ]
        assert all(f < worst_feasible for f in infeasibles), \
            f"infeasible {infeasibles} >= feasible {worst_feasible}"


class TestGradedPenalty:
    def test_more_violations_worse_fitness(self, tmp_path):
        # Infeasible'lar arasinda gradyan: AYNI |S|, daha cok ihlal (line)
        # -> daha dusuk fitness. AG(2,3)'te iki |S|=5 kume:
        #   low : 00 01 02 10 11 -> 1 line  (matches=3)
        #   high: 00 01 02 10 20 -> 2 line (matches=6)  (cift sayisi ayni=10)
        # yogunluk (matches/cift) yukselince fitness duser.
        inst = inst_for(tmp_path, 2)
        low = evaluate_text(inst, "00\n01\n02\n10\n11\n")
        high = evaluate_text(inst, "00\n01\n02\n10\n20\n")
        assert high["info"]["line_count"] > low["info"]["line_count"]
        assert high["fitness"] < low["fitness"]

    def test_infeasible_fitness_in_minus_two_minus_one(self, tmp_path):
        # infeasible fitness = -1 - min(1, ihlal/cift) -> [-2,-1] araligi.
        # Görev 2: eskiden `or f <= -1.0` disjunct'i vardi (zayif; -50 gecerdi).
        # Dogru assert: -2.0 <= f < -1.0 (tam -2.0 dahil: matches/cift=1.0 durumu).
        inst = inst_for(tmp_path, 2)
        v = evaluate_text(inst, "00\n01\n02\n")
        f = v["fitness"]
        assert -2.0 <= f < -1.0, f"infeasible fitness {f} [-2,-1] araliginda degil"
        assert f < 0.0


class TestReportedSizeSensor:
    def test_reported_size_ignored_but_recorded(self, tmp_path):
        # "# size K" beyani verdict'i DEGISTIRMEZ; info.reported_size_matches'e yazilir.
        inst = inst_for(tmp_path, 2)
        correct = "# size 4\n00\n01\n10\n11\n"
        v = evaluate_text(inst, correct)
        assert v["feasible"] is True
        assert v["cost"] == 4
        assert v["info"].get("reported_size") == 4
        assert v["info"].get("reported_size_matches") is True

    def test_reported_size_lie_detected(self, tmp_path):
        inst = inst_for(tmp_path, 2)
        lie = "# size 99\n00\n01\n10\n11\n"  # gercekte 4, 99 diye yalan
        v = evaluate_text(inst, lie)
        assert v["cost"] == 4  # gercek hesap etkilenmez
        assert v["info"]["reported_size"] == 99
        assert v["info"]["reported_size_matches"] is False

    def test_no_reported_size_gives_none(self, tmp_path):
        inst = inst_for(tmp_path, 2)
        v = evaluate_text(inst, "00\n01\n10\n11\n")
        assert v["info"].get("reported_size") is None
        assert v["info"].get("reported_size_matches") is None

    def test_reported_size_compared_to_unique_count(self, tmp_path):
        # Görev 3: reported_size_matches HAM satir sayisina degil TEKIL vektor
        # sayisina gore olcmeli. Duplicate'li cikti "# size 3" (3 satir) ama
        # 2 tekil vektor -> matches False (solver 3 diye sismis, gercek 2).
        inst = inst_for(tmp_path, 2)
        v = evaluate_text(inst, "# size 3\n00\n00\n01\n")  # 00 tekrar, 2 tekil
        assert v["feasible"] is False  # duplicate_vector
        assert v["info"]["reported_size"] == 3
        assert v["info"]["reported_size_matches"] is False  # 3 != 2 (tekil)
