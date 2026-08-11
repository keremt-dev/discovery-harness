"""Aday programi ayri process'te kosturur — probleme-agnostik.

Sozlesme (cvrp-discovery deseninden): aday program
    python <program> <instance_yolu> <cikti_yolu>
ile cagrilir; cwd gecici bir dizindir (repo dosyalarina yazmanin akista
yeri yok). Wall-clock timeout asilirsa process oldurulur; o ana kadar
cikti dosyasina yazilmis cozum KURTARILIR (anytime solver'lar kismi
cozum birakabilir). Runner cozum metnini YORUMLAMAZ; puanlama problem
eklentisinin isidir.

Bilinen sinir (devralindi): Windows'ta subprocess icin ag/bellek izolasyonu
OS duzeyinde zorlanmiyor; tek kullanicili yerel makinede kabul edilen risk.
"""

import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path

STDERR_TAIL = 2000


@dataclass(frozen=True)
class RunResult:
    solution_text: str
    returncode: int | None  # timeout'ta None
    stderr_tail: str
    wall_s: float
    timed_out: bool


def run_candidate(program_path, instance_path, timeout_s,
                  extra_args=None) -> RunResult:
    program = Path(program_path).resolve()
    t0 = time.perf_counter()
    with tempfile.TemporaryDirectory(prefix="discovery-run-") as tmpdir:
        out_path = Path(tmpdir) / "out.txt"
        returncode = None
        stderr_tail = ""
        timed_out = False
        try:
            proc = subprocess.run(
                [sys.executable, str(program), str(instance_path),
                 str(out_path)] + [str(a) for a in (extra_args or [])],
                capture_output=True, text=True, timeout=timeout_s,
                cwd=tmpdir,
            )
            returncode = proc.returncode
            stderr_tail = (proc.stderr or "")[-STDERR_TAIL:]
        except subprocess.TimeoutExpired as exc:
            timed_out = True
            stderr = exc.stderr
            if isinstance(stderr, bytes):
                stderr = stderr.decode("utf-8", errors="replace")
            stderr_tail = (stderr or "")[-STDERR_TAIL:]
        wall_s = time.perf_counter() - t0
        solution_text = ""
        if out_path.exists():
            try:
                solution_text = out_path.read_text(encoding="utf-8")
            except OSError:
                solution_text = ""
    return RunResult(
        solution_text=solution_text,
        returncode=returncode,
        stderr_tail=stderr_tail,
        wall_s=wall_s,
        timed_out=timed_out,
    )
