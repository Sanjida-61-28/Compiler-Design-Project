EPS = 'ε'

# ---------- Left recursion removal (immediate + indirect) ----------
def remove_left_recursion(g):
    names = list(g)                         # fix an order: A1, A2, A3 ...
    out = {}
    for i, A in enumerate(names):
        alts = g[A]

        # Step 1 (indirect): if a rule starts with an EARLIER nonterminal Aj,
        # replace Aj by its own rules.   A -> Aj x   ==>   A -> (rules of Aj) x
        for Aj in names[:i]:
            new = []
            for a in alts:
                if a and a[0] == Aj:
                    new += [b + a[1:] for b in out[Aj]]
                else:
                    new.append(a)
            alts = new

        # Step 2 (immediate): split into  A -> A alpha  and  A -> beta
        alpha = [a[1:] for a in alts if a and a[0] == A]
        beta = [a for a in alts if not (a and a[0] == A)]
        if not alpha:                       # no left recursion in A
            out[A] = alts
            continue
        if not beta:
            raise ValueError(f"Semantic error: '{A}' has only left-recursive "
                             f"alternatives (no base case)")
        A2 = A + "'"
        out[A] = [b + [A2] for b in beta]               # Rule 1: A  -> beta A'
        out[A2] = [x + [A2] for x in alpha] + [[]]      # Rule 2: A' -> alpha A' | ε
    return out

remove_indirect = remove_left_recursion     # main.py uses this name

# ---------- Left factoring ----------
def common_prefix(alts):
    prefix = []
    for symbols in zip(*alts):
        if len(set(symbols)) > 1:
            break
        prefix.append(symbols[0])
    return prefix

def left_factor(g):
    out, used = {}, set(g)
    work = list(g.items())
    while work:
        A, alts = work.pop(0)
        groups = {}                         # first symbol -> its alternatives
        for a in alts:
            groups.setdefault(a[0] if a else None, []).append(a)

        out[A], new_rules = [], []
        for first, group in groups.items():
            if first is None or len(group) == 1:        # nothing to factor
                out[A] += group
                continue
            prefix = common_prefix(group)               # A -> prefix A'
            A2 = A + "'"
            while A2 in used:
                A2 += "'"
            used.add(A2)
            out[A].append(prefix + [A2])
            rest = [a[len(prefix):] for a in group]     # A' -> the remaining parts
            rest.sort(key=lambda s: s == [])            # ε goes last
            new_rules.append((A2, rest))
        work = new_rules + work             # new rules may need factoring too
    return out

# ---------- Printing ----------
def show(g):
    for A, alts in g.items():
        print(A, '->', ' | '.join(' '.join(a) if a else EPS for a in alts))
        # ---------- Optimization ----------
def remove_duplicates(g):
    """A -> a | a | b   becomes   A -> a | b"""
    out = {}
    for A, alts in g.items():
        out[A] = []
        for a in alts:
            if a not in out[A]:
                out[A].append(a)
    return out