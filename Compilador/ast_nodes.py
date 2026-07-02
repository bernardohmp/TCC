class ASTNode:
    pass

#programa inicial é constituido de statments
class Program(ASTNode):
    def __init__(self, statements):
        self.statements = statements

#Assignment e definido por um identificador e um expressao
class Assignment(ASTNode):
    def __init__(self, identifier, expression):
        self.identifier = identifier
        self.expression = expression

# um if e definido por uma condicao, um bloco then e opicionalmente um bloco else
class If(ASTNode):
    def __init__(self, condition, then_block, else_block=None):
        self.condition = condition
        self.then_block = then_block
        self.else_block = else_block
#while e definido por uma condicao e um body
class While(ASTNode):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body
#um bloco generico e definido por statements
class Block(ASTNode):
    def __init__(self, statements):
        self.statements = statements
#uma operacao binaria e definida pelo operador esquerdo, direito e a opercao em si
class BinaryOp(ASTNode):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right
#variavel possui o proprio nome
class Variable(ASTNode):
    def __init__(self, name):
        self.name = name
#numero possui o proprio valor
class Number(ASTNode):
    def __init__(self, value):
        self.value = value
#uma funcao possui seu nome, parametros e corpo
class FunctionDef(ASTNode):
    def __init__(self, name, params, body):
        self.name = name         
        self.params = params      
        self.body = body          
#o return retorna uma expressao
class Return(ASTNode):
    def __init__(self, expression):
        self.expression = expression
#uma chamada de funcao possui o nome e os argumentos, os argumentos sendo uma lista de expressoes
class FunctionCall(ASTNode):
    def __init__(self, name, arguments):
        self.name = name          
        self.arguments = arguments 