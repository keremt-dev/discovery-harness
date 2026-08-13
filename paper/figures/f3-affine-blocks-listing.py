def affine_blocks(v, k, t, rng):
    """All d-flats of AG(m,p) as k-blocks, or None if not applicable."""
    if v > 512:
        return None
    p = None
    for q in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31):
        if v % q == 0:
            p = q
            break
    if p is None:
        return None
    m, x = 0, 1
    while x < v:
        x *= p
        m += 1
    if x != v:
        return None
    d, y = 0, 1
    while y * p <= k:
        y *= p
        d += 1
    if d < t - 1:
        return None

    # digit-wise addition mod p == the translation group of AG(m,p)
    add = []
    for a in range(v):
        row = [0] * v
        for b in range(v):
            s, mul, aa, bb = 0, 1, a, b
            for _ in range(m):
                s += (((aa % p) + (bb % p)) % p) * mul
                aa //= p
                bb //= p
                mul *= p
            row[b] = s
        add.append(row)

    # all d-dimensional linear subspaces, by repeated closure
    spans = [frozenset((0,))]
    for _ in range(d):
        seen = set()
        nxt = []
        for sp in spans:
            for g in range(1, v):
                if g in sp:
                    continue
                ns = set(sp)
                cur = 0
                for _ in range(p - 1):
                    cur = add[cur][g]
                    arow = add[cur]
                    for s in sp:
                        ns.add(arow[s])
                fs = frozenset(ns)
                if fs not in seen:
                    seen.add(fs)
                    nxt.append(fs)
        spans = nxt
        if not spans:
            return None

    # cosets => the d-flats
    seenb = set()
    out = []
    for sp in spans:
        for a in range(v):
            arow = add[a]
            blk = tuple(sorted(arow[s] for s in sp))
            if blk not in seenb:
                seenb.add(blk)
                out.append(blk)
    if not out:
        return None

    pad = k - len(out[0])
    if pad > 0:
        res = []
        for blk in out:
            inb = set(blk)
            pool = [z for z in range(v) if z not in inb]
            rng.shuffle(pool)
            res.append(tuple(sorted(blk + tuple(pool[:pad]))))
        out = res
    return out
