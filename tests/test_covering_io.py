"""problems/covering io testleri: parser SERT — bozuk instance raise eder."""

import pytest

from problems.covering.io import Instance, InstanceFormatError, parse_instance


def write(tmp_path, text, name="cover-v7-k3-t2.cover"):
    f = tmp_path / name
    f.write_text(text, encoding="utf-8")
    return f


class TestParseValid:
    def test_basic(self, tmp_path):
        f = write(tmp_path, "# fano\nv 7\nk 3\nt 2\n")
        inst = parse_instance(f)
        assert inst == Instance(name="cover-v7-k3-t2", v=7, k=3, t=2)

    def test_comments_and_blanks(self, tmp_path):
        f = write(tmp_path, "\n# a\nv 32  # evren\n\nk 8\nt 4 # t\n")
        inst = parse_instance(f)
        assert (inst.v, inst.k, inst.t) == (32, 8, 4)

    def test_name_from_stem(self, tmp_path):
        f = write(tmp_path, "v 13\nk 3\nt 2\n", name="hedef-x.cover")
        assert parse_instance(f).name == "hedef-x"


class TestParseInvalid:
    @pytest.mark.parametrize("text", [
        "v 7\nk 3\n",                    # t eksik
        "k 3\nt 2\n",                    # v eksik
        "v 7\nt 2\n",                    # k eksik
        "",                              # hepsi eksik
    ])
    def test_missing_keys(self, tmp_path, text):
        with pytest.raises(InstanceFormatError, match="eksik"):
            parse_instance(write(tmp_path, text))

    def test_non_integer(self, tmp_path):
        with pytest.raises(InstanceFormatError, match="tamsayi degil"):
            parse_instance(write(tmp_path, "v yedi\nk 3\nt 2\n"))

    @pytest.mark.parametrize("v,k,t", [
        (7, 7, 2),   # v == k
        (7, 3, 3),   # k == t
        (7, 3, 0),   # t < 1
        (3, 5, 2),   # v < k
    ])
    def test_ordering_constraint(self, tmp_path, v, k, t):
        with pytest.raises(InstanceFormatError, match="v > k > t"):
            parse_instance(write(tmp_path, f"v {v}\nk {k}\nt {t}\n"))

    def test_unknown_line(self, tmp_path):
        with pytest.raises(InstanceFormatError, match="bilinmeyen"):
            parse_instance(write(tmp_path, "v 7\nk 3\nt 2\nbudget 5\n"))

    def test_duplicate_key(self, tmp_path):
        with pytest.raises(InstanceFormatError, match="iki kez"):
            parse_instance(write(tmp_path, "v 7\nv 8\nk 3\nt 2\n"))

    def test_extra_value(self, tmp_path):
        with pytest.raises(InstanceFormatError, match="tek deger"):
            parse_instance(write(tmp_path, "v 7 9\nk 3\nt 2\n"))
