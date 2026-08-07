"""problems/ eklenti yükleyicisi (harness/registry.py) testleri.

Sözleşme (CLAUDE.md §3): her eklenti SENSE ("min"|"max") ve üç çağrılabilir
(parse_instance, evaluate_text, penalty_scale) sağlamak zorunda. Çekirdek
probleme-agnostiktir: registry hiçbir problem adı bilmez, yalnızca verilen
kökteki paketleri yükleyip sözleşmeyi doğrular.
"""

import textwrap

import pytest

from harness.registry import (
    ProblemContractError,
    ProblemNotFoundError,
    list_problems,
    load_problem,
)

VALID_INIT = """\
    from .impl import evaluate_text

    SENSE = "max"

    def parse_instance(path):
        return {"path": str(path)}

    def penalty_scale(instance):
        return 2.0
"""

VALID_IMPL = """\
    def evaluate_text(instance, text):
        return {
            "feasible": True, "cost": 1.0, "violations": {},
            "fitness": 1.0, "eval_ms": 0, "info": {},
        }
"""


def make_plugin(root, name, init_src, extra_files=None):
    plugin_dir = root / name
    plugin_dir.mkdir(parents=True)
    (plugin_dir / "__init__.py").write_text(
        textwrap.dedent(init_src), encoding="utf-8"
    )
    for fname, src in (extra_files or {}).items():
        (plugin_dir / fname).write_text(textwrap.dedent(src), encoding="utf-8")
    return plugin_dir


class TestLoadProblem:
    def test_loads_valid_plugin_with_relative_import(self, tmp_path):
        # Göreli import (from .impl import ...) kofn'un gerçek yapısını taklit
        # eder; paket mekaniği çalışmıyorsa burada patlar.
        make_plugin(tmp_path, "dummymax", VALID_INIT, {"impl.py": VALID_IMPL})

        problem = load_problem("dummymax", problems_root=tmp_path)

        assert problem.name == "dummymax"
        assert problem.sense == "max"
        instance = problem.parse_instance("foo.txt")
        verdict = problem.evaluate_text(instance, "çözüm metni")
        assert verdict["feasible"] is True
        assert problem.penalty_scale(instance) == 2.0

    def test_unknown_problem_raises_not_found(self, tmp_path):
        with pytest.raises(ProblemNotFoundError):
            load_problem("boyle_bir_problem_yok", problems_root=tmp_path)

    def test_missing_contract_attribute_raises(self, tmp_path):
        make_plugin(
            tmp_path,
            "eksik",
            """\
            SENSE = "max"

            def parse_instance(path):
                return {}

            def evaluate_text(instance, text):
                return {}
            """,
        )
        with pytest.raises(ProblemContractError, match="penalty_scale"):
            load_problem("eksik", problems_root=tmp_path)

    def test_invalid_sense_raises(self, tmp_path):
        make_plugin(
            tmp_path,
            "yanlis_sense",
            """\
            SENSE = "maximize"

            def parse_instance(path):
                return {}

            def evaluate_text(instance, text):
                return {}

            def penalty_scale(instance):
                return 1.0
            """,
        )
        with pytest.raises(ProblemContractError, match="SENSE"):
            load_problem("yanlis_sense", problems_root=tmp_path)

    def test_non_callable_contract_member_raises(self, tmp_path):
        make_plugin(
            tmp_path,
            "cagirilamaz",
            """\
            SENSE = "min"
            parse_instance = 5

            def evaluate_text(instance, text):
                return {}

            def penalty_scale(instance):
                return 1.0
            """,
        )
        with pytest.raises(ProblemContractError, match="parse_instance"):
            load_problem("cagirilamaz", problems_root=tmp_path)


class TestListProblems:
    def test_lists_only_packages(self, tmp_path):
        make_plugin(tmp_path, "aaa", VALID_INIT, {"impl.py": VALID_IMPL})
        make_plugin(tmp_path, "bbb", VALID_INIT, {"impl.py": VALID_IMPL})
        (tmp_path / "paket_degil").mkdir()  # __init__.py yok
        (tmp_path / "dosya.txt").write_text("x", encoding="utf-8")

        assert list_problems(problems_root=tmp_path) == ["aaa", "bbb"]

    def test_empty_or_missing_root_gives_empty_list(self, tmp_path):
        assert list_problems(problems_root=tmp_path / "yok") == []
