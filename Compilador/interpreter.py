from Compilador.ast_nodes import *

class ReturnException(Exception):
    def __init__(self, value):
        self.value = value

class Interpreter:
    MAX_MOVES=150
    MAX_STEPS = 2000
    def __init__(self):
        #guardar as variaveis, funcoes criadas pelo usuario e funcoes ja existentes, de movimentacao
        self.variables = {}
        self.functions = {}
        self.builtins = {
            'move_right': self.builtin_move_right,
            'move_left': self.builtin_move_left,
            'move_up': self.builtin_move_up,
            'move_down': self.builtin_move_down
        }
        self.moves = []
        self.step_count = 0 
    #funcao inicial de visita, ela achara a funcao especifica de acordo com o tipo do node
    def visit(self, node):
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_visit) #visitara a funcao correspondente, se nao achar vai para a excessao "generic_visit"
        return visitor(node)

    def generic_visit(self, node):
        print(f'Nenhum método visit_{type(node).__name__} definido')
        return None

    def visit_Program(self, node):
        # Primeiro, registrar todas as definições de função
        for item in node.statements:
            if isinstance(item, FunctionDef):
                self.functions[item.name] = item
        # Depois, executar os comandos de nível superior (que não são definições)
        for item in node.statements:
            if not isinstance(item, FunctionDef):
                self.visit(item)

    def visit_FunctionDef(self, node):
        # Já registrada em visit_Program, não faz nada aqui
        pass
    # para o assignment(ident = express)
    def visit_Assignment(self, node):
        value = self.visit(node.expression)
        self.variables[node.identifier] = value
    #verifica a condicao, se verdadeira executa o if, senão, se houver um bloco else o executa
    def visit_If(self, node):
        cond = self.visit(node.condition)
        if cond:
            self.visit(node.then_block)
        elif node.else_block:
            self.visit(node.else_block)
    #enquanto a condicao do while for verdadeira, continua a executar o body
    def visit_While(self, node):
        while self.visit(node.condition):
            self.step_count += 1
            if self.step_count > self.MAX_STEPS:
                raise Exception("Limite de operações excedido. Possível loop infinito.")
            self.visit(node.body)
    #em um bloco visita statment a statmente o executando
    def visit_Block(self, node):
        for stmt in node.statements:
            self.visit(stmt)
    #trata as operacoes com 2 operadores, sejam comparativas ou de operacao
    def visit_BinaryOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        op = node.op
        if op == '+': return left + right
        elif op == '-': return left - right
        elif op == '*': return left * right
        elif op == '/': return left // right  # inteiro
        elif op == '==': return left == right
        elif op == '!=': return left != right
        elif op == '<': return left < right
        elif op == '>': return left > right
        elif op == '<=': return left <= right
        elif op == '>=': return left >= right
        else:
            raise Exception(f'Operador desconhecido {op}')
    #retorna o nome da variavel
    def visit_Variable(self, node):
        if node.name in self.variables:
            return self.variables[node.name]
        else:
            raise Exception(f"Variável '{node.name}' não definida")
    #retorna o valor do numero
    def visit_Number(self, node):
        return node.value
    #retorna o valor da expressao atribuida ao return
    def visit_Return(self, node):
        value = self.visit(node.expression)
        raise ReturnException(value)

    def visit_FunctionCall(self, node):
        # Avalia os argumentos primeiro (podem conter outras chamadas)
        arg_values = [self.visit(arg) for arg in node.arguments]

        # Verifica se é uma função embutida
        if node.name in self.builtins:
            return self.builtins[node.name](arg_values)

        #Caso contrário, procura nas funções definidas
        if node.name not in self.functions:
            raise Exception(f"Função '{node.name}' não definida")
        try:
            func_def = self.functions[node.name]
        except:
           raise Exception("Erro no nome da funcao")
        if len(arg_values) != len(func_def.params):
            raise Exception(f"Função '{node.name}' espera {len(func_def.params)} argumentos, mas {len(arg_values)} foram fornecidos")

        # Salva escopo anterior
        previous_vars = self.variables.copy()
        # Novo escopo com os parâmetros
        self.variables.update(dict(zip(func_def.params, arg_values)))

        try:
            self.visit(func_def.body)
            result = 0  # valor padrão se não houver return
        except ReturnException as ret:
            result = ret.value
        finally:
            self.variables = previous_vars

        return result

    #definicao das funcoes embutidas, ate o momento so imprime na tela as direcoes
    def builtin_move_right(self, args):
        if len(args) != 0:
            raise Exception("move_right() não aceita argumentos")
        if len(self.moves) > self.MAX_MOVES:
            raise Exception("Numero maximo de comandos atingido, provavel looping infinito")
        self.moves.append('move_right')
        return 0

    def builtin_move_left(self, args):
        if len(args) != 0:
            raise Exception("move_left() não aceita argumentos")
        if len(self.moves) > self.MAX_MOVES:
            raise Exception("Numero maximo de comandos atingido, provavel looping infinito")
        self.moves.append('move_left')
        return 0

    def builtin_move_up(self, args):
        if len(args) != 0:
            raise Exception("move_up() não aceita argumentos")
        if len(self.moves) > self.MAX_MOVES:
            raise Exception("Numero maximo de comandos atingido, provavel looping infinito")
        self.moves.append('move_up')
        return 0

    def builtin_move_down(self, args):
        if len(args) != 0:
            raise Exception("move_down() não aceita argumentos")
        if len(self.moves) > self.MAX_MOVES:
            raise Exception("Numero maximo de comandos atingido, provavel looping infinito")
        self.moves.append('move_down')
        return 0