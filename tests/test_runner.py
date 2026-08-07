"""harness/runner.py testleri — aday programi ayri process'te kosturma.

Probleme-agnostik: runner cozum metnini yorumlamaz, yalnizca tasir.
"""

import textwrap

from harness.runner import run_candidate


def write_program(tmp_path, body, name="prog.py"):
    f = tmp_path / name
    f.write_text(textwrap.dedent(body), encoding="utf-8")
    return f


class TestRunCandidate:
    def test_good_program_solution_captured(self, tmp_path):
        prog = write_program(tmp_path, """\
            import sys
            with open(sys.argv[2], "w") as f:
                f.write("10 0 0\\n")
        """)
        rr = run_candidate(prog, "instance-yolu", timeout_s=10)
        assert rr.timed_out is False
        assert rr.returncode == 0
        assert "10 0 0" in rr.solution_text

    def test_failing_program_stderr_captured(self, tmp_path):
        prog = write_program(tmp_path, """\
            import sys
            print("patladim: sebep", file=sys.stderr)
            sys.exit(3)
        """)
        rr = run_candidate(prog, "instance-yolu", timeout_s=10)
        assert rr.returncode == 3
        assert "patladim" in rr.stderr_tail
        assert rr.solution_text == ""

    def test_hanging_program_times_out(self, tmp_path):
        prog = write_program(tmp_path, """\
            import time
            time.sleep(30)
        """)
        rr = run_candidate(prog, "instance-yolu", timeout_s=1)
        assert rr.timed_out is True
        assert rr.solution_text == ""
        assert rr.wall_s < 10

    def test_partial_output_rescued_on_timeout(self, tmp_path):
        # Anytime davranis: solver ciktisini yazip sonra asarsa, yazilan
        # cozum KURTARILIR (cvrp deseninde verdict timeout sonrasi da
        # cikti dosyasindan okunur).
        prog = write_program(tmp_path, """\
            import sys, time
            with open(sys.argv[2], "w") as f:
                f.write("3 3 4\\n")
            time.sleep(30)
        """)
        rr = run_candidate(prog, "instance-yolu", timeout_s=1)
        assert rr.timed_out is True
        assert "3 3 4" in rr.solution_text

    def test_instance_path_passed_as_argv1(self, tmp_path):
        prog = write_program(tmp_path, """\
            import sys
            with open(sys.argv[2], "w") as f:
                f.write(sys.argv[1])
        """)
        rr = run_candidate(prog, "ozel-instance.kofn", timeout_s=10)
        assert "ozel-instance.kofn" in rr.solution_text
