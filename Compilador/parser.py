from Compilador.lexer import Lexer
from Compilador.ast_nodes import *


class Parser:
    #comeca no token 0
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current_token = self.tokens[0]
        self.flag = 0

    #funcao simples eat, apenas verifica se o tipo do token é o tipo esperado
    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.pos += 1
            if self.pos < len(self.tokens):
                self.current_token = self.tokens[self.pos]
            return self.tokens[self.pos - 1]
        else:
            raise SyntaxError(
                f"Esperado {token_type}, encontrado {self.current_token.type} "
                f"na linha {self.current_token.line}"
        )

    # Regras da gramática
    def parse(self):
        items = []
        while self.current_token.type != 'EOF':
            #se o token for um def, estamos definindo funcao
            if self.current_token.type == 'DEF':
                items.append(self.function_definition())
            # senao o token e um statment
            else:
                items.append(self.statement())
        return Program(items)

    def statement(self):
    # Comandos que começam com palavras-chave especificas
        if self.current_token.type == 'IF':
            return self.if_statement()
        elif self.current_token.type == 'WHILE':
            return self.while_statement()
        elif self.current_token.type == 'RETURN':
            self.eat('RETURN')
            expr = self.expression()
            self.eat('SEMICOLON')
            return Return(expr)
        elif self.current_token.type == 'LBRACE':
            return self.block()
        else:
            # Se for um IDENT, pode ser atribuicao ou chamada de funcao
            if self.current_token.type == 'IDENT':
                # Olha o próximo token sem consumir
                if self.pos + 1 < len(self.tokens) and self.tokens[self.pos + 1].type == 'ASSIGN':
                    # É uma atribuicao: ident = expr ;
                    var_name = self.eat('IDENT').value
                    self.eat('ASSIGN')
                    expr = self.expression()
                    self.eat('SEMICOLON')
                    return Assignment(var_name, expr)
                else:
                    # É uma expressao começando com IDENT ex chamada de função
                    expr = self.expression()
                    self.eat('SEMICOLON')
                    return expr
            else:
                # Qualquer outra expressao ex 2+2;
                expr = self.expression()
                self.eat('SEMICOLON')
                return expr
    #um bloco sempre tera a estrutura {statments}
    def block(self):
        self.eat('LBRACE')
        statements = []
        while self.current_token.type != 'RBRACE':
            statements.append(self.statement())
        self.eat('RBRACE')
        return Block(statements)
    #um if sempre tera a estrutura if (expressao) bloco (else bloco) opcional
    def if_statement(self):
        self.eat('IF')
        self.eat('LPAREN')
        condition = self.expression()
        self.eat('RPAREN')
        then_block = self.statement()  # pode ser bloco ou comando simples
        else_block = None
        if self.current_token.type == 'ELSE':
            self.eat('ELSE')
            else_block = self.statement()
        return If(condition, then_block, else_block)
    #um while tera a estrutura while(expressao) {statment}
    def while_statement(self):
        self.eat('WHILE')
        self.eat('LPAREN')
        condition = self.expression()
        self.eat('RPAREN')
        body = self.statement()
        return While(condition, body)

    # Expressões com precedência 
    def expression(self):
        return self.comparison()   
    #comparacoes como == != ou <
    def comparison(self):    
        node = self.addition()
        while self.current_token.type in ('EQ', 'NE', 'LT', 'GT', 'LE', 'GE'):
            op = self.current_token.value
            self.eat(self.current_token.type)
            node = BinaryOp(node, op, self.addition())
        return node
    #adicao e subtracao
    def addition(self):
        node = self.term()
        while self.current_token.type in ('PLUS', 'MINUS'):
            op = self.current_token.value
            self.eat(self.current_token.type)
            node = BinaryOp(node, op, self.term())
        return node
    #termo como multiplicacao e divisao
    def term(self):
        node = self.factor()
        while self.current_token.type in ('MUL', 'DIV'):
            op = self.current_token.value
            self.eat(self.current_token.type)
            node = BinaryOp(node, op, self.factor())
        return node
    # um fator pode ser um numero, uma atribuicao ou uma chamada de funcao
    def factor(self):
        token = self.current_token
        if token.type == 'NUMBER':
            self.eat('NUMBER')
            return Number(int(token.value))
        elif token.type == 'IDENT':
            self.eat('IDENT')
            # Se após o identificador ouver um parenteses, e uma chamada de funcao
            if self.current_token.type == 'LPAREN':
                self.eat('LPAREN')
                args = []
                if self.current_token.type != 'RPAREN':
                    args.append(self.expression())
                    while self.current_token.type == 'COMMA':
                        self.eat('COMMA')
                        args.append(self.expression())
                self.eat('RPAREN')
                return FunctionCall(token.value, args)
            else:
                return Variable(token.value)
        elif token.type == 'LPAREN':
            self.eat('LPAREN')
            node = self.expression()
            self.eat('RPAREN')
            return node
        else:
            raise SyntaxError(f"Fator inesperado: {token.type} na linha {token.line}")
    #definicao de funcao na forma def nome(parametros){expressao}
    def function_definition(self):
        self.eat('DEF')
        func_name = self.eat('IDENT').value
        self.eat('LPAREN')
        params = []
        if self.current_token.type != 'RPAREN':
            params.append(self.eat('IDENT').value)
            while self.current_token.type == 'COMMA':
                self.eat('COMMA')
                params.append(self.eat('IDENT').value)
        self.eat('RPAREN')
        body = self.block()   # corpo da função é um bloco
        return FunctionDef(func_name, params, body)