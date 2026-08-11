"""P5 eklentisi: (v,k,t) covering design — minimum blok sayisi.

Sozlesme (CLAUDE.md §3): SENSE, parse_instance, evaluate_text,
penalty_scale. kofn/capset re-export deseni aynen — harness/registry
eklentiyi probleme-agnostik cekirdek uzerinden yukler (harness/ icinde
TEK SATIR degisiklik olmadan; Faz F sinavi kuralı).

Hedef hucre kurasyonu: data/covering/reference/curate_targets.py
(LJCR arsivi; dondu 2026-03-01, canli skorbord coveringrepository.com).
"""

from .io import Instance, InstanceFormatError, parse_instance
from .objective import evaluate_text
from .spec import SENSE, penalty_scale, schoenheim

__all__ = ["SENSE", "parse_instance", "evaluate_text", "penalty_scale",
           "schoenheim", "Instance", "InstanceFormatError"]
