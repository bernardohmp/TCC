import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROGRESSO_PRINCIPAL = os.path.join(BASE_DIR, 'progresso_Principal.txt')
PROGRESSO_SECUNDARIO = os.path.join(BASE_DIR, 'progresso_Secundario.txt')

def ler_progresso(modo):
    """Retorna o maior nível desbloqueado (1 a 5). Padrão 1."""
    arquivo = PROGRESSO_PRINCIPAL if modo == "Principal" else PROGRESSO_SECUNDARIO
    if not os.path.exists(arquivo):
        return 1
    with open(arquivo, 'r', encoding='utf-8') as f:
        try:
            valor = int(f.read().strip())
            return max(1, min(valor, 5))  # garante entre 1 e 5
        except:
            return 1

def atualizar_progresso(modo, nivel_atual):
    """Desbloqueia o próximo nível se o nível atual for igual ao maior desbloqueado e <5."""
    arquivo = PROGRESSO_PRINCIPAL if modo == "Principal" else PROGRESSO_SECUNDARIO
    desbloqueado = ler_progresso(modo)
    if nivel_atual >= desbloqueado and nivel_atual < 5:
        with open(arquivo, 'w', encoding='utf-8') as f:
            f.write(str(nivel_atual + 1))