"""P1 eklentisi: weighted k-out-of-n:G, cok tipli (Ozkut & Tutuncu 2025).

Sozlesme (CLAUDE.md §3): SENSE, parse_instance, evaluate_text, penalty_scale.
"""

from .io import InstanceFormatError, parse_instance
from .objective import evaluate_text
from .spec import SENSE, penalty_scale

__all__ = ["SENSE", "parse_instance", "evaluate_text", "penalty_scale",
           "InstanceFormatError"]
