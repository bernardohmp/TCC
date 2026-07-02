import re
from collections import namedtuple

Token = namedtuple('Token', ['type', 'value', 'line', 'column'])

class Lexer:
    def __init__(self, source_code):
        self.source = source_code
        self.pos = 0
        self.line = 1
        self.col = 1
        self.current_char = self.source[0] if self.source else None

        # Definição dos tokens
        self.token_specs = [
                ('NUMBER',    r'\d+'),
                ('IDENT',     r'[a-zA-Z_][a-zA-Z0-9_]*'),
                #tokens de comparacao e assign
                ('LE',        r'<='),
                ('GE',        r'>='),
                ('EQ',        r'=='),
                ('NE',        r'!='),
                ('ASSIGN',    r'='),
                ('LT',        r'<'),
                ('GT',        r'>'),
                #tokens de operacao
                ('PLUS',      r'\+'),
                ('MINUS',     r'-'),
                ('MUL',       r'\*'),
                ('DIV',       r'/'),
                #parenteses e chaves
                ('LPAREN',    r'\('),
                ('RPAREN',    r'\)'),
                ('LBRACE',    r'\{'),
                ('RBRACE',    r'\}'),
                #ponto e virgula(final de comando), virgula, spaco em branco e nova linha
                ('SEMICOLON', r';'),
                ('COMMA',     r','),
                ('SKIP',      r'[ \t]+'),
                ('NEWLINE',   r'\n'),
                ('MISMATCH',  r'.'), # se não atribuir a nada é um erro
        ]
        # Compilar o regex acima
        self.token_re = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in self.token_specs)
        self.regex = re.compile(self.token_re)
    def tokenize(self):
        tokens = []
        for mo in self.regex.finditer(self.source):
            #tipo do token, EQ NE etc
            kind = mo.lastgroup
            #valor especifico, como x,5 ou if
            value = mo.group()
            #pula espaco em branco e avanca 1 coluna
            if kind == 'SKIP':
                self.col += len(value)
                continue
            #pula \n e avanca 1 linha e posiciona a coluna no 1
            elif kind == 'NEWLINE':
                self.line += 1
                self.col = 1
                continue
            #palavras reservadas serao tratadas como seu proprio token em maisculo
            elif kind == 'IDENT' and value in ('if', 'else', 'while','def', 'return'):
                kind = value.upper()
            elif kind == 'MISMATCH':
                raise Exception(f"Erro: Caractere inesperado '{value}' na linha {self.line}, coluna {self.col}")
            # atribui o valor dos tokens
            token = Token(kind, value, self.line, self.col)
            tokens.append(token)
            self.col += len(value)
        #no final adiciona EOF
        tokens.append(Token('EOF', '', self.line, self.col))
        return tokens