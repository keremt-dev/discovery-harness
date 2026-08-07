"""SENSE (min/max) -> combined_score işaret dönüşümü testleri.

OpenEvolve daima MAKSİMİZE eder. Bu dönüşümdeki bir işaret hatası evrimi
sessizce tersine çevirir; bu yüzden deponun ilk testi budur (CLAUDE.md §3).
"""

import pytest

from harness.score import combined_score


class TestMinProblem:
    def test_negates_fitness(self):
        assert combined_score(100.0, "min") == -100.0

    def test_better_fitness_gives_higher_score(self):
        # cvrp-discovery kalibrasyonu: 33991 (iyi) vs 44486 (kötü tohum)
        assert combined_score(33991.0, "min") > combined_score(44486.0, "min")


class TestMaxProblem:
    def test_keeps_fitness(self):
        assert combined_score(0.95, "max") == 0.95

    def test_better_fitness_gives_higher_score(self):
        assert combined_score(0.99, "max") > combined_score(0.95, "max")


class TestSenseValidation:
    @pytest.mark.parametrize("bad_sense", ["MIN", "Max", "maximize", "", None])
    def test_invalid_sense_raises_value_error(self, bad_sense):
        # Konfigürasyon yazım hatası sessizce yutulmaz: yalnızca "min"/"max".
        with pytest.raises(ValueError):
            combined_score(1.0, bad_sense)
