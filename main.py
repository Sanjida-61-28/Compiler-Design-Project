import argparse, sys
import lexer, parser as gparser
from transform import remove_indirect, left_factor, show, remove_duplicates
from semantic import build_symbol_table, print_table, semantic_check
from ambiguity import find_ambiguity, make_unambiguous, left_recursive

def main():
    sys.stdout.reconfigure(encoding='utf-8')

    ap = argparse.ArgumentParser()
    ap.add_argument('file')
    ap.add_argument('-tokens', action='store_true')
    ap.add_argument('-symtab', action='store_true')
    ap.add_argument('-lr', action='store_true',
                    help='skip the ambiguity check; only remove left recursion + left factoring')
    ap.add_argument('-opt', action='store_true',
                    help='only run the optimization (remove duplicate alternatives)')
    ap.add_argument('-len', type=int, default=9, dest='maxlen',
                    help='max string length for the ambiguity search')
    args = ap.parse_args()

    data = open(args.file, encoding='utf-8-sig').read().strip() + '\n'
    lx = lexer.build()

    if args.tokens:
        lx.input(data)
        for tok in lx:
            print(f"{tok.type:12} {tok.value!r:10} line {tok.lineno}")
        lexer.errors.clear()
        lx.lineno = 1

    lx.lineno = 1
    ps = gparser.build()
    grammar = ps.parse(data, lexer=lx)

    if lexer.errors or grammar is None:
        print('\n'.join(lexer.errors))
        sys.exit(1)

    table = build_symbol_table(grammar)
    if args.symtab:
        print_table(table)
        print()
    errors, warnings = semantic_check(grammar, table)
    for w in warnings:
        print(w, file=sys.stderr)
    if errors:
        print('\n'.join(errors))
        sys.exit(1)

    # Optimization: remove duplicate alternatives
    grammar = remove_duplicates(grammar)
    if args.opt:                      # -opt: only the optimization
        show(grammar)
        return

    # -lr: only left recursion removal + left factoring
    if args.lr:
        try:
            show(left_factor(remove_indirect(grammar)))
        except ValueError as e:
            print(e)
            sys.exit(1)
        return

    N = args.maxlen
    result = find_ambiguity(grammar, N)

    # Case 1: not ambiguous -> print only this line
    if result is None:
        print("Not Ambiguous")
        return

    # Case 2: ambiguous -> apply the rules and show the unambiguous grammar
    print("Grammar is AMBIGUOUS.")
    print("\nOriginal grammar:")
    show(grammar)

    unamb, changed = make_unambiguous(grammar)
    if not changed:
        print("\nCould not remove this ambiguity automatically "
              "(supported: operator precedence/associativity, dangling else).")
        sys.exit(1)

    print("\nStep 1 - Remove ambiguity (precedence / matched-unmatched rule):")
    show(unamb)

    try:
        current = unamb
        step = 2
        lrec = left_recursive(current)
        if lrec:
            print(f"\nStep {step} - Remove left recursion (found in: {', '.join(lrec)})")
            print("  Rule 1: A -> A a | b   becomes   A -> b A'")
            print("  Rule 2:                          A' -> a A' | ε")
            current = remove_indirect(current)
            show(current)
            step += 1
        final = left_factor(current)
        if final != current:
            print(f"\nStep {step} - Left factoring:")
            show(final)
            current = final

        print("\nFinal unambiguous grammar:")
        show(current)
    except ValueError as e:
        print(e)
        sys.exit(1)

if __name__ == '__main__':
    main()