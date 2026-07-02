import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARQUIVO_PRINCIPAL = os.path.join(BASE_DIR, 'pontuacao_Principal.txt')
ARQUIVO_SECUNDARIO = os.path.join(BASE_DIR, 'pontuacao_Secundaria.txt')


def calcula_pontuacao(modo,qtd_comandos,tempo):
    if modo =="Principal":
        pontuacao = 2000 - (qtd_comandos *100)
        return pontuacao
    else:
        pontuacao = int(2000 - (tempo*10))
        return pontuacao

def atualizar_linha_se_maior(arquivo_txt, indice_linha, novo_valor):
    # Se o arquivo não existe, cria com zeros para 5 níveis
    if not os.path.exists(arquivo_txt):
        os.makedirs(os.path.dirname(arquivo_txt), exist_ok=True)  # garante que o diretório exista
        with open(arquivo_txt, 'w', encoding='utf-8') as f:
            for _ in range(5):      # 5 níveis
                f.write("0\n")

    # Lê todas as linhas
    with open(arquivo_txt, 'r', encoding='utf-8') as f:
        linhas = f.readlines()

    # Verifica se a linha existe
    if indice_linha < 0 or indice_linha >= len(linhas):
        print("Índice inválido")
        return False

    # Obtém o valor atual da linha
    try:
        valor_atual = float(linhas[indice_linha].strip())
    except ValueError:
        print("A linha não contém um número válido")
        return False

    # Compara e substitui se o novo valor for maior
    if novo_valor > valor_atual:
        linhas[indice_linha] = f"{novo_valor}\n"
        with open(arquivo_txt, 'w', encoding='utf-8') as f:
            f.writelines(linhas)
        return True
    return False