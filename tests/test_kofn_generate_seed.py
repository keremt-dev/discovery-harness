"""Faz D testleri: instance ureteci + tohum solver.

Uretec: tohumlu, deterministik, fizibilitesi garantili, doyumsuz K bandi
(docs/bilimsel-iddia-plani.md §5 tasarim ilkesi).
Tohum solver: kendi kendine yeten tek dosya (evrim genomu), cvrp sozlesmesi:
    python problems/kofn/seed_solver.py <instance.kofn> <cikti.txt>
"""

import subprocess
import sys
from pathlib import Path

import pytest

from problems.kofn.enumerate import enumerate_optimum
from problems.kofn.generate import generate_instance
from problems.kofn.io import parse_instance
from problems.kofn.objective import evaluate_text, system_reliability

REPO = Path(__file__).resolve().parent.parent
SEED_SOLVER = REPO / "problems" / "kofn" / "seed_solver.py"
ROUTER = REPO / "data" / "kofn" / "instances" / "router-n10-k20.kofn"


def gen_inst(tmp_path, n, m, seed):
    f = tmp_path / f"gen-n{n}-m{m}-s{seed}.kofn"
    f.write_text(generate_instance(n, m, seed), encoding="utf-8")
    return f


def run_seed_solver(instance_path, tmp_path):
    out = tmp_path / "out.txt"
    proc = subprocess.run(
        [sys.executable, str(SEED_SOLVER), str(instance_path), str(out)],
        capture_output=True, text=True, timeout=30,
    )
    assert proc.returncode == 0, proc.stderr
    return out.read_text(encoding="utf-8")


class TestGenerator:
    def test_deterministic_for_same_seed(self):
        assert generate_instance(12, 3, 42) == generate_instance(12, 3, 42)

    def test_different_seed_differs(self):
        assert generate_instance(12, 3, 1) != generate_instance(12, 3, 2)

    def test_output_parses_with_requested_shape(self, tmp_path):
        inst = parse_instance(gen_inst(tmp_path, 12, 3, 42))
        assert inst.n_total == 12
        assert inst.m == 3

    @pytest.mark.parametrize("seed", [1, 7, 42])
    def test_feasible_allocation_guaranteed(self, tmp_path, seed):
        # En ucuz tipe tam dolum daima butceye sigmali.
        inst = parse_instance(gen_inst(tmp_path, 12, 3, seed))
        min_cost = min(inst.costs)
        assert inst.n_total * min_cost <= inst.budget

    @pytest.mark.parametrize("seed", [1, 7, 42])
    def test_nondegenerate_and_unsaturated(self, tmp_path, seed):
        # Kanitli optimum (0,1) araliginda: ne umutsuz ne doymus.
        inst = parse_instance(gen_inst(tmp_path, 10, 3, seed))
        opt = enumerate_optimum(inst)["reliability"]
        assert 0 < opt < 1

    @pytest.mark.parametrize("n,m", [(120, 6), (200, 8)])
    def test_large_n_not_saturated(self, tmp_path, n, m):
        # Buyuk n'de sabit-oran K bandi doyuma gider (buyuk sayilar
        # yasasi). K kuantil-tabanli secilmeli: oran-greedy kurulumun
        # tahsisi bile R~1'e ulasamamali (doyumsuz bolge garantisi).
        from problems.kofn.seed_solver import construct, reliability
        inst = parse_instance(gen_inst(tmp_path, n, m, 1))
        weights = [float(w) for w in inst.weights]
        costs = [float(c) for c in inst.costs]
        rels = [float(p) for p in inst.reliabilities]
        alloc, _ = construct(inst.n_total, float(inst.budget),
                             weights, costs, rels)
        r = reliability(alloc, weights, rels, float(inst.k))
        assert 0.001 < r < 0.999


class TestSertProfile:
    """'sert' ureteci profili: oran-aldatmali, dar butceli, plato yapili.

    Varlik sebebi (2026-08-05): standart profil + guclu tohum, evrime
    headroom birakmiyordu (gen-n120-m6-s2'de 50 iterasyon duz cizgi).
    """

    def test_deterministic(self):
        a = generate_instance(20, 4, 3, profile="sert")
        assert a == generate_instance(20, 4, 3, profile="sert")
        assert a != generate_instance(20, 4, 3)  # standarttan farkli

    def test_parses_and_feasibility_guaranteed(self, tmp_path):
        f = tmp_path / "sert.kofn"
        f.write_text(generate_instance(20, 4, 3, profile="sert"),
                     encoding="utf-8")
        inst = parse_instance(f)
        assert inst.n_total * min(inst.costs) <= inst.budget

    def test_standart_profile_unchanged(self):
        # profil parametresi eski davranisi degistirmemeli
        assert generate_instance(12, 3, 42) == generate_instance(
            12, 3, 42, profile="standart")

    def test_grid_contains_true_headroom(self, tmp_path):
        # Tasarim hedefi testi: (20,4) x seed 1..10 izgarasinda en az BIR
        # instance'ta kanitli optimum, idealize tohumun >0.05 ustunde.
        from problems.kofn.refsearch import idealized_seed
        best = 0.0
        for seed in range(1, 11):
            f = tmp_path / f"s{seed}.kofn"
            f.write_text(generate_instance(20, 4, seed, profile="sert"),
                         encoding="utf-8")
            inst = parse_instance(f)
            opt = float(enumerate_optimum(inst)["reliability"])
            seed_r = idealized_seed(inst)["reliability"]
            best = max(best, opt - seed_r)
        assert best > 0.05, f"en iyi gercek headroom {best:.4f}"


