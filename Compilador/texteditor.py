import pygame

class MultilineEditor:
    def __init__(self, x, y, width, height, font_size=28, bg_color=(50,50,50), text_color=(255,255,255)):
        self.rect = pygame.Rect(x, y, width, height)
        self.bg_color = bg_color
        self.text_color = text_color
        self.font = pygame.font.Font(None, font_size)
        
        # Altura da linha: altura real máxima dos glifos + 6 pixels de folga
        self.line_height = self.font.get_height() + 6
        
        self.text = ""
        self.cursor_pos = 0
        self.scroll_y = 0
        
        self.cursor_visible = True
        self.cursor_timer = 0
        self.cursor_blink_interval = 500
        
        self.surface = None
        self._visual_lines = []
        self.update_surface()

    def _wrap_text_to_visual(self, text, max_width):
        """Quebra o texto em linhas visuais conforme a largura."""
        paragraphs = text.split('\n')
        visual = []
        for para in paragraphs:
            if para == "":
                visual.append("")
                continue
            words = para.split(' ')
            cur_line = ""
            for w in words:
                while self.font.size(w)[0] > max_width:
                    part = w
                    while self.font.size(part)[0] > max_width and len(part) > 1:
                        part = part[:-1]
                    if part == "":
                        part = w[0]
                    visual.append(cur_line + part if cur_line else part)
                    w = w[len(part):]
                    cur_line = ""
                    if not w:
                        break
                if not w:
                    continue
                trial = cur_line + (" " if cur_line else "") + w
                if self.font.size(trial)[0] > max_width:
                    visual.append(cur_line)
                    cur_line = w
                else:
                    cur_line = trial
            if cur_line:
                visual.append(cur_line)
        return visual

    def update_surface(self):
        max_w = self.rect.width
        self._visual_lines = self._wrap_text_to_visual(self.text, max_w)
        total_h = len(self._visual_lines) * self.line_height
        
        # Garante que a superfície tenha pelo menos a altura do retângulo + uma linha extra
        h = max(self.rect.height, total_h) + self.line_height
        self.surface = pygame.Surface((self.rect.width, h))
        self.surface.fill(self.bg_color)
        y = 0
        for line in self._visual_lines:
            text_surf = self.font.render(line, True, self.text_color)
            self.surface.blit(text_surf, (0, y))
            y += self.line_height

    def _get_visual_pos(self, abs_pos):
        text_before = self.text[:abs_pos]
        vis_lines = self._wrap_text_to_visual(text_before, self.rect.width)
        if not vis_lines:
            return 0, 0
        line_i = len(vis_lines) - 1
        col = len(vis_lines[-1])
        return line_i, col

    def _abs_from_visual(self, line_i, col):
        pos = 0
        for i in range(line_i):
            target_line = self._visual_lines[i]
            pos += len(target_line)
            if pos < len(self.text) and self.text[pos] == '\n':
                pos += 1
        target_line = self._visual_lines[line_i]
        pos += min(col, len(target_line))
        return pos

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.text = self.text[:self.cursor_pos] + '\n' + self.text[self.cursor_pos:]
                self.cursor_pos += 1
                self.update_surface()
                return True
            elif event.key == pygame.K_BACKSPACE:
                if self.cursor_pos > 0:
                    self.text = self.text[:self.cursor_pos-1] + self.text[self.cursor_pos:]
                    self.cursor_pos -= 1
                    self.update_surface()
                return True
            elif event.key == pygame.K_DELETE:
                if self.cursor_pos < len(self.text):
                    self.text = self.text[:self.cursor_pos] + self.text[self.cursor_pos+1:]
                    self.update_surface()
                return True
            elif event.key == pygame.K_LEFT:
                if self.cursor_pos > 0:
                    self.cursor_pos -= 1
                return True
            elif event.key == pygame.K_RIGHT:
                if self.cursor_pos < len(self.text):
                    self.cursor_pos += 1
                return True
            elif event.key == pygame.K_UP:
                line_i, col = self._get_visual_pos(self.cursor_pos)
                if line_i > 0:
                    target_line_idx = line_i - 1
                    target_line = self._visual_lines[target_line_idx]
                    new_col = min(col, len(target_line))
                    self.cursor_pos = self._abs_from_visual(target_line_idx, new_col)
                return True
            elif event.key == pygame.K_DOWN:
                line_i, col = self._get_visual_pos(self.cursor_pos)
                if line_i < len(self._visual_lines) - 1:
                    target_line_idx = line_i + 1
                    target_line = self._visual_lines[target_line_idx]
                    new_col = min(col, len(target_line))
                    self.cursor_pos = self._abs_from_visual(target_line_idx, new_col)
                return True
            elif event.unicode and event.unicode.isprintable():
                self.text = self.text[:self.cursor_pos] + event.unicode + self.text[self.cursor_pos:]
                self.cursor_pos += 1
                self.update_surface()
                return True
            return False

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                mx, my = event.pos
                local_x = mx - self.rect.x
                local_y = my - self.rect.y + self.scroll_y
                line_i = int(local_y // self.line_height)
                if 0 <= line_i < len(self._visual_lines):
                    line_text = self._visual_lines[line_i]
                    col = 0
                    for i in range(1, len(line_text)+1):
                        if self.font.size(line_text[:i])[0] > local_x:
                            col = i-1
                            break
                    else:
                        col = len(line_text)
                    self.cursor_pos = self._abs_from_visual(line_i, col)
                    self.cursor_visible = True
                    self.cursor_timer = 0
                    return True
        return False

    def get_text(self):
        return self.text

    def update(self, dt):
        self.cursor_timer += dt * 1000
        if self.cursor_timer >= self.cursor_blink_interval:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0

    def draw(self, dest_surface, offset_x=0, offset_y=0):
        # Nenhum recorte – a superfície do split_screen_left já limita naturalmente
        # Força scroll_y a ser múltiplo de line_height
        self.scroll_y = (self.scroll_y // self.line_height) * self.line_height
        
        # Desenha a superfície do editor
        dest_surface.blit(self.surface, (self.rect.x, self.rect.y - self.scroll_y))
        
        # Posição do cursor
        line_i, col = self._get_visual_pos(self.cursor_pos)
        if line_i < len(self._visual_lines):
            line_text = self._visual_lines[line_i]
            prefix = line_text[:col]
            cursor_x = self.rect.x + self.font.size(prefix)[0]
        else:
            cursor_x = self.rect.x
        cursor_y = self.rect.y + line_i * self.line_height - self.scroll_y
        
        # Ajuste de scroll suave (mantendo alinhamento)
        if cursor_y < self.rect.y:
            # calcula quantas linhas subir
            diff = self.rect.y - cursor_y
            lines_up = (diff + self.line_height - 1) // self.line_height
            self.scroll_y -= lines_up * self.line_height
            cursor_y += lines_up * self.line_height
        elif cursor_y + self.line_height > self.rect.y + self.rect.height:
            diff = (cursor_y + self.line_height) - (self.rect.y + self.rect.height)
            lines_down = (diff + self.line_height - 1) // self.line_height
            self.scroll_y += lines_down * self.line_height
            cursor_y -= lines_down * self.line_height
        
        # Redesenha após possível ajuste
        dest_surface.blit(self.surface, (self.rect.x, self.rect.y - self.scroll_y))
        
        # Cursor
        if self.cursor_visible:
            cursor_rect = pygame.Rect(cursor_x, cursor_y, 2, self.line_height)
            pygame.draw.rect(dest_surface, self.text_color, cursor_rect)