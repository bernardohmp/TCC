import sys
import os
import pygame
import random
from Compilador.lexer import Lexer
from Compilador.parser import Parser
from Compilador.interpreter import Interpreter
from Compilador.texteditor import *
from Compilador.texto import *
from Compilador.pontuacao import *
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import time
from Mapa.mapa import *
from Mapa.sprites import *
import re
class Spritesheet:
    def __init__(self, path):
        self.spritesheet = pygame.image.load(path).convert_alpha()

    def get_image(self, x, y, width, height):
        sprite = pygame.Surface((width, height), pygame.SRCALPHA)
        sprite.blit(self.spritesheet, (0, 0), (x, y, width, height))
        return sprite

class Game():
    def __init__(self, modo, nivel,tilesize):
        self.TILESIZE = tilesize
        self.modo = modo
        self.nivel = nivel
        self.inicio = time.time()
        self.final = time.time()
        self.victory = False
        self.pontuacao_final = 0

        self.error_message = None
        self.error_timer = 0.0

        pygame.init()
        self.VIRTUAL_WIDTH = 1877
        self.VIRTUAL_HEIGHT = 1280
        info = pygame.display.Info()
        self.real_width = info.current_w
        self.real_height = info.current_h
        self.screen = pygame.display.set_mode((self.real_width, self.real_height), pygame.FULLSCREEN)

        # Superfície virtual
        self.virtual_screen = pygame.Surface((self.VIRTUAL_WIDTH, self.VIRTUAL_HEIGHT))

        # Fatores de escala
        self.scale_x = self.VIRTUAL_WIDTH / self.real_width
        self.scale_y = self.VIRTUAL_HEIGHT / self.real_height

        # Layout da tela dividida
        self.largura3_4 = self.VIRTUAL_WIDTH // 4
        self.split_screen_left = pygame.Surface((self.largura3_4, self.VIRTUAL_HEIGHT))
        self.split_screen_right = pygame.Surface((self.VIRTUAL_WIDTH - self.largura3_4, self.VIRTUAL_HEIGHT))
        real_left_width = self.real_width // 4
        real_editor_height = self.real_height // 2   # metade superior da tela real
        self.editor_real_rect = pygame.Rect(0, 0, real_left_width, real_editor_height)

        self.clock = pygame.time.Clock()
        self.running = True
        self.dt = 0

        self.player_spritesheet = Spritesheet('Mapa/Imagens/Player/Char_002.png')

        self.mapa_idx = random.randint(0, 4)
        if self.modo == "Principal":
            self.tilemap = [list(row) for row in tilemaps[(self.nivel)-1][self.mapa_idx]]
        else:
            self.tilemap = [list(row) for row in tilemaps_secundario]
        # Player
        self.player_pos = [0,0]
        self.direction = "up"
        self.animationCounter = 0
        self.is_sliding = False
        self.move_duration = 0.4
        self.moves = 0

        # Editor de texto
        self.dialog_height = self.VIRTUAL_HEIGHT // 2
        editor_height = self.VIRTUAL_HEIGHT - 0 - self.dialog_height
        if self.modo == "Principal":
            self.dialog_messages = TEXTOS_MODO_PRINCIPAL[self.nivel-1]
            self.reference_text = TEXTOS_FINAIS_PRINCIPAL[self.nivel-1]
        else:
            self.dialog_messages = TEXTOS_MODO_SECUNDARIO[self.nivel-1]
            self.reference_text = TEXTOS_FINAIS_SECUNDARIO[self.nivel-1]
            self.comandos = COMANDOS_PARA_OS_CODIGOS[self.nivel-1]
        self.current_message_index = 0
        self.dialog_active = True  # O diálogo começa ativo
        self.tutorial_complete = False
        self.dialog_font = pygame.font.Font(None, 30)
        self.reference_font = pygame.font.Font(None, 30)
        self.dialog_font_large = pygame.font.Font(None, 40)
        self.flag_dialog = True
        self.dialog_height = self.VIRTUAL_HEIGHT // 2 - 20   # 20 pixels a mais para o editor
        editor_height = self.VIRTUAL_HEIGHT - self.dialog_height
        self.editor = MultilineEditor(
            0, 
            0,
            self.largura3_4, 
            editor_height,
            font_size=28, 
            bg_color=(50,50,50), 
            text_color=(255,255,255)
    )
        self.editor.rect = self.editor_real_rect
        self.editor.update_surface()
        try:
            self.dialog_char_spritesheet = Spritesheet('Mapa/Imagens/Player/Char_001_Idle.png') 
            self.dialog_char_img = self.dialog_char_spritesheet.get_image(8, 10, 32, 40)
            self.dialog_char_img = pygame.transform.scale(self.dialog_char_img, (80, 80))
        except:
            # Se não houver imagem, cria um placeholder
            self.dialog_char_img = pygame.Surface((80, 80), pygame.SRCALPHA)
            self.dialog_char_img.fill((255, 200, 100))
        # Grupos de sprites
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.blocks = pygame.sprite.Group()
        self.grounds = pygame.sprite.Group()
        self.check_points = pygame.sprite.Group()

        self.lock = False
        self.create_map()
        if self.modo == "Secundario":
            self.editor.text = CODIGOS_MODO_SECUNDARIO[self.nivel - 1]
            self.editor.update_surface() 
            self.draw()
    #DIALOGO
    def advance_dialog(self):
        if self.dialog_active and not self.tutorial_complete:
            self.current_message_index += 1
            if self.current_message_index >= len(self.dialog_messages):
                self.tutorial_complete = True  # Tutorial terminou
                self.dialog_active = False
                self.flag_dialog = False

    def draw_dialog(self, surface):
        dialog_y = self.VIRTUAL_HEIGHT - self.dialog_height
        dialog_rect = pygame.Rect(0, dialog_y, self.largura3_4, self.dialog_height)

        pygame.draw.rect(surface, (40, 40, 60), dialog_rect)
        pygame.draw.rect(surface, (100, 100, 150), dialog_rect, 2)

        if self.dialog_active and not self.tutorial_complete:
            # MODO TUTORIAL
            char_margin = 15
            char_x = dialog_rect.x + char_margin
            char_y = dialog_rect.y + dialog_rect.height - self.dialog_char_img.get_height() - char_margin
            surface.blit(self.dialog_char_img, (char_x, char_y))

            # Balão
            balloon_x = char_x + self.dialog_char_img.get_width() + 10
            balloon_width = dialog_rect.width - balloon_x - 15
            balloon_height = dialog_rect.height - 60
            balloon_y = dialog_rect.y + 10

            balloon_rect = pygame.Rect(balloon_x, balloon_y, balloon_width, balloon_height)
            pygame.draw.rect(surface, (255, 255, 255), balloon_rect, border_radius=15)
            pygame.draw.rect(surface, (0, 0, 0), balloon_rect, 2, border_radius=15)

            # Ponta do balão
            ponta_x = balloon_x
            ponta_y = char_y + self.dialog_char_img.get_height() // 2
            pygame.draw.polygon(surface, (255, 255, 255), [
                (ponta_x, ponta_y - 15),
                (ponta_x, ponta_y + 15),
                (ponta_x - 20, ponta_y)
            ])
            pygame.draw.polygon(surface, (0, 0, 0), [
                (ponta_x, ponta_y - 15),
                (ponta_x, ponta_y + 15),
                (ponta_x - 20, ponta_y)
            ], 2)

            # Texto da mensagem
            if self.current_message_index < len(self.dialog_messages):
                message = self.dialog_messages[self.current_message_index]
                lines = self.wrap_text(message, self.dialog_font_large, balloon_width - 20)
                line_height = self.dialog_font_large.get_linesize() + 5
                y_text = balloon_y + 15
                for line in lines:
                    text_surface = self.dialog_font_large.render(line, True, (0, 0, 0))
                    surface.blit(text_surface, (balloon_x + 10, y_text))
                    y_text += line_height

            # Indicador "Pressione ENTER"
            if self.current_message_index < len(self.dialog_messages) - 1:
                hint = "Pressione ENTER"
            else:
                hint = "Pressione ENTER para começar"
            hint_surface = self.dialog_font_large.render(hint, True, (200, 200, 100))
            hint_x = dialog_rect.centerx - hint_surface.get_width() // 2
            surface.blit(hint_surface, (hint_x, dialog_rect.y + dialog_rect.height - 35))

        else:
            #REFERÊNCIA
            if self.error_message:
                error_box = pygame.Rect(20, dialog_y + 20, self.largura3_4 - 40, self.dialog_height - 40)
                pygame.draw.rect(surface, (80, 0, 0), error_box, border_radius=10)
                pygame.draw.rect(surface, (255, 100, 100), error_box, 2, border_radius=10)

                # Texto do erro
                lines = self.wrap_text(self.error_message, self.dialog_font_large, error_box.width - 20)
                y_text = error_box.y + 20
                for line in lines:
                    text_surf = self.dialog_font_large.render(line, True, (255, 200, 200))
                    surface.blit(text_surf, (error_box.x + 10, y_text))
                    y_text += self.dialog_font_large.get_linesize() + 5

            else:
                # Texto de referência
                y_offset = dialog_y + 25
                for line in self.reference_text:
                    if line == "":
                        y_offset += 15
                        continue
                    if line.isupper() or line.endswith(":"):
                        color = (255, 255, 100)
                        font = self.reference_font
                    elif "move_" in line:
                        color = (100, 255, 100)
                        font = self.reference_font
                    else:
                        color = (100, 255, 100)
                        font = self.reference_font
                    text_surface = font.render(line, True, color)
                    surface.blit(text_surface, (25, y_offset))
                    y_offset += 25

    def wrap_text(self, text, font, max_width):
        words = text.split(' ')
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + " " + word if current_line else word
            test_surface = font.render(test_line, True, (255, 255, 255))
            
            if test_surface.get_width() <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        return lines

    #Mapa e sprites
    def reset_level(self):
        if self.modo == "Principal":
            self.dialog_messages = TEXTOS_MODO_PRINCIPAL[self.nivel-1]
            self.reference_text = TEXTOS_FINAIS_PRINCIPAL[self.nivel-1]
            self.tilemap = [list(row) for row in tilemaps[(self.nivel)-1][self.mapa_idx]]
        else:
            self.dialog_messages = TEXTOS_MODO_SECUNDARIO[self.nivel-1]
            self.reference_text = TEXTOS_FINAIS_SECUNDARIO[self.nivel-1]
            self.comandos = COMANDOS_PARA_OS_CODIGOS[self.nivel-1]
            self.tilemap = [list(row) for row in tilemaps_secundario]
        self.current_message_index = 0
        self.dialog_active = True  # O diálogo começa ativo
        self.tutorial_complete = False
        self.create_map()
        self.draw()
    def create_map(self):
        self.inicio = time.time()
        if hasattr(self, 'player') and self.player:
            self.player.kill()
            self.player = None
        self.grounds.empty()
        self.blocks.empty()
        self.check_points.empty()
        self.virtual_screen.fill("black")

        for i, row in enumerate(self.tilemap):
            for j, column in enumerate(row):
                ground = Ground(self, j, i)
                self.grounds.add(ground)
                if column == 'B':
                    block = Block(self, j, i)
                    self.blocks.add(block)
                if column == 'P':
                    self.player = Player(self, j, i)
                    self.player_pos = [i, j]
                if column == 'C':
                    check_point = CheckPoint(self, j, i)
                    self.check_points.add(check_point)

    def update_map(self):
        if self.player:
            row, col = self.player_pos
            self.player.rect.topleft = (col * self.TILESIZE, row * self.TILESIZE)

    # Compilação
    def compile_and_run(self, source_code):
        try:
            lexer = Lexer(source_code)
            tokens = lexer.tokenize()
            if tokens == 0:
                return [], "Erro léxico no código."
            parser = Parser(tokens)
            ast = parser.parse()
            if parser.flag != 0:
                return [], "Erro de sintaxe. Verifique parênteses, chaves e ponto-e-vírgula."
            interpreter = Interpreter()
            interpreter.visit(ast)
            return interpreter.moves, None
        except Exception as e:
            return [], f"Erro inesperado: {str(e)}"

    # Eventos
    def handle_pontuacao(self, movimentos):
        self.final = time.time()
        tempo = self.final - self.inicio
        if self.modo == "Secundario":
            pontuacao = calcula_pontuacao("Secundario", 0, int(tempo))
            atualizar_linha_se_maior(ARQUIVO_SECUNDARIO, self.nivel - 1, pontuacao)
        else:
            pontuacao = calcula_pontuacao("Principal", movimentos, int(tempo))
            atualizar_linha_se_maior(ARQUIVO_PRINCIPAL, self.nivel - 1, pontuacao)

        self.pontuacao_final = pontuacao
        self.victory = True
        self.running = False   
    def handle_events(self):
        events = pygame.event.get()
        for event in events:
            # Evento de fechar janela
            if event.type == pygame.QUIT:
                self.running = False
                continue
            
            # Eventos de teclado
            if event.type == pygame.KEYDOWN:
                # ESC sempre fecha o jogo
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    continue
                if event.key == pygame.K_RIGHT and self.modo == "Secundario":
                    self.move_player("direita")
                    if self.comandos != "":
                        linha, separador, resto = self.comandos.partition('\n')
                        self.comandos = resto
                        comando = linha.strip()
                        if comando == "direita":
                            if resto == "":
                                print("Voce ganhou")
                                self.handle_pontuacao(0)
                        else:
                            print("movimento incorreto")
                if event.key == pygame.K_LEFT and self.modo == "Secundario":
                    self.move_player("esquerda")
                    if self.comandos != "":
                            linha, separador, resto = self.comandos.partition('\n')
                            self.comandos = resto
                            comando = linha.strip()
                            if comando == "esquerda":
                                if resto == "":
                                    print("Voce ganhou")
                                    self.handle_pontuacao(0)
                            else:
                                print("movimento incorreto")
                if event.key == pygame.K_UP and self.modo == "Secundario":
                    self.move_player("cima")
                    if self.comandos != "":
                            linha, separador, resto = self.comandos.partition('\n')
                            self.comandos = resto
                            comando = linha.strip()
                            if comando == "cima":
                                if resto == "":
                                    print("Voce ganhou")
                                    self.handle_pontuacao(0)
                            else:
                                print("movimento incorreto")
                if event.key == pygame.K_DOWN and self.modo == "Secundario":
                    self.move_player("baixo")
                    if self.comandos != "":
                            linha, separador, resto = self.comandos.partition('\n')
                            self.comandos = resto
                            comando = linha.strip()
                            if comando == "baixo":
                                if resto == "":
                                    print("Voce ganhou")
                                    self.handle_pontuacao(0)
                            else:
                                print("movimento incorreto")
                if event.key == pygame.K_RETURN:
                    if self.dialog_active and not self.tutorial_complete:
                        self.advance_dialog()
                        continue 
                #Passar as teclas para o editor
                if self.modo=="Principal" and self.flag_dialog == False:
                    self.editor.handle_event(event)
                
            # Eventos de mouse
            elif event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
                virt_x = event.pos[0] * self.scale_x
                virt_y = event.pos[1] * self.scale_y
                
                # Cria um novo evento
                new_event = pygame.event.Event(
                    event.type,
                    pos=(virt_x, virt_y),
                    button=event.button if hasattr(event, 'button') else 0,
                    buttons=event.buttons if hasattr(event, 'buttons') else (0, 0, 0)
                )
                self.editor.handle_event(new_event)
                
            # Outros eventos
            else:
                self.editor.handle_event(event)
        
        return events
    
    def move_player(self, direcao):
        col, lin = self.player_pos[0], self.player_pos[1]
        target_col, target_lin = col, lin
        if direcao == "direita":
            target_lin = lin + 1
        elif direcao == "esquerda":
            target_lin = lin - 1
        elif direcao == "cima":
            target_col = col - 1
        elif direcao == "baixo":
            target_col = col + 1
        else:
            return False  # direção inválida

        # Verifica se o destino é um B
        if self.tilemap[target_col][target_lin] == 'B':
            return False
        # Atualiza o tilemap
        self.tilemap[col][lin] = '.'
        self.tilemap[target_col][target_lin] = 'P'
        self.player_pos = [target_col, target_lin]

        # Executa animação
        self.is_sliding = True
        self.slide_to(target_col, target_lin, direcao)
        self.is_sliding = False

        return True

    def execute_code(self):
        if not self.lock:
            self.lock = True
            code = self.editor.get_text()
            movimentos, erro = self.compile_and_run(code)
            if erro:
                self.error_message = erro
                self.lock = False
                return
            self.error_message = None

            for i, comando in enumerate(movimentos):
                col, lin = self.player_pos[0], self.player_pos[1]
                target_col, target_lin = col, lin
                direcao = None

                if comando == 'move_right':
                    if lin+1 < len(self.tilemap[0]) and self.tilemap[col][lin+1] != 'B':
                        direcao = "direita"
                        target_lin = lin + 1
                elif comando == 'move_left':
                    if lin-1 >= 0 and self.tilemap[col][lin-1] != 'B':
                        direcao = "esquerda"
                        target_lin = lin - 1
                elif comando == 'move_up':
                    if col-1 >= 0 and self.tilemap[col-1][lin] != 'B':
                        direcao = "cima"
                        target_col = col - 1
                elif comando == 'move_down':
                    if col+1 < len(self.tilemap) and self.tilemap[col+1][lin] != 'B':
                        direcao = "baixo"
                        target_col = col + 1

                if direcao is None:
                    continue

                # Verifica vitória antes de mover
                if self.tilemap[target_col][target_lin] == 'C':
                    print("Vitoria")
                    self.handle_pontuacao(self.moves)

                # Executa o movimento
                self.tilemap[col][lin] = '.'
                self.tilemap[target_col][target_lin] = 'P'
                self.player_pos = [target_col, target_lin]

                self.is_sliding = True
                self.slide_to(target_col, target_lin, direcao)
                self.is_sliding = False

                if i == len(movimentos) - 1:
                    time.sleep(1)

            # Após todos os movimentos, recria o mapa
            self.tilemap = [list(row) for row in tilemaps[(self.nivel)-1][self.mapa_idx]]
            self.create_map()
            self.draw()
            self.lock = False
    def count_moves(self,texto):
        i = 0
        padrao = r'move_(?:left|right|up|down)\(\);'
        for match in re.finditer(padrao, texto):
            i = i+1
        return i
            

    def update(self):
        self.editor.update(self.dt)
        if self.error_message:
            self.error_timer += self.dt
            if self.error_timer > 5.0:
                self.error_message = None
                self.error_timer = 0.0
        keys = pygame.key.get_pressed()
        if (keys[pygame.K_F5] or keys[pygame.K_CAPSLOCK]) and self.modo == "Principal":
            texto = self.editor.get_text()
            self.moves = self.count_moves(texto)
            self.execute_code()
        elif keys[pygame.K_F6] and self.modo == "Principal":
            self.editor.text = "i=0; while(i<3){move_up();move_right();i=i+1;}move_up();"
            self.execute_code()
        elif keys[pygame.K_F7]:
            self.reset_level()

    def draw(self):
        self.split_screen_left.fill(self.editor.bg_color)
        separator_y = self.VIRTUAL_HEIGHT - self.dialog_height
        pygame.draw.line(self.split_screen_left, (100,100,100), 
                        (0, separator_y), 
                        (self.largura3_4, separator_y))
        self.draw_dialog(self.split_screen_left)
        
        self.split_screen_right.fill("black")
        if not self.is_sliding:
            self.update_map()
        self.all_sprites.draw(self.split_screen_right)
        
        self.virtual_screen.blit(self.split_screen_left, (0, 0))
        self.virtual_screen.blit(self.split_screen_right, (self.largura3_4, 0))
        scaled_screen = pygame.transform.scale(self.virtual_screen, (self.real_width, self.real_height))
        self.screen.blit(scaled_screen, (0, 0))
        self.editor.draw(self.screen)
        
        pygame.display.flip()

    def draw_left(self):
        self.split_screen_left.fill(self.editor.bg_color)
        separator_y = self.VIRTUAL_HEIGHT - self.dialog_height
        pygame.draw.line(self.split_screen_left, (100,100,100), 
                        (0, separator_y), 
                        (self.largura3_4, separator_y))
        self.draw_dialog(self.split_screen_left)
        
        self.virtual_screen.blit(self.split_screen_left, (0, 0))
        self.virtual_screen.blit(self.split_screen_right, (self.largura3_4, 0))
        scaled_screen = pygame.transform.scale(self.virtual_screen, (self.real_width, self.real_height))
        self.screen.blit(scaled_screen, (0, 0))
        
        self.editor.draw(self.screen)
        
        pygame.display.flip()

    def run(self):
        self.create_map()
        self.draw()
        while self.running:
            self.dt = self.clock.tick(60) / 1000.0
            self.handle_events()
            self.update()
            self.draw_left()

    def slide_to(self, target_col, target_lin, direction):
        start_x, start_y = self.player.rect.topleft
        end_x = target_lin * self.TILESIZE
        end_y = target_col * self.TILESIZE

        # Animações (spritesheet)
        down_anim = [self.player_spritesheet.get_image(8, 10, 32, 40),
                     self.player_spritesheet.get_image(60, 10, 32, 40),
                     self.player_spritesheet.get_image(100, 10, 32, 40),
                     self.player_spritesheet.get_image(196, 10, 32, 40)]
        left_anim = [self.player_spritesheet.get_image(8, 60, 32, 40),
                     self.player_spritesheet.get_image(60, 60, 32, 40),
                     self.player_spritesheet.get_image(100, 60, 32, 40),
                     self.player_spritesheet.get_image(196, 60, 32, 40)]
        right_anim = [self.player_spritesheet.get_image(8, 104, 32, 40),
                      self.player_spritesheet.get_image(60, 104, 32, 40),
                      self.player_spritesheet.get_image(100, 104, 32, 40),
                      self.player_spritesheet.get_image(196, 104, 32, 40)]
        up_anim = [self.player_spritesheet.get_image(8, 154, 32, 40),
                   self.player_spritesheet.get_image(60, 154, 32, 40),
                   self.player_spritesheet.get_image(100, 154, 32, 40),
                   self.player_spritesheet.get_image(196, 154, 32, 40)]

        if direction == "direita":
            frames = right_anim
        elif direction == "esquerda":
            frames = left_anim
        elif direction == "cima":
            frames = up_anim
        else:
            frames = down_anim

        elapsed = 0.0
        anim_counter = 0.0
        clock = pygame.time.Clock()

        while elapsed < self.move_duration:
            dt = clock.tick(60) / 1000.0
            elapsed += dt
            progress = elapsed / self.move_duration

            x = start_x + (end_x - start_x) * progress
            y = start_y + (end_y - start_y) * progress
            self.player.rect.topleft = (x, y)

            anim_counter += dt * 5
            frame_idx = int(anim_counter) % len(frames)
            self.player.image = pygame.transform.scale(frames[frame_idx], (self.TILESIZE, self.TILESIZE))

            self.draw()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return

        self.player.rect.topleft = (end_x, end_y)