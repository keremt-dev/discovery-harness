"""problems/capset io + spec testleri (P4: F3^n cap set).

Instance formati (CLAUDE.md §3 + docs/p4-problem-tanimi.md §5):
    # yorum serbest
    dimension <n>

Cozum metni: '#' yorum + bitisik {0,1,2} karakterli satirlar.
Bu dosya yalnizca Instance tarafini (parse_instance, InstanceFormatError)
ve spec tarafini (SENSE, penalty_scale) test eder. Cozum tarafini
(evaluate_text) test_capset_objective.py test eder.
"""

import pytest

from problems.capset.io import Instance, InstanceFormatError, parse_instance
from problems.capset.spec import SENSE, penalty_scale


def make_inst(tmp_path, text, name="i.cap"):
    f = tmp_path / name
    f.write_text(text, encoding="utf-8")
    return parse_instance(f)


@pytest.fixture
def inst(tmp_path):
    return make_inst(tmp_path, "# cap set n=8\n\ndimension 8\n", "capset-n8.cap")


class TestSpec:
    def test_sense_is_max(self):
        assert SENSE == "max"

    def test_penalty_scale_meshulam_bound(self, inst):
        # penalty_scale(n) = 2*3^n / n (Meshulam teorem siniri; teorem != referans).
        # n=8: 2*6561/8 = 1640.25
        s = penalty_scale(inst)
        assert isinstance(s, float)
        assert s == pytest.approx(2 * 3**8 / 8)

    def test_penalty_scale_grows_with_n(self, tmp_path):
        # Buyuk n'de olcek buyur -> fitness instance'lar arasi karsilastirilabilir.
        small = penalty_scale(make_inst(tmp_path, "dimension 2\n"))
        big = penalty_scale(make_inst(tmp_path, "dimension 6\n"))
        assert big > small


class TestParseInstance:
    def test_valid_instance_fields(self, inst):
        assert isinstance(inst, Instance)
        assert inst.dimension == 8
        # name dosya govdesinden degil dosya adindan (ya da verilmisse ordan);
        # capset instance'i minimal: name bilgilendirici.
        assert isinstance(inst.name, str)

    def test_comments_and_blank_lines_ignored(self, tmp_path):
        text = (
            "# bu bir yorum\n"
            "\n"
            "   # girintili yorum\n"
            "dimension 4\n"
            "# son\n"
        )
        i = make_inst(tmp_path, text)
        assert i.dimension == 4

    def test_dimension_missing_raises(self, tmp_path):
        with pytest.raises(InstanceFormatError, match="[Dd]imension"):
            make_inst(tmp_path, "# sadece yorum\n")

    def test_dimension_not_integer_raises(self, tmp_path):
        with pytest.raises(InstanceFormatError):
            make_inst(tmp_path, "dimension sekiz\n")

    def test_dimension_zero_raises(self, tmp_path):
        with pytest.raises(InstanceFormatError):
            make_inst(tmp_path, "dimension 0\n")

    def test_dimension_negative_raises(self, tmp_path):
        with pytest.raises(InstanceFormatError):
            make_inst(tmp_path, "dimension -3\n")

    def test_unknown_line_raises(self, tmp_path):
        # capset instance'i minimal; tanimlanmamis baslik hatadir (katu taraf).
        with pytest.raises(InstanceFormatError):
            make_inst(tmp_path, "dimension 4\nfoo bar\n")

    def test_dimension_extra_tokens_raises(self, tmp_path):
        with pytest.raises(InstanceFormatError):
            make_inst(tmp_path, "dimension 4 5\n")
