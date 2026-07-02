import os
import pygame, sys
from button import Button
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Compilador.main import Game
from Compilador.pontuacao import ARQUIVO_PRINCIPAL, ARQUIVO_SECUNDARIO
from Compilador.progresso import ler_progresso, atualizar_progresso

pygame.init()

# Resolução 
DESIGN_LARGURA = 1920
DESIGN_ALTURA = 1280

# Tela fullscreen
SCREEN = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
NATIVA_LARGURA, NATIVA_ALTURA = SCREEN.get_size()
pygame.display.set_caption("Menu")

# Fatores de escala
ESCALA_X = NATIVA_LARGURA / DESIGN_LARGURA
ESCALA_Y = NATIVA_ALTURA / DESIGN_ALTURA

def escala_x(valor):
    """Converte uma coordenada X do design para a resolução nativa."""
    return int(valor * ESCALA_X)

def escala_y(valor):
    """Converte uma coordenada Y do design para a resolução nativa."""
    return int(valor * ESCALA_Y)

def escala_fonte(tamanho):
    """Retorna um tamanho de fonte escalado (mínimo 12)."""
    return max(12, int(tamanho * min(ESCALA_X, ESCALA_Y)))

# Carrega e redimensiona o fundo para cobrir a tela inteira
BG = pygame.image.load("Interface/assets/Background.png")
BG = pygame.transform.smoothscale(BG, (NATIVA_LARGURA, NATIVA_ALTURA))

def get_font(size):
    return pygame.font.Font("Interface/assets/font.ttf", escala_fonte(size))