class TestRealisticProfiles:
    """Benchmark v1 profilleri: makalenin uygulama senaryolarindan turetilmis
    GERCEKCI parametre rejimleri (sert/aldatmali degil). Iz-2 yayin paketi
    (docs/faz-e-gradyan.md kapanisi): router = kucuk tamsayi agirliklar +
    yuksek guvenilirlik; enerji = kapasite-oranli agirliklar (makaledeki
    2/1.9/2.1 orani, tamsayiya olceklenmis), orta guvenilirlik.
    """

    @pytest.mark.parametrize("profile", ["router", "enerji"])
    def test_deterministic_and_parses(self, tmp_path, profile):
        a = generate_instance(30, 5, 3, profile=profile)
        assert a == generate_instance(30, 5, 3, profile=profile)
        f = tmp_path / "i.kofn"
        f.write_text(a, encoding="utf-8")
        inst = parse_instance(f)
        assert inst.n_total == 30 and inst.m == 5

    @pytest.mark.parametrize("profile", ["router", "enerji"])
    def test_feasibility_guaranteed(self, tmp_path, profile):
        f = tmp_path / "i.kofn"
        f.write_text(generate_instance(30, 5, 7, profile=profile),
                     encoding="utf-8")
        inst = parse_instance(f)
        assert inst.n_total * min(inst.costs) <= inst.budget

    @pytest.mark.parametrize("profile", ["router", "enerji"])
    def test_small_tier_nondegenerate(self, tmp_path, profile):
        # kucuk katman enum kanitli olacak: 0 < opt < 1 (doyumsuz bolge)
        f = tmp_path / "i.kofn"
        f.write_text(generate_instance(15, 3, 5, profile=profile),
                     encoding="utf-8")
        opt = enumerate_optimum(parse_instance(f))["reliability"]
        assert 0 < opt < 1

    def test_reliability_regimes_differ(self, tmp_path):
        # router: yuksek p (>=0.90); enerji: daha genis/orta bant (>=0.75)
        for profile, lo in [("router", 0.90), ("enerji", 0.75)]:
            f = tmp_path / "i.kofn"
            f.write_text(generate_instance(30, 5, 11, profile=profile),
                         encoding="utf-8")
            inst = parse_instance(f)
            assert all(p >= lo for p in inst.reliabilities), profile


class TestSeedSolver:
    def test_router_solution_is_feasible(self, tmp_path):
        text = run_seed_solver(ROUTER, tmp_path)
        v = evaluate_text(parse_instance(ROUTER), text)
        assert v["feasible"] is True, v["violations"]

    def test_router_seed_escapes_zero_plateau(self, tmp_path):
        # CLAUDE.md Faz D: tohum, maliyet/fayda ORANINA gore kurar.
        # Salt "hepsi-en-ucuz" baslangici router'da R=0 platosuna saplanir
        # (tekil takas esigi gecemez); oran-greedy kurulum bunu asmali.
        text = run_seed_solver(ROUTER, tmp_path)
        v = evaluate_text(parse_instance(ROUTER), text)
        assert v["feasible"] is True
        assert v["cost"] > 0.9  # kanitli optimum 0.9999; naif plato 0.0

    def test_reports_objective_line(self, tmp_path):
        text = run_seed_solver(ROUTER, tmp_path)
        v = evaluate_text(parse_instance(ROUTER), text)
        assert v["info"]["reported_objective"] is not None

    @pytest.mark.parametrize("seed", [1, 7, 42])
    def test_generated_instances_feasible(self, tmp_path, seed):
        f = gen_inst(tmp_path, 12, 3, seed)
        v = evaluate_text(parse_instance(f), run_seed_solver(f, tmp_path))
        assert v["feasible"] is True, v["violations"]

    @pytest.mark.parametrize("seed", [1, 7])
    def test_never_beats_proven_optimum(self, tmp_path, seed):
        # Tanim geregi: tohum R <= kanitli optimum R. Ihlal = enstruman bugu.
        f = gen_inst(tmp_path, 10, 3, seed)
        inst = parse_instance(f)
        v = evaluate_text(inst, run_seed_solver(f, tmp_path))
        opt = enumerate_optimum(inst)["reliability"]
        assert v["cost"] <= float(opt) + 1e-12

    def test_time_budget_respected_on_large_instance(self, tmp_path):
        # Anytime sozlesmesi: KOFN_SEED_TIME_S=1 verilen buyuk instance'ta
        # duvar saati makul sinirda kalmali (tarama ICI deadline kontrolu).
        import os
        import time
        f = gen_inst(tmp_path, 200, 8, 1)
        out = tmp_path / "out.txt"
        env = dict(os.environ, KOFN_SEED_TIME_S="1")
        t0 = time.perf_counter()
        proc = subprocess.run(
            [sys.executable, str(SEED_SOLVER), str(f), str(out)],
            capture_output=True, text=True, timeout=60, env=env,
        )
        wall = time.perf_counter() - t0
        assert proc.returncode == 0, proc.stderr
        assert wall < 12, f"1 sn butce ile {wall:.1f} sn kostu"
        # cikti yine gecerli olmali
        v = evaluate_text(parse_instance(f), out.read_text(encoding="utf-8"))
        assert v["feasible"] is True

    def test_seed_beats_naive_all_cheapest(self, tmp_path):
        # Tohum greedy, en azindan baslangic noktasi olan "hepsi en ucuz"
        # tahsisinden kotu olmamali.
        f = gen_inst(tmp_path, 12, 3, 42)
        inst = parse_instance(f)
        cheapest = min(range(inst.m), key=lambda j: inst.costs[j])
        naive = tuple(inst.n_total if j == cheapest else 0
                      for j in range(inst.m))
        naive_r = float(system_reliability(naive, inst))
        v = evaluate_text(inst, run_seed_solver(f, tmp_path))
        assert v["cost"] >= naive_r - 1e-12
