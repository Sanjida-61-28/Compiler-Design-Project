
def left_recursive(g):
    """Return the nonterminals A that can derive A ... (A =>+ A x)."""
    first = {A: {alt[0] for alt in alts if alt and alt[0] in g}
             for A, alts in g.items()}
    result = []
    for A in g:
        reach, todo = set(), list(first[A])
        while todo:
            X = todo.pop()
            if X not in reach:
                reach.add(X)
                todo += first[X]
        if A in reach:
            result.append(A)
    return result

# ---------- 2. Ambiguity check ----------
def find_ambiguity(g, N=9):
    """A grammar is ambiguous if some string has 2 or more leftmost derivations.
    We expand the leftmost nonterminal step by step and count how many
    different derivations reach each sentential form (max length N)."""
    for A in g:
        forms = {(A,): 1}                      # form -> number of derivations
        for _ in range(4 * N):                 # max derivation steps
            nxt, working = {}, False
            for form, count in forms.items():
                i = next((k for k, s in enumerate(form) if s in g), None)
                if i is None:                  # only terminals: finished string
                    nxt[form] = nxt.get(form, 0) + count
                    continue
                working = True
                for alt in g[form[i]]:         # expand the leftmost nonterminal
                    new = form[:i] + tuple(alt) + form[i + 1:]
                    if len(new) <= N:
                        nxt[new] = nxt.get(new, 0) + count
            forms = nxt
            for form, count in forms.items():
                if count >= 2 and all(s not in g for s in form):
                    return A, form             # this string has 2+ derivations
            if not working:
                break
    return None

# ---------- 3. Make the grammar unambiguous ----------
def fresh(g, taken, pool):
    """Pick an unused nonterminal name from pool."""
    for n in pool:
        if n not in g and n not in taken:
            taken.add(n)
            return n

def fix_operators(g, A, taken):
    """E -> E + E | E * E | id   ==>   E -> E + T | T ; T -> T * F | F ; F -> id
    (an operator written earlier gets lower precedence; all are left-associative)"""
    alts = g[A]
    is_binary = lambda a: len(a) >= 3 and a[0] == A and a[-1] == A and A not in a[1:-1]
    ops = []                                   # operators, in order of appearance
    for a in alts:
        if is_binary(a) and tuple(a[1:-1]) not in ops:
            ops.append(tuple(a[1:-1]))
    base = [a for a in alts if not is_binary(a)]
    if not ops or not base:
        return None
    levels = [A] + [fresh(g, taken, 'TFGHKLMNPQ') for _ in ops]
    new = {}
    for k, op in enumerate(ops):               # level k: X -> X op Y | Y
        new[levels[k]] = [[levels[k], *op, levels[k + 1]], [levels[k + 1]]]
    new[levels[-1]] = base                     # last level: the basic items
    return new

def fix_dangling_else(g, A, taken):
    """S -> p S | p S q S | other   (if / if-else)   ==>   matched / unmatched form"""
    alts = g[A]
    for long in alts:                          # long = p S q S
        for k in range(1, len(long) - 2):
            p, q = long[:k], long[k + 1:-1]
            short = p + [A]                    # short = p S
            if long[k] == A and long[-1] == A and short in alts and A not in p + q:
                other = [a for a in alts if a != short and a != long]
                M = fresh(g, taken, 'MPQ')     # matched    (every if has an else)
                U = fresh(g, taken, 'UVW')     # unmatched  (some if has no else)
                return {A: [[M], [U]],
                        M: [p + [M] + q + [M]] + other,
                        U: [short, p + [M] + q + [U]]}
    return None

def make_unambiguous(g):
    g = {A: [list(a) for a in alts] for A, alts in g.items()}
    taken, changed = set(), False
    for A in list(g):
        fixed = fix_dangling_else(g, A, taken) or fix_operators(g, A, taken)
        if fixed:                              # replace A's rule by the new rules
            new_g = {}
            for B, alts in g.items():
                new_g.update(fixed if B == A else {B: alts})
            g, changed = new_g, True
    return g, changed