def play():
    x = True
    while x:
        MOUSE_POS = pygame.mouse.get_pos()
        SCREEN.fill("black")

        MODO_TEXT = get_font(45).render("Escolha um modo", True, "white")
        MODO_RECT = MODO_TEXT.get_rect(center=(NATIVA_LARGURA // 2, escala_y(60)))
        SCREEN.blit(MODO_TEXT, MODO_RECT)

        MODO_PRINCIPAL = Button(image=None, pos=(NATIVA_LARGURA // 2, escala_y(260)),
                                text_input="MODO PRINCIPAL", font=get_font(50),
                                base_color="white", hovering_color="Green")
        MODO_SECUNDARIO = Button(image=None, pos=(NATIVA_LARGURA // 2, escala_y(460)),
                                 text_input="MODO SECUNDARIO", font=get_font(50),
                                 base_color="white", hovering_color="Green")

        MODO_PRINCIPAL.changeColor(MOUSE_POS)
        MODO_PRINCIPAL.update(SCREEN)
        MODO_SECUNDARIO.changeColor(MOUSE_POS)
        MODO_SECUNDARIO.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                x = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if MODO_PRINCIPAL.checkForInput(MOUSE_POS):
                    modo_principal()
                if MODO_SECUNDARIO.checkForInput(MOUSE_POS):
                    modo_secundario()

        pygame.display.update()

def modo_principal():
    tilesizes = {1: 256, 2: 160, 3: 128, 4: 128, 5: 64}
    nivel_escolhido = None
    nivel_desbloqueado = ler_progresso("Principal")

    while nivel_escolhido is None:
        MOUSE_POS = pygame.mouse.get_pos()
        SCREEN.fill("black")

        MODO_TEXT = get_font(45).render("Escolha um nível", True, "white")
        MODO_RECT = MODO_TEXT.get_rect(center=(NATIVA_LARGURA // 2, escala_y(60)))
        SCREEN.blit(MODO_TEXT, MODO_RECT)

        posicoes = {
            1: (escala_x(460), escala_y(260)),
            2: (escala_x(460), escala_y(460)),
            3: (escala_x(1460), escala_y(260)),
            4: (escala_x(1460), escala_y(460)),
            5: (NATIVA_LARGURA // 2, escala_y(660))
        }
        botoes = []
        for i in range(1, 6):
            if i <= nivel_desbloqueado:
                cor = "white"
                hover = "Green"
                bloqueado = False
            else:
                cor = "gray"
                hover = "gray"
                bloqueado = True
            btn = Button(image=None, pos=posicoes[i],
                         text_input=f"NÍVEL {i}", font=get_font(50),
                         base_color=cor, hovering_color=hover)
            botoes.append((i, btn, bloqueado))

        for _, btn, _ in botoes:
            btn.changeColor(MOUSE_POS)
            btn.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                for i, btn, bloqueado in botoes:
                    if not bloqueado and btn.checkForInput(MOUSE_POS):
                        nivel_escolhido = i
                        break

        pygame.display.update()

    nivel_atual = nivel_escolhido
    while nivel_atual <= 5:
        game = Game("Principal", nivel_atual, tilesizes[nivel_atual])
        game.run()

        if game.victory:
            atualizar_progresso("Principal", nivel_atual)
            acao = tela_vitoria(game)
            if acao == "menu":
                return
            elif acao == "proximo":
                nivel_atual += 1
        else:
            return

def modo_secundario():
    tilesizes = {1: 256, 2: 160, 3: 128, 4: 128, 5: 64}
    nivel_escolhido = None
    nivel_desbloqueado = ler_progresso("Secundario")

    while nivel_escolhido is None:
        MOUSE_POS = pygame.mouse.get_pos()
        SCREEN.fill("black")

        MODO_TEXT = get_font(45).render("Escolha um nível", True, "white")
        MODO_RECT = MODO_TEXT.get_rect(center=(NATIVA_LARGURA // 2, escala_y(60)))
        SCREEN.blit(MODO_TEXT, MODO_RECT)

        posicoes = {
            1: (escala_x(460), escala_y(260)),
            2: (escala_x(460), escala_y(460)),
            3: (escala_x(1460), escala_y(260)),
            4: (escala_x(1460), escala_y(460)),
            5: (NATIVA_LARGURA // 2, escala_y(660))
        }
        botoes = []
        for i in range(1, 6):
            if i <= nivel_desbloqueado:
                cor = "white"
                hover = "Green"
                bloqueado = False
            else:
                cor = "gray"
                hover = "gray"
                bloqueado = True
            btn = Button(image=None, pos=posicoes[i],
                         text_input=f"NÍVEL {i}", font=get_font(50),
                         base_color=cor, hovering_color=hover)
            botoes.append((i, btn, bloqueado))

        for _, btn, _ in botoes:
            btn.changeColor(MOUSE_POS)
            btn.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                for i, btn, bloqueado in botoes:
                    if not bloqueado and btn.checkForInput(MOUSE_POS):
                        nivel_escolhido = i
                        break

        pygame.display.update()

    nivel_atual = nivel_escolhido
    while nivel_atual <= 5:
        game = Game("Secundario", nivel_atual, tilesizes[nivel_atual])
        game.run()

        if game.victory:
            atualizar_progresso("Secundario", nivel_atual)
            acao = tela_vitoria(game)
            if acao == "menu":
                return
            elif acao == "proximo":
                nivel_atual += 1
        else:
            return

def ler_pontuacoes(caminho_arquivo):
    """Retorna uma lista com as pontuações (float) de cada nível (5 níveis)."""
    if not os.path.exists(caminho_arquivo):
        return [0.0] * 5
    with open(caminho_arquivo, 'r', encoding='utf-8') as f:
        linhas = f.readlines()
    pontuacoes = []
    for i in range(5):
        if i < len(linhas):
            try:
                pontuacoes.append(float(linhas[i].strip()))
            except ValueError:
                pontuacoes.append(0.0)
        else:
            pontuacoes.append(0.0)
    return pontuacoes

def Pontuacao():
    while True:
        PONTUACAO_MOUSE_POS = pygame.mouse.get_pos()
        SCREEN.fill("black")

        TITLE_TEXT = get_font(70).render("PONTUAÇÕES", True, "gold")
        TITLE_RECT = TITLE_TEXT.get_rect(center=(NATIVA_LARGURA // 2, escala_y(80)))
        SCREEN.blit(TITLE_TEXT, TITLE_RECT)

        PONTUACAO_BACK = Button(image=None, pos=(NATIVA_LARGURA // 2, escala_y(1200)),
                                text_input="VOLTAR", font=get_font(60),
                                base_color="white", hovering_color="green")
        PONTUACAO_BACK.changeColor(PONTUACAO_MOUSE_POS)
        PONTUACAO_BACK.update(SCREEN)

        principal = ler_pontuacoes(ARQUIVO_PRINCIPAL)
        secundario = ler_pontuacoes(ARQUIVO_SECUNDARIO)

        col_esq_x = escala_x(300)
        col_dir_x = escala_x(1100)
        y_inicial = escala_y(220)
        espacamento = escala_y(100)
        separacao_valor = escala_x(450)

        header_principal = get_font(50).render("Modo Principal", True, "cyan")
        header_secundario = get_font(50).render("Modo Secundário", True, "orange")
        SCREEN.blit(header_principal, (col_esq_x, y_inicial - escala_y(70)))
        SCREEN.blit(header_secundario, (col_dir_x, y_inicial - escala_y(70)))

        for nivel in range(5):
            y = y_inicial + nivel * espacamento

            nivel_txt = f"Nível {nivel+1}:"
            nivel_surf = get_font(35).render(nivel_txt, True, "white")
            SCREEN.blit(nivel_surf, (col_esq_x, y))
            pts_p = f"{principal[nivel]:.0f}"
            pts_p_surf = get_font(35).render(pts_p, True, "white")
            SCREEN.blit(pts_p_surf, (col_esq_x + separacao_valor, y))

            SCREEN.blit(nivel_surf, (col_dir_x, y))
            pts_s = f"{secundario[nivel]:.0f}"
            pts_s_surf = get_font(35).render(pts_s, True, "lightyellow")
            SCREEN.blit(pts_s_surf, (col_dir_x + separacao_valor, y))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PONTUACAO_BACK.checkForInput(PONTUACAO_MOUSE_POS):
                    main_menu()

        pygame.display.update()

def tela_vitoria(game):
    """Exibe a tela de vitória e retorna 'menu' ou 'proximo'."""
    tem_proximo = game.nivel < 5

    while True:
        SCREEN.fill("black")
        MOUSE_POS = pygame.mouse.get_pos()

        titulo = get_font(70).render("VOCÊ VENCEU!", True, "gold")
        titulo_rect = titulo.get_rect(center=(NATIVA_LARGURA // 2, escala_y(200)))
        SCREEN.blit(titulo, titulo_rect)

        pontos_text = get_font(50).render(f"Pontuação: {game.pontuacao_final}", True, "white")
        pontos_rect = pontos_text.get_rect(center=(NATIVA_LARGURA // 2, escala_y(350)))
        SCREEN.blit(pontos_text, pontos_rect)

        btn_menu = Button(image=None, pos=(NATIVA_LARGURA // 2, escala_y(550)),
                          text_input="MENU", font=get_font(60),
                          base_color="white", hovering_color="green")
        btn_menu.changeColor(MOUSE_POS)
        btn_menu.update(SCREEN)

        btn_proximo = None
        if tem_proximo:
            btn_proximo = Button(image=None, pos=(NATIVA_LARGURA // 2, escala_y(700)),
                                 text_input="PRÓXIMO NÍVEL", font=get_font(60),
                                 base_color="white", hovering_color="cyan")
            btn_proximo.changeColor(MOUSE_POS)
            btn_proximo.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_menu.checkForInput(MOUSE_POS):
                    return "menu"
                if tem_proximo and btn_proximo.checkForInput(MOUSE_POS):
                    return "proximo"

        pygame.display.update()

def main_menu():
    while True:
        SCREEN.fill("black")
        SCREEN.blit(BG, (0, 0))
        MENU_MOUSE_POS = pygame.mouse.get_pos()

        MENU_TEXT = get_font(100).render("MAIN MENU", True, "#b68f40")
        MENU_RECT = MENU_TEXT.get_rect(center=(NATIVA_LARGURA // 2, escala_y(100)))
        SCREEN.blit(MENU_TEXT, MENU_RECT)

        # Botões com imagens escaladas
        play_img = pygame.image.load("Interface/assets/Play Rect.png")
        play_img = pygame.transform.smoothscale(play_img, (escala_x(380), escala_y(100)))
        PLAY_BUTTON = Button(image=play_img,
                             pos=(NATIVA_LARGURA // 2, escala_y(250)), text_input="JOGAR", font=get_font(75),
                             base_color="#d7fcd4", hovering_color="White")

        pontuacao_img = pygame.image.load("Interface/assets/Pontuacao Rect.png")
        pontuacao_img = pygame.transform.smoothscale(pontuacao_img, (escala_x(760), escala_y(100)))
        PONTUACAO_BUTTON = Button(image=pontuacao_img, pos=(NATIVA_LARGURA // 2, escala_y(400)),
                                  text_input="PONTUAÇÕES", font=get_font(75),
                                  base_color="#d7fcd4", hovering_color="White")

        quit_img = pygame.image.load("Interface/assets/Quit Rect.png")
        quit_img = pygame.transform.smoothscale(quit_img, (escala_x(380), escala_y(100)))
        QUIT_BUTTON = Button(image=quit_img,
                             pos=(NATIVA_LARGURA // 2, escala_y(550)), text_input="SAIR", font=get_font(75),
                             base_color="#d7fcd4", hovering_color="White")

        for button in [PLAY_BUTTON, PONTUACAO_BUTTON, QUIT_BUTTON]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                    play()
                if PONTUACAO_BUTTON.checkForInput(MENU_MOUSE_POS):
                    Pontuacao()
                if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()

main_menu()