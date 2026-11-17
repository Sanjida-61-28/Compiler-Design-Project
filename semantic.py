def build_symbol_table(grammar):
    """name -> {'type': 'NT' or 'T', 'used_in': rules whose right side uses it}"""
    table = {A: {'type': 'NT', 'used_in': []} for A in grammar}
    for lhs, alts in grammar.items():
        for alt in alts:
            for s in alt:
                kind = 'NT' if s[0].isupper() else 'T'     # capital letter = nonterminal
                entry = table.setdefault(s, {'type': kind, 'used_in': []})
                if lhs not in entry['used_in']:
                    entry['used_in'].append(lhs)
    return table

def print_table(table):
    print(f"{'Name':<8}{'Type':<6}Used in rules of")
    for name, e in table.items():
        print(f"{name:<8}{e['type']:<6}{', '.join(e['used_in']) or '-'}")

def semantic_check(grammar, table):
    errors, warnings = [], []

    # Check 1: a nonterminal is used but has no rule of its own
    for name, e in table.items():
        if e['type'] == 'NT' and name not in grammar:
            warnings.append(f"Semantic warning: nonterminal '{name}' is used "
                            f"(in rules of: {', '.join(e['used_in'])}) but has no rule")

    # Check 2: every alternative is left-recursive, so there is no base case (E -> E a)
    for A, alts in grammar.items():
        if all(a and a[0] == A for a in alts):
            errors.append(f"Semantic error: '{A}' has only left-recursive "
                          f"alternatives (no base case)")
    return errors, warnings