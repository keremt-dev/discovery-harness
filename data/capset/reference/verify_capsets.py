"""Pozitif kontrol kumelerinin cap-set (3-AP'siz) dogrulamasi.

data/capset/reference/ altindaki her cap kumesini O(|S|^2) saf-tamsayi
dogrulayicisiyla test eder: (1) her vektor n uzunlugunda {0,1,2};
(2) tekrar yok; (3) 3 FARKLI x,y,z icin x+y+z = 0 (mod 3) ihlali yok.

Bu, P4.0 literatur dogrulamasinin makine-tarafli kanitidir: FunSearch
512-kumesi "altin pozitif kontrol" olarak bagimsiz dogrulanmistir. Cozum
formati (.txt: `#` yorum + bitisik {0,1,2}) ve Python-liste formati
(.pylist) desteklenir. Ayrica ayni kumenin iki formatinin KUME OLARAK
esit oldugunu (set equality) sınar (README iddiasi; Görev 4d).

Kullanim:
    python data/capset/reference/verify_capsets.py
"""

import ast
import sys
from pathlib import Path


def load_solution_text(path):
    """Cozum metnini oku: '#' yorum atla; her satir bitisik {0,1,2}."""
    vecs = []
    for raw in Path(path).read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        vecs.append(tuple(int(c) for c in line))
    return vecs


def load_pylist(path):
    """FunSearch orijinal formati: her satir Python listesi [1,1,1,1,...]."""
    vecs = []
    for raw in Path(path).read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            continue
        vecs.append(tuple(ast.literal_eval(line)))
    return vecs


def check_cap(vecs):
    """(ok, n, |S|, ihlal_sayisi, ornek) dondur. O(|S|^2 * n), saf tamsayi."""
    n = len(vecs[0]) if vecs else 0
    # (1) uzunluk + alfabe
    for v in vecs:
        if len(v) != n:
            return False, n, len(vecs), -1, ("bad_len", v)
        if any(c not in (0, 1, 2) for c in v):
            return False, n, len(vecs), -1, ("bad_alpha", v)
    # (2) tekrar
    if len(set(vecs)) != len(vecs):
        return False, n, len(vecs), -1, ("duplicate",)
    # (3) 3-AP'sizlik: her {x,y} cifti icin z = -(x+y) mod 3
    S = set(vecs)
    L = vecs
    violations = 0
    example = None
    for i in range(len(L)):
        x = L[i]
        for j in range(i + 1, len(L)):
            y = L[j]
            z = tuple((-(a + b)) % 3 for a, b in zip(x, y))
            if z in S and z != x and z != y:
                violations += 1
                if example is None:
                    example = (x, y, z)
    return violations == 0, n, len(vecs), violations, example


# Beklenen degerler (docs/p4-problem-tanimi.md §2 tablosu)
EXPECTED = {
    "optimal_n2_size4.txt": (2, 4, True),
    "optimal_n3_size9.txt": (3, 9, True),
    "optimal_n4_size20.txt": (4, 20, True),
    "funsearch_n8_size512.txt": (8, 512, True),
    "funsearch_n8_size512.pylist": (8, 512, True),
}


def main():
    ref_dir = Path(__file__).parent
    failures = 0
    for fn, (exp_n, exp_size, exp_cap) in EXPECTED.items():
        path = ref_dir / fn
        if not path.exists():
            print(f"  EKSIK: {fn}")
            failures += 1
            continue
        vecs = load_pylist(path) if fn.endswith(".pylist") else load_solution_text(path)
        ok, n, size, viol, example = check_cap(vecs)
        good = (ok == exp_cap and n == exp_n and size == exp_size and viol == 0)
        mark = "OK " if good else "HA!"
        print(f"  [{mark}] {fn}: n={n} |S|={size} cap={ok} ihlal={viol} "
              f"(beklenen n={exp_n} |S|={exp_size})")
        if example is not None:
            print(f"         ornek ihlal: {example}")
        if not good:
            failures += 1

    # Kume-esitligi (Görev 4d): ayni kumenin iki formati (README iddiasi).
    txt = ref_dir / "funsearch_n8_size512.txt"
    pyl = ref_dir / "funsearch_n8_size512.pylist"
    if txt.exists() and pyl.exists():
        same = set(load_solution_text(txt)) == set(load_pylist(pyl))
        mark = "OK " if same else "HA!"
        print(f"  [{mark}] kume-esitligi: funsearch_n8_size512.txt == .pylist")
        if not same:
            failures += 1
    print()
    if failures:
        print(f"BASARISIZ: {failures} kontrol bekleneni saglamiyor.")
        sys.exit(1)
    print("TAMAM: tum pozitif kontrol kumeleri cap-set olarak dogrulandi "
          "(kume-esitligi dahil).")


if __name__ == "__main__":
    main()
