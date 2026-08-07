"""problems/ altındaki problem eklentilerini yükler ve sözleşmeyi doğrular.

Çekirdek probleme-agnostiktir: bu modülde hiçbir problem adı geçmez.
Eklenti sözleşmesi (CLAUDE.md §3):

    SENSE: "min" | "max"
    parse_instance(path) -> Instance
    evaluate_text(instance, text) -> verdict
    penalty_scale(instance) -> float

Eklentiler `<problems_root>/<name>/__init__.py` paketi olarak yüklenir.
Modül adı çakışmasın diye sys.modules'a "discovery_problems_<name>" olarak
kaydedilir; böylece eklenti içi göreli importlar (from .impl import ...)
standart import mekanizmasıyla çalışır.
"""

import importlib.util
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from harness.score import VALID_SENSES

_MODULE_PREFIX = "discovery_problems_"
_REQUIRED_CALLABLES = ("parse_instance", "evaluate_text", "penalty_scale")


class ProblemNotFoundError(Exception):
    """problems_root altında istenen adda bir eklenti paketi yok."""


class ProblemContractError(Exception):
    """Eklenti yüklendi ama §3 sözleşmesini sağlamıyor."""


@dataclass(frozen=True)
class Problem:
    name: str
    sense: str
    parse_instance: Callable[..., Any]
    evaluate_text: Callable[..., Any]
    penalty_scale: Callable[..., Any]
    module: Any = field(repr=False)


def default_problems_root() -> Path:
    return Path(__file__).resolve().parent.parent / "problems"


def load_problem(name: str, problems_root=None) -> Problem:
    root = Path(problems_root) if problems_root is not None else default_problems_root()
    init_py = root / name / "__init__.py"
    if not init_py.is_file():
        raise ProblemNotFoundError(f"problem eklentisi bulunamadı: {init_py}")

    module_name = _MODULE_PREFIX + name
    spec = importlib.util.spec_from_file_location(
        module_name,
        init_py,
        submodule_search_locations=[str(init_py.parent)],
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        sys.modules.pop(module_name, None)
        raise

    sense = getattr(module, "SENSE", None)
    if sense not in VALID_SENSES:
        raise ProblemContractError(
            f"{name}: SENSE {sense!r} geçersiz; {VALID_SENSES} bekleniyor"
        )
    for attr in _REQUIRED_CALLABLES:
        if not callable(getattr(module, attr, None)):
            raise ProblemContractError(
                f"{name}: sözleşme üyesi {attr!r} yok ya da çağrılabilir değil"
            )

    return Problem(
        name=name,
        sense=sense,
        parse_instance=module.parse_instance,
        evaluate_text=module.evaluate_text,
        penalty_scale=module.penalty_scale,
        module=module,
    )


def list_problems(problems_root=None) -> list:
    root = Path(problems_root) if problems_root is not None else default_problems_root()
    if not root.is_dir():
        return []
    return sorted(
        p.parent.name
        for p in root.glob("*/__init__.py")
        if not p.parent.name.startswith("_")
    )
