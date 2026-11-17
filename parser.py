import ply.yacc as yacc
from lexer import tokens, errors

# grammar : one or more rules.  Result: a dict  { 'E': [['E','+','T'], ['T']], ... }
def p_grammar(p):
    '''grammar : grammar rule
               | rule'''
    g, rule = (p[1], p[2]) if len(p) == 3 else ({}, p[1])
    g.setdefault(rule[0], []).extend(rule[1])
    p[0] = g

# rule : E -> E + T | T
def p_rule(p):
    'rule : NONTERMINAL ARROW alternatives NEWLINE'
    p[0] = (p[1], p[3])

# alternatives : one or more alternatives separated by |
def p_alternatives(p):
    '''alternatives : alternatives BAR alternative
                    | alternative'''
    p[0] = p[1] + [p[3]] if len(p) == 4 else [p[1]]

# alternative : a list of symbols, or ε (empty list)
def p_alternative_symbols(p):
    'alternative : symbols'
    p[0] = p[1]

def p_alternative_epsilon(p):
    'alternative : EPSILON'
    p[0] = []

# symbols : one or more symbols  ->  ['E', '+', 'T']
def p_symbols(p):
    '''symbols : symbols NONTERMINAL
               | symbols TERMINAL
               | NONTERMINAL
               | TERMINAL'''
    p[0] = p[1] + [p[2]] if len(p) == 3 else [p[1]]

def p_error(p):
    if p:
        errors.append(f"Syntax error at line {p.lineno}: unexpected '{p.value}'")
    else:
        errors.append("Syntax error: unexpected end of input")

def build():
    return yacc.yacc(write_tables=False, debug=False)