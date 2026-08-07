"""P4 eklentisi: cap set (F_3^n icinde 3-AP'siz en buyuk kume).

Sozlesme (CLAUDE.md §3 + problems/capset/CLAUDE.md §3):
SENSE, parse_instance, evaluate_text, penalty_scale. Kofn'deki
re-export deseni aynen kopyalandi (from .io import ..., .objective,
.spec) — boylece harness/registry.load_problem("capset") eklentiyi
probleme-agnostik cekirdek uzerinden yukler (Faz F sinavi).
"""

from .io import Instance, InstanceFormatError, parse_instance
from .objective import evaluate_text
from .spec import SENSE, penalty_scale

__all__ = ["SENSE", "parse_instance", "evaluate_text", "penalty_scale",
           "Instance", "InstanceFormatError"]
