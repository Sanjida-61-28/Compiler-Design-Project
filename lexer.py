import ply.lex as lex

tokens = ('NONTERMINAL', 'TERMINAL', 'ARROW', 'BAR', 'EPSILON', 'NEWLINE')

t_ignore = ' \t'                              # spaces and tabs are skipped
errors = []

# simple tokens: name = regular expression
t_BAR = r'\|'
t_EPSILON = r'ε'
t_NONTERMINAL = r"[A-Z][A-Za-z0-9_']*"       # starts with a capital letter: E, T, E'
t_TERMINAL = r'[a-z0-9_+*/()=<>;,\-]+'       # id, +, *, (, ) ...

# ARROW is a function so that it is tried BEFORE t_TERMINAL (which also accepts '-')
def t_ARROW(t):
    r'->'
    return t

def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += len(t.value)            # count lines for error messages
    return t

def t_error(t):
    errors.append(f"Lexical error at line {t.lexer.lineno}: illegal character '{t.value[0]}'")
    t.lexer.skip(1)

def build():
    return lex.lex()