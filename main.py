import json
import math
import random
from dataclasses import dataclass
from pathlib import Path

import pygame


WIDTH, HEIGHT = 1280, 720
FPS = 60

BG_TOP = (14, 16, 28)
BG_BOTTOM = (7, 48, 42)
PANEL = (23, 29, 46)
PANEL_2 = (31, 39, 60)
GOLD = (238, 190, 92)
GOLD_2 = (255, 221, 139)
GREEN = (38, 175, 117)
RED = (212, 73, 73)
BLACK = (18, 20, 28)
WHITE = (244, 245, 248)
MUTED = (164, 176, 188)
BLUE = (88, 148, 255)
PURPLE = (149, 119, 255)
CARD = (250, 248, 239)
INK = (28, 31, 36)
DISABLED = (72, 81, 95)


def clamp(value, low, high):
    return max(low, min(high, value))


def lerp_color(a, b, t):
    return tuple(int(a[i] * (1 - t) + b[i] * t) for i in range(3))


def br_money(value):
    return f"{int(value):,}".replace(",", ".")


def rounded_rect(surface, rect, color, radius=12, border=0, border_color=None):
    pygame.draw.rect(surface, color, rect, border_radius=radius)
    if border and border_color:
        pygame.draw.rect(surface, border_color, rect, border, border_radius=radius)


def draw_text(surface, text, font, color, pos, anchor="topleft"):
    rendered = font.render(str(text), True, color)
    rect = rendered.get_rect()
    setattr(rect, anchor, pos)
    surface.blit(rendered, rect)
    return rect


def draw_centered_wrapped(surface, text, font, color, rect, line_gap=6):
    words = str(text).split()
    lines = []
    current = ""
    for word in words:
        test = word if not current else f"{current} {word}"
        if font.size(test)[0] <= rect.width - 20:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    max_fit = max(1, (rect.height + line_gap) // (font.get_height() + line_gap))
    lines = lines[:max_fit]
    total_h = len(lines) * font.get_height() + max(0, len(lines) - 1) * line_gap
    y = max(rect.y, rect.centery - total_h // 2)
    old_clip = surface.get_clip()
    surface.set_clip(rect)
    for line in lines:
        rendered = font.render(line, True, color)
        r = rendered.get_rect(centerx=rect.centerx, top=y)
        surface.blit(rendered, r)
        y += font.get_height() + line_gap
    surface.set_clip(old_clip)


def draw_wrapped_text(surface, text, font, color, rect, line_gap=5, max_lines=None):
    words = str(text).split()
    lines = []
    current = ""
    for word in words:
        test = word if not current else f"{current} {word}"
        if font.size(test)[0] <= rect.width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    if max_lines:
        lines = lines[:max_lines]
    old_clip = surface.get_clip()
    surface.set_clip(rect)
    y = rect.y
    for line in lines:
        rendered = font.render(line, True, color)
        surface.blit(rendered, (rect.x, y))
        y += font.get_height() + line_gap
        if y > rect.bottom:
            break
    surface.set_clip(old_clip)


def draw_diamond(surface, center, radius, color, border_color=None, border=0):
    points = [
        (center[0], center[1] - radius),
        (center[0] + radius, center[1]),
        (center[0], center[1] + radius),
        (center[0] - radius, center[1]),
    ]
    pygame.draw.polygon(surface, color, points)
    if border and border_color:
        pygame.draw.polygon(surface, border_color, points, border)


def blit_cover(surface, image, rect, alpha=110):
    if not image:
        return
    iw, ih = image.get_size()
    if iw <= 0 or ih <= 0:
        return
    scale = max(rect.w / iw, rect.h / ih)
    scaled = pygame.transform.smoothscale(image, (int(iw * scale), int(ih * scale))).convert_alpha()
    scaled.set_alpha(alpha)
    src = scaled.get_rect(center=rect.center)
    old_clip = surface.get_clip()
    surface.set_clip(rect)
    surface.blit(scaled, src)
    surface.set_clip(old_clip)


def draw_chip(surface, center, radius, label, font):
    pygame.draw.circle(surface, (144, 24, 45), center, radius)
    pygame.draw.circle(surface, GOLD_2, center, radius, 4)
    pygame.draw.circle(surface, (92, 12, 31), center, radius - 12, 2)
    for angle in range(0, 360, 45):
        rad = math.radians(angle)
        p1 = (int(center[0] + math.cos(rad) * (radius - 5)), int(center[1] + math.sin(rad) * (radius - 5)))
        p2 = (int(center[0] + math.cos(rad) * (radius - 20)), int(center[1] + math.sin(rad) * (radius - 20)))
        pygame.draw.line(surface, GOLD_2, p1, p2, 5)
    draw_text(surface, label, font, WHITE, center, "center")


def draw_premium_chip(surface, center, radius, label, font, pulse=0.0):
    glow = pygame.Surface((radius * 4, radius * 4), pygame.SRCALPHA)
    glow_center = (radius * 2, radius * 2)
    for i in range(5, 0, -1):
        alpha = int((18 + pulse * 18) * i)
        pygame.draw.circle(glow, (*GOLD_2, alpha), glow_center, radius + i * 12, 2)
    surface.blit(glow, glow.get_rect(center=center))
    pygame.draw.circle(surface, (95, 12, 34), center, radius)
    pygame.draw.circle(surface, (168, 25, 52), center, radius - 10)
    pygame.draw.circle(surface, GOLD_2, center, radius, 5)
    pygame.draw.circle(surface, (78, 10, 27), center, radius - 28, 3)
    for angle in range(0, 360, 30):
        rad = math.radians(angle + pulse * 6)
        outer = (int(center[0] + math.cos(rad) * (radius - 6)), int(center[1] + math.sin(rad) * (radius - 6)))
        inner = (int(center[0] + math.cos(rad) * (radius - 27)), int(center[1] + math.sin(rad) * (radius - 27)))
        pygame.draw.line(surface, GOLD_2, outer, inner, 5)
    for angle in (35 + pulse * 28, 215 + pulse * 28):
        rad = math.radians(angle)
        sparkle = (int(center[0] + math.cos(rad) * (radius + 12)), int(center[1] + math.sin(rad) * (radius + 12)))
        pygame.draw.circle(surface, (255, 246, 201), sparkle, max(2, radius // 16))
        pygame.draw.circle(surface, (*GOLD_2, 90), sparkle, max(5, radius // 9), 1)
    pygame.draw.circle(surface, (255, 255, 255), (center[0] - radius // 3, center[1] - radius // 3), max(3, radius // 18))
    draw_text(surface, label, font, WHITE, center, "center")


def draw_game_icon(surface, rect, scene, fonts, hovered=False):
    bg = (13, 19, 34) if not hovered else (18, 27, 48)
    rounded_rect(surface, rect, bg, 18, 2, GOLD)
    shine = pygame.Rect(rect.x + 8, rect.y + 8, rect.w - 16, 18)
    pygame.draw.rect(surface, (255, 255, 255, 20), shine, border_radius=9)

    if scene == "blackjack":
        left = pygame.Rect(rect.x + 22, rect.y + 25, 38, 54)
        right = pygame.Rect(rect.x + 45, rect.y + 16, 38, 54)
        rounded_rect(surface, left, CARD, 6, 1, (220, 214, 200))
        rounded_rect(surface, right, CARD, 6, 1, (220, 214, 200))
        draw_text(surface, "A", fonts["small"], INK, (left.x + 7, left.y + 5))
        draw_text(surface, "K", fonts["small"], RED, (right.x + 7, right.y + 5))
        draw_diamond(surface, left.center, 9, INK)
        pygame.draw.circle(surface, RED, (right.centerx - 5, right.centery - 3), 6)
        pygame.draw.circle(surface, RED, (right.centerx + 5, right.centery - 3), 6)
        pygame.draw.polygon(surface, RED, [(right.centerx - 12, right.centery), (right.centerx + 12, right.centery), (right.centerx, right.centery + 16)])
    elif scene == "dice":
        for dx, dy, val in [(18, 20, 5), (48, 42, 3)]:
            die = pygame.Rect(rect.x + dx, rect.y + dy, 42, 42)
            rounded_rect(surface, die, CARD, 9, 2, (214, 202, 178))
            spots = [(0.28, 0.28), (0.72, 0.28), (0.5, 0.5), (0.28, 0.72), (0.72, 0.72)] if val == 5 else [(0.28, 0.28), (0.5, 0.5), (0.72, 0.72)]
            for px, py in spots:
                pygame.draw.circle(surface, INK, (die.x + int(die.w * px), die.y + int(die.h * py)), 3)
    elif scene == "roulette":
        center = rect.center
        pygame.draw.circle(surface, GOLD_2, center, 33)
        for i, color in enumerate([GREEN, RED, BLACK, RED, BLACK, RED, BLACK, RED]):
            a1 = -math.pi / 2 + i * math.tau / 8
            a2 = -math.pi / 2 + (i + 1) * math.tau / 8
            points = [center]
            for a in (a1, (a1 + a2) / 2, a2):
                points.append((int(center[0] + math.cos(a) * 31), int(center[1] + math.sin(a) * 31)))
            pygame.draw.polygon(surface, color, points)
        pygame.draw.circle(surface, (13, 18, 30), center, 15)
        pygame.draw.circle(surface, WHITE, (center[0] + 19, center[1] - 19), 5)
        draw_text(surface, "0", fonts["tiny"], WHITE, center, "center")
    elif scene == "slots":
        machine = pygame.Rect(rect.x + 10, rect.y + 18, rect.w - 20, rect.h - 30)
        rounded_rect(surface, machine, (126, 25, 58), 10, 2, GOLD)
        reel_w, gap = 28, 4
        x0 = machine.x + (machine.w - (reel_w * 3 + gap * 2)) // 2
        for i, label in enumerate(["67", "TRE", "JOG"]):
            reel = pygame.Rect(x0 + i * (reel_w + gap), machine.y + 12, reel_w, 42)
            rounded_rect(surface, reel, (246, 239, 218), 6, 1, (211, 199, 167))
            draw_text(surface, label, fonts["tiny"], (126, 25, 58), reel.center, "center")
    elif scene == "mines":
        for row in range(3):
            for col in range(3):
                cell = pygame.Rect(rect.x + 22 + col * 22, rect.y + 18 + row * 22, 18, 18)
                rounded_rect(surface, cell, (25, 55, 95), 5, 1, (87, 139, 194))
        draw_diamond(surface, rect.center, 20, (86, 184, 255), WHITE, 2)
        draw_diamond(surface, rect.center, 9, (190, 235, 255))
    elif scene == "plinko":
        center_x = rect.centerx
        top_y = rect.y + 22
        for row in range(4):
            for col in range(row + 1):
                x = center_x + int((col - row / 2) * 22)
                y = top_y + row * 15
                pygame.draw.circle(surface, GOLD_2, (x, y), 4)
                pygame.draw.circle(surface, (255, 255, 255), (x - 1, y - 1), 1)
        for i, mult in enumerate(["3x", "1x", "3x"]):
            bucket = pygame.Rect(rect.x + 21 + i * 25, rect.y + 70, 22, 14)
            rounded_rect(surface, bucket, (35, 53, 77), 4, 1, GOLD if i != 1 else (83, 98, 128))
            draw_text(surface, mult, fonts["tiny"], GOLD_2 if i != 1 else WHITE, bucket.center, "center")
        pygame.draw.circle(surface, (236, 62, 78), (center_x, rect.y + 14), 8)
    elif scene == "coinflip":
        pygame.draw.circle(surface, GOLD_2, rect.center, 34)
        pygame.draw.circle(surface, (176, 111, 36), rect.center, 28, 4)
        draw_text(surface, "67", fonts["small"], (82, 45, 18), rect.center, "center")
        for i in range(3):
            pygame.draw.circle(surface, (255, 246, 201), (rect.x + 22 + i * 32, rect.y + 20 + i * 18), 3)
    elif scene == "crash":
        base = pygame.Rect(rect.x + 18, rect.y + 70, rect.w - 36, 8)
        pygame.draw.rect(surface, (76, 91, 118), base, border_radius=4)
        points = [(rect.x + 24, rect.y + 68), (rect.x + 45, rect.y + 58), (rect.x + 62, rect.y + 43), (rect.x + 90, rect.y + 22)]
        pygame.draw.lines(surface, GREEN, False, points, 5)
        pygame.draw.circle(surface, RED, points[-1], 7)
        draw_text(surface, "x", fonts["h3"], GOLD_2, (rect.x + 48, rect.y + 28), "center")


@dataclass
class Button:
    rect: pygame.Rect
    text: str
    action: object
    kind: str = "primary"
    enabled: bool = True
    icon: str = ""
    tooltip: str = ""

    def contains(self, pos):
        return self.rect.collidepoint(pos)

    def handle(self, event):
        if not self.enabled:
            return False
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self.contains(event.pos):
            self.action()
            return True
        return False

    def draw(self, surface, fonts, mouse_pos):
        hovered = self.enabled and self.contains(mouse_pos)
        palette = {
            "primary": ((213, 155, 54), (244, 194, 92), INK),
            "secondary": ((45, 56, 78), (61, 76, 104), WHITE),
            "danger": ((161, 53, 62), (205, 68, 78), WHITE),
            "success": ((34, 135, 91), (43, 173, 116), WHITE),
            "ghost": ((28, 35, 54), (36, 46, 70), WHITE),
            "blue": ((55, 93, 166), (74, 124, 218), WHITE),
        }
        normal, hot, text_color = palette.get(self.kind, palette["secondary"])
        color = hot if hovered else normal
        if not self.enabled:
            color = DISABLED
            text_color = (142, 151, 162)
        rounded_rect(surface, self.rect, color, 10, 1, (255, 255, 255, 35))
        label = f"{self.icon} {self.text}".strip()
        draw_centered_wrapped(surface, label, fonts["button"], text_color, self.rect, 2)


class Scene:
    def __init__(self, app):
        self.app = app
        self.buttons = []

    def on_enter(self):
        pass

    def build_ui(self):
        self.buttons = []

    def update(self, dt):
        pass

    def handle_event(self, event):
        for button in list(self.buttons):
            if button.handle(event):
                return True
        return False

    def draw(self, surface):
        pass

    def draw_panel_title(self, surface, title, subtitle=None):
        draw_text(surface, title, self.app.fonts["h2"], WHITE, (64, 98))
        if subtitle:
            draw_wrapped_text(surface, subtitle, self.app.fonts["small"], MUTED, pygame.Rect(66, 136, 650, 42), 4, 2)


class CasinoGameScene(Scene):
    min_bet = 25
    max_bet = 10000

    def __init__(self, app):
        super().__init__(app)
        self.bet = 100

    def can_change_bet(self):
        return True

    def change_bet(self, amount):
        if not self.can_change_bet():
            return
        self.bet = clamp(self.bet + amount, self.min_bet, min(self.max_bet, max(self.min_bet, self.app.balance)))

    def draw_bet_box(self, surface, x, y, w=370):
        rect = pygame.Rect(x, y, w, 74)
        rounded_rect(surface, rect, PANEL_2, 12, 1, (82, 96, 126))
        draw_text(surface, "APOSTA", self.app.fonts["tiny"], MUTED, (x + 18, y + 13))
        draw_text(surface, f"{br_money(self.bet)} fichas", self.app.fonts["h3"], GOLD_2, (x + 18, y + 34))

    def add_bet_buttons(self, x, y):
        enabled = self.can_change_bet()
        self.buttons.extend(
            [
                Button(pygame.Rect(x + 166, y + 15, 44, 44), "-", lambda: self.change_bet(-25), "secondary", enabled),
                Button(pygame.Rect(x + 214, y + 15, 44, 44), "+", lambda: self.change_bet(25), "secondary", enabled),
                Button(pygame.Rect(x + 266, y + 15, 88, 44), "ALL IN", self.all_in_bet, "ghost", enabled),
            ]
        )

    def maximize_bet(self):
        self.all_in_bet()

    def all_in_bet(self):
        if not self.can_change_bet():
            return
        self.bet = max(self.min_bet, self.app.balance)


class AgeGateScene(Scene):
    def __init__(self, app):
        super().__init__(app)
        self.time = 0.0

    def build_ui(self):
        self.buttons = [
            Button(pygame.Rect(420, 492, 440, 58), "Sou maior de 18 anos", lambda: self.app.set_scene("menu"), "primary"),
            Button(pygame.Rect(420, 566, 440, 58), "Sou menor de 18 anos", self.deny_access, "danger"),
        ]

    def deny_access(self):
        self.app.quit_game()

    def update(self, dt):
        self.time += dt

    def draw(self, surface):
        veil = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        veil.fill((4, 7, 14, 210))
        surface.blit(veil, (0, 0))
        for i in range(16):
            angle = self.time * 0.35 + i * math.tau / 16
            radius = 235 + math.sin(self.time * 1.2 + i) * 16
            x = int(WIDTH // 2 + math.cos(angle) * radius)
            y = int(318 + math.sin(angle) * radius * 0.45)
            pygame.draw.circle(surface, (255, 221, 139, 30), (x, y), 3 + i % 3)
        halo = pygame.Surface((460, 460), pygame.SRCALPHA)
        for radius in range(210, 70, -28):
            alpha = int(12 + (210 - radius) * 0.18)
            pygame.draw.circle(halo, (*GOLD_2, alpha), (230, 230), radius, 2)
        surface.blit(halo, halo.get_rect(center=(WIDTH // 2, 292)))
        draw_premium_chip(surface, (WIDTH // 2, 292), 94, "67", self.app.fonts["h1"], (math.sin(self.time * 2.2) + 1) / 2)
        draw_text(surface, "Casino 67", self.app.fonts["mega"], GOLD_2, (WIDTH // 2, 112), "center")
        draw_text(surface, "feito por: André B, Christian S, Rony F", self.app.fonts["body"], MUTED, (WIDTH // 2, 184), "center")
        panel = pygame.Rect(350, 424, 580, 226)
        rounded_rect(surface, panel, (15, 22, 36), 22, 1, (86, 101, 132))
        draw_text(surface, "Verificação de idade", self.app.fonts["h2"], WHITE, (WIDTH // 2, 448), "center")
        draw_text(surface, "Confirme sua idade para acessar o salão principal.", self.app.fonts["small"], MUTED, (WIDTH // 2, 482), "center")


class MenuScene(Scene):
    def __init__(self, app):
        super().__init__(app)
        self.card_rects = []
        self.hovered_scene = None
        self.last_hovered_scene = None
        self.time = 0.0
        self.hover_progress = {}

    def build_ui(self):
        self.buttons = []
        games = [
            ("blackjack", "Blackjack", "Faça 21, dobre ou divida pares contra o dealer.", "cards"),
            ("dice", "Dice", "Dados animados com apostas em soma, paridade e sete.", "dice"),
            ("roulette", "Roleta", "Mesa 0-36 com número, cor, faixa e dúzias.", "wheel"),
            ("slots", "Slots", "Cinco rolos com 67, treino, jogo e cereja.", "reels"),
            ("plinko", "Plinko", "Escolha risco e colunas para buscar buckets altos.", "pins"),
            ("mines", "Mines", "Abra gemas, evite minas e saque no multiplicador.", "mine"),
            ("coinflip", "Cara/Coroa", "Escolha cara ou coroa e acompanhe a moeda girar.", "coin"),
            ("crash", "Crash 67", "Saque antes do multiplicador explodir.", "rocket"),
        ]
        self.card_rects = []
        start_x, start_y = 52, 340
        card_w, card_h, gap_x, gap_y = 276, 166, 18, 12
        for i, (scene, title, desc, icon) in enumerate(games):
            col = i % 4
            row = i // 4
            rect = pygame.Rect(start_x + col * (card_w + gap_x), start_y + row * (card_h + gap_y), card_w, card_h)
            self.card_rects.append((rect, scene, title, desc, icon))
            self.buttons.append(Button(pygame.Rect(rect.x + 24, rect.bottom - 58, rect.w - 48, 44), "Jogar", lambda s=scene: self.app.set_scene(s), "primary"))
        self.buttons.append(Button(pygame.Rect(1030, 268, 170, 46), "Recarregar", self.app.refill_balance, "secondary"))
        self.buttons.append(Button(pygame.Rect(842, 268, 170, 46), "Rankings", lambda: self.app.set_scene("rankings"), "ghost"))

    def update(self, dt):
        self.time += dt
        mouse = pygame.mouse.get_pos()
        hovered = None
        for rect, scene, *_ in self.card_rects:
            if rect.collidepoint(mouse):
                hovered = scene
                break
        self.hovered_scene = hovered
        for _, scene, *_ in self.card_rects:
            current = self.hover_progress.get(scene, 0.0)
            target = 1.0 if hovered == scene else 0.0
            speed = 7.5 if target else 5.0
            self.hover_progress[scene] = current + (target - current) * clamp(dt * speed, 0, 1)
        if hovered != self.last_hovered_scene and hovered == "blackjack":
            self.app.play_sound("blackjack_hover")
        self.last_hovered_scene = hovered

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            for rect, scene, *_ in self.card_rects:
                if rect.collidepoint(event.pos):
                    self.app.set_scene(scene)
                    return True
        return super().handle_event(event)

    def draw_lobby_background(self, surface):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for y in range(96, HEIGHT, 18):
            t = (y - 96) / (HEIGHT - 96)
            color = (6, int(28 + 28 * (1 - t)), int(36 + 22 * (1 - t)), int(22 + 34 * (1 - t)))
            pygame.draw.rect(overlay, color, pygame.Rect(0, y, WIDTH, 18))
        pulse = (math.sin(self.time * 1.2) + 1) / 2
        pygame.draw.circle(overlay, (255, 216, 120, int(22 + pulse * 16)), (1060, 210), 260, 2)
        pygame.draw.circle(overlay, (74, 190, 143, 24), (210, 548), 360, 2)
        pygame.draw.polygon(overlay, (255, 220, 140, 14), [(610, 92), (754, 92), (1100, 680), (880, 680)])
        pygame.draw.polygon(overlay, (88, 220, 170, 10), [(120, 96), (230, 96), (500, 680), (250, 680)])
        for i in range(46):
            speed = 10 + (i % 5) * 5
            x = int((i * 173 + self.time * speed) % (WIDTH + 80) - 40)
            y = 124 + (i * 79) % 520
            r = 1 + (i % 3)
            alpha = 42 + (i % 4) * 16
            pygame.draw.circle(overlay, (255, 231, 164, alpha), (x, y), r)
        surface.blit(overlay, (0, 0))

    def draw_lobby_header(self, surface):
        fonts = self.app.fonts
        hero = pygame.Rect(52, 108, 1176, 214)
        shadow = pygame.Surface((hero.w + 36, hero.h + 36), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (0, 0, 0, 92), shadow.get_rect().inflate(-18, -18), border_radius=26)
        surface.blit(shadow, (hero.x - 18, hero.y - 10))
        rounded_rect(surface, hero, (11, 18, 31), 26, 1, (76, 89, 116))
        pygame.draw.line(surface, GOLD_2, (hero.x + 28, hero.y + 34), (hero.x + 560, hero.y + 34), 2)
        draw_text(surface, "LOBBY PREMIUM", fonts["tiny"], GOLD_2, (76, 124))
        draw_text(surface, "Casino 67", fonts["mega"], GOLD_2, (72, 148))
        draw_text(surface, "Salão 67", fonts["h1"], WHITE, (75, 230))
        draw_text(surface, "feito por: André B, Christian S, Rony F", fonts["body"], MUTED, (78, 282))
        draw_premium_chip(surface, (1094, 180), 76, "67", fonts["h1"], (math.sin(self.time * 1.6) + 1) / 2)
        draw_text(surface, "Salão principal", fonts["h3"], WHITE, (72, 326))

    def draw_menu_card(self, surface, rect, scene, title, desc, hovered):
        fonts = self.app.fonts
        t = self.hover_progress.get(scene, 0.0)
        shadow = pygame.Surface((rect.w + 34, rect.h + 34), pygame.SRCALPHA)
        shadow_alpha = int(70 + t * 70)
        pygame.draw.rect(shadow, (0, 0, 0, shadow_alpha), pygame.Rect(17, 18, rect.w, rect.h), border_radius=18)
        surface.blit(shadow, (rect.x - 17, rect.y - 10))
        border = lerp_color((71, 84, 112), GOLD_2, t)
        fill = lerp_color(PANEL, (34, 43, 64), t)
        rounded_rect(surface, rect, fill, 18, 2, border)
        hover_image = self.app.images.get("blackjack_hover")
        if scene == "blackjack" and hovered and hover_image:
            blit_cover(surface, hover_image, rect.inflate(-4, -4), 96)
            veil = pygame.Surface(rect.size, pygame.SRCALPHA)
            veil.fill((9, 13, 24, 86))
            surface.blit(veil, rect)
        if t > 0.02:
            glow = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
            sweep_x = int(-rect.w * 0.5 + ((self.time * 170) % (rect.w * 1.8)))
            pygame.draw.polygon(glow, (255, 235, 170, int(34 * t)), [(sweep_x, 0), (sweep_x + 62, 0), (sweep_x + 152, rect.h), (sweep_x + 88, rect.h)])
            surface.blit(glow, rect)
        compact = rect.h < 220
        icon_rect = pygame.Rect(rect.x + 16, rect.y + 22, 96 if compact else 116, 72 if compact else 96)
        draw_game_icon(surface, icon_rect, scene, fonts, hovered)
        title_rect = pygame.Rect(rect.x + (124 if compact else 12), rect.y + (20 if compact else 132), rect.w - (140 if compact else 24), 34)
        draw_centered_wrapped(surface, title, fonts["h3"], WHITE, title_rect, 2)
        desc_panel = pygame.Rect(rect.x + (124 if compact else 14), rect.y + (58 if compact else 174), rect.w - (140 if compact else 28), 48 if compact else 86)
        rounded_rect(surface, desc_panel, (14, 20, 34), 12, 1, lerp_color((62, 76, 104), (132, 112, 66), t))
        draw_wrapped_text(surface, desc, fonts["small"], MUTED, desc_panel.inflate(-14, -10), 4, 2 if compact else 3)
        cta = pygame.Rect(rect.x + 24, rect.bottom - 58, rect.w - 48, 44)
        if t > 0.03:
            cta_glow = pygame.Surface((cta.w + 30, cta.h + 24), pygame.SRCALPHA)
            pygame.draw.rect(cta_glow, (255, 210, 112, int(72 * t)), pygame.Rect(15, 12, cta.w, cta.h), border_radius=12)
            surface.blit(cta_glow, (cta.x - 15, cta.y - 12))

    def draw(self, surface):
        self.draw_lobby_background(surface)
        self.draw_lobby_header(surface)
        mouse = pygame.mouse.get_pos()
        for rect, scene, title, desc, icon in self.card_rects:
            self.draw_menu_card(surface, rect, scene, title, desc, rect.collidepoint(mouse))


class BlackjackScene(CasinoGameScene):
    suits = ["♠", "♥", "♦", "♣"]
    ranks = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]

    def __init__(self, app):
        super().__init__(app)
        self.deck = []
        self.player = []
        self.dealer = []
        self.phase = "ready"
        self.message = "Ajuste a aposta e distribua as cartas."
        self.stake = 0
        self.player_hands = []
        self.hand_stakes = []
        self.active_hand = 0
        self.hand_status = []
        self.card_anim = 0.0
        self.card_anim_owner = None

    def on_enter(self):
        self.message = "Ajuste a aposta e distribua as cartas."
        if self.app.balance < self.bet:
            self.bet = max(self.min_bet, min(self.bet, self.app.balance))

    def can_change_bet(self):
        return self.phase in ("ready", "result")

    def update(self, dt):
        if self.card_anim > 0:
            self.card_anim = max(0, self.card_anim - dt)

    def build_ui(self):
        self.buttons = [Button(pygame.Rect(24, 22, 112, 42), "Menu", lambda: self.app.set_scene("menu"), "secondary")]
        self.add_bet_buttons(850, 604)
        if self.phase in ("ready", "result"):
            self.buttons.append(Button(pygame.Rect(64, 604, 180, 52), "Dar cartas", self.start_hand, "primary", self.app.balance >= self.bet))
        if self.phase == "player":
            self.buttons.extend(
                [
                    Button(pygame.Rect(64, 604, 112, 52), "Carta", self.hit, "blue"),
                    Button(pygame.Rect(188, 604, 112, 52), "Parar", self.stand, "success"),
                    Button(
                        pygame.Rect(312, 604, 112, 52),
                        "Dobrar",
                        self.double_down,
                        "primary",
                        len(self.current_hand()) == 2 and self.app.balance >= self.current_stake(),
                    ),
                    Button(
                        pygame.Rect(436, 604, 92, 52),
                        "Split",
                        self.split_hand,
                        "ghost",
                        self.can_split(),
                    ),
                ]
            )

    def make_deck(self):
        self.deck = [(rank, suit) for suit in self.suits for rank in self.ranks]
        random.shuffle(self.deck)

    def draw_card_from_deck(self):
        if len(self.deck) < 12:
            self.make_deck()
        return self.deck.pop()

    def current_hand(self):
        if not self.player_hands:
            return self.player
        return self.player_hands[self.active_hand]

    def current_stake(self):
        if not self.hand_stakes:
            return self.stake
        return self.hand_stakes[self.active_hand]

    def card_split_value(self, card):
        rank, _ = card
        if rank == "A":
            return 11
        if rank in ("10", "J", "Q", "K"):
            return 10
        return int(rank)

    def can_split(self):
        hand = self.current_hand()
        return (
            self.phase == "player"
            and len(self.player_hands) == 1
            and len(hand) == 2
            and self.card_split_value(hand[0]) == self.card_split_value(hand[1])
            and self.app.balance >= self.current_stake()
        )

    def sync_player_alias(self):
        self.player = self.current_hand() if self.player_hands else []

    def start_hand(self):
        if self.app.balance < self.bet:
            self.message = "Saldo insuficiente para esta aposta."
            return
        self.app.balance -= self.bet
        self.stake = self.bet
        self.make_deck()
        self.player = [self.draw_card_from_deck(), self.draw_card_from_deck()]
        self.dealer = [self.draw_card_from_deck(), self.draw_card_from_deck()]
        self.player_hands = [self.player]
        self.hand_stakes = [self.stake]
        self.active_hand = 0
        self.hand_status = [""]
        self.phase = "player"
        self.card_anim = 0.45
        self.card_anim_owner = "player"
        self.message = "Sua vez: peça carta, pare, dobre ou faça split se possível."
        self.resolve_naturals()

    def resolve_naturals(self):
        player_bj = self.hand_value(self.player) == 21 and len(self.player) == 2
        dealer_bj = self.hand_value(self.dealer) == 21 and len(self.dealer) == 2
        if player_bj and dealer_bj:
            self.app.balance += self.stake
            self.message = "Dois blackjacks. Empate, aposta devolvida."
            self.phase = "result"
        elif player_bj:
            payout = int(self.stake * 2.5)
            self.app.balance += payout
            self.message = f"Blackjack! Você recebeu {br_money(payout)} fichas."
            self.phase = "result"
        elif dealer_bj:
            self.message = "Dealer abriu blackjack. Aposta perdida."
            self.phase = "result"

    def hand_value(self, hand):
        total = 0
        aces = 0
        for rank, _ in hand:
            if rank == "A":
                aces += 1
                total += 11
            elif rank in ("J", "Q", "K"):
                total += 10
            else:
                total += int(rank)
        while total > 21 and aces:
            total -= 10
            aces -= 1
        return total

    def hit(self):
        if self.phase != "player":
            return
        hand = self.current_hand()
        hand.append(self.draw_card_from_deck())
        self.sync_player_alias()
        self.card_anim = 0.35
        self.card_anim_owner = "player"
        value = self.hand_value(hand)
        if value > 21:
            self.hand_status[self.active_hand] = f"estourou com {value}"
            self.message = f"Mão {self.active_hand + 1} estourou com {value}."
            self.advance_hand()
        elif value == 21:
            self.stand()
        else:
            self.message = f"Mão {self.active_hand + 1} vale {value}. Continue ou pare."

    def stand(self):
        if self.phase != "player":
            return
        self.hand_status[self.active_hand] = "parou"
        self.advance_hand()

    def advance_hand(self):
        if self.active_hand + 1 < len(self.player_hands):
            self.active_hand += 1
            self.sync_player_alias()
            value = self.hand_value(self.current_hand())
            self.message = f"Agora jogue a mão {self.active_hand + 1}, valendo {value}."
            return
        self.resolve_dealer()

    def resolve_dealer(self):
        while self.hand_value(self.dealer) < 17:
            self.dealer.append(self.draw_card_from_deck())
            self.card_anim = 0.35
            self.card_anim_owner = "dealer"
        dealer_value = self.hand_value(self.dealer)
        self.phase = "result"
        summaries = []
        total_payout = 0
        for index, hand in enumerate(self.player_hands):
            player_value = self.hand_value(hand)
            stake = self.hand_stakes[index]
            if player_value > 21:
                summaries.append(f"Você perdeu ({player_value})")
            elif dealer_value > 21 or player_value > dealer_value:
                payout = stake * 2
                total_payout += payout
                summaries.append(f"Você venceu {player_value}x{dealer_value}")
            elif player_value == dealer_value:
                total_payout += stake
                summaries.append(f"Você empatou em {player_value}")
            else:
                summaries.append(f"Você perdeu {player_value}x{dealer_value}")
        if total_payout:
            self.app.balance += total_payout
        self.message = f"{'; '.join(summaries)}. Pagamento: {br_money(total_payout)}."

    def double_down(self):
        hand = self.current_hand()
        if self.phase != "player" or len(hand) != 2 or self.app.balance < self.current_stake():
            return
        extra = self.current_stake()
        self.app.balance -= extra
        self.hand_stakes[self.active_hand] += extra
        self.stake = sum(self.hand_stakes)
        hand.append(self.draw_card_from_deck())
        self.sync_player_alias()
        self.card_anim = 0.35
        self.card_anim_owner = "player"
        if self.hand_value(hand) > 21:
            self.hand_status[self.active_hand] = f"dobrou e estourou com {self.hand_value(hand)}"
            self.message = f"Mão {self.active_hand + 1} dobrou e estourou."
        else:
            self.hand_status[self.active_hand] = "dobrou"
        self.advance_hand()

    def split_hand(self):
        if not self.can_split():
            return
        original = self.current_hand()
        stake = self.current_stake()
        self.app.balance -= stake
        first = [original[0], self.draw_card_from_deck()]
        second = [original[1], self.draw_card_from_deck()]
        self.player_hands = [first, second]
        self.hand_stakes = [stake, stake]
        self.hand_status = ["", ""]
        self.active_hand = 0
        self.stake = sum(self.hand_stakes)
        self.sync_player_alias()
        self.card_anim = 0.35
        self.card_anim_owner = "player"
        self.message = "Split feito! Jogue primeiro a mão 1."

    def draw_card(self, surface, card, x, y, hidden=False, animate=False):
        card_surface = pygame.Surface((98, 136), pygame.SRCALPHA)
        pygame.draw.rect(card_surface, (0, 0, 0, 58), pygame.Rect(8, 10, 86, 122), border_radius=13)
        rect = pygame.Rect(3, 4, 86, 122)
        if hidden:
            rounded_rect(card_surface, rect, (115, 28, 50), 12, 2, GOLD)
            inner = pygame.Rect(rect.x + 9, rect.y + 9, rect.w - 18, rect.h - 18)
            rounded_rect(card_surface, inner, (92, 15, 36), 9, 1, (178, 52, 82))
            for i in range(7):
                y_line = rect.y + 18 + i * 14
                pygame.draw.line(card_surface, (180, 55, 83), (rect.x + 13, y_line), (rect.x + 73, y_line), 2)
            draw_text(card_surface, "67", self.app.fonts["h3"], GOLD_2, rect.center, "center")
        else:
            rank, suit = card
            color = RED if suit in ("♥", "♦") else INK
            rounded_rect(card_surface, rect, CARD, 12, 2, (224, 218, 202))
            pygame.draw.rect(card_surface, (255, 255, 255, 48), pygame.Rect(rect.x + 7, rect.y + 8, rect.w - 14, 18), border_radius=8)
            draw_text(card_surface, rank, self.app.fonts["card"], color, (rect.x + 10, rect.y + 8))
            draw_text(card_surface, suit, self.app.fonts["h2"], color, rect.center, "center")
            draw_text(card_surface, rank, self.app.fonts["card"], color, (rect.x + 76, rect.y + 114), "bottomright")
        if animate and self.card_anim > 0:
            progress = 1 - clamp(self.card_anim / 0.45, 0, 1)
            scale = 0.86 + 0.14 * progress
            angle = -7 + 7 * progress
            image = pygame.transform.rotozoom(card_surface, angle, scale)
            target = image.get_rect(center=(x + 43, y + 61 - int((1 - progress) * 42)))
            surface.blit(image, target)
        else:
            surface.blit(card_surface, (x - 3, y - 3))

    def draw_hand(self, surface, title, hand, x, y, hide_first=False, active=False, spacing=96):
        title_color = GOLD_2 if active else MUTED
        draw_text(surface, title, self.app.fonts["body"], title_color, (x, y - 34))
        if active:
            pygame.draw.line(surface, GOLD_2, (x, y - 7), (x + 220, y - 7), 3)
        for i, card in enumerate(hand):
            owner = "dealer" if title == "Dealer" else "player"
            animate = self.card_anim_owner == owner and i == len(hand) - 1
            self.draw_card(surface, card, x + i * spacing, y, hidden=hide_first and i == 0, animate=animate)

    def draw(self, surface):
        self.draw_panel_title(surface, "Blackjack", "Chegue a 21 sem estourar. Blackjack paga 3:2.")
        table = pygame.Rect(48, 172, 1184, 406)
        rounded_rect(surface, table, (10, 76, 59), 26, 5, GOLD)
        inner = table.inflate(-26, -24)
        rounded_rect(surface, inner, (12, 99, 71), 24, 2, (31, 135, 100))
        pygame.draw.ellipse(surface, (16, 126, 88), pygame.Rect(106, 208, 1068, 304), 8)
        pygame.draw.arc(surface, GOLD_2, pygame.Rect(162, 232, 960, 250), math.pi, math.tau, 3)
        draw_text(surface, "BLACKJACK", self.app.fonts["tiny"], (194, 235, 212), (590, 196))
        for cx in (220, 360, 500, 640):
            pygame.draw.circle(surface, (17, 112, 80), (cx, 529), 34, 2)
            pygame.draw.circle(surface, (210, 176, 94), (cx, 529), 22, 1)
        dealer_hidden = self.phase == "player"
        self.draw_hand(surface, "Dealer", self.dealer, 154, 244, dealer_hidden)
        hands = self.player_hands if self.player_hands else ([self.player] if self.player else [])
        if len(hands) > 1:
            for index, hand in enumerate(hands):
                x = 154 + index * 300
                title = f"Mão {index + 1} ({self.hand_value(hand)})"
                self.draw_hand(surface, title, hand, x, 412, False, self.phase == "player" and index == self.active_hand, 72)
        else:
            self.draw_hand(surface, "Você", self.player, 154, 412, False)
        player_value = self.hand_value(self.current_hand()) if hands else 0
        dealer_value = self.hand_value(self.dealer) if self.dealer and not dealer_hidden else "?"
        info_rect = pygame.Rect(760, 228, 360, 248)
        rounded_rect(surface, info_rect, (18, 26, 42), 18, 1, (80, 97, 124))
        draw_text(surface, "PLACAR DA MÃO", self.app.fonts["tiny"], MUTED, (info_rect.x + 24, info_rect.y + 22))
        label = "Mão ativa" if len(hands) > 1 and self.phase == "player" else "Você"
        draw_text(surface, f"{label}: {player_value}", self.app.fonts["h2"], WHITE, (info_rect.x + 24, info_rect.y + 58))
        draw_text(surface, f"Dealer: {dealer_value}", self.app.fonts["h2"], WHITE, (info_rect.x + 24, info_rect.y + 108))
        draw_text(surface, f"Mesa: {br_money(self.stake)} fichas", self.app.fonts["body"], GOLD_2, (info_rect.x + 24, info_rect.y + 166))
        msg_rect = pygame.Rect(502, 604, 320, 74)
        rounded_rect(surface, msg_rect, PANEL_2, 12, 1, (82, 96, 126))
        draw_centered_wrapped(surface, self.message, self.app.fonts["small"], WHITE, msg_rect)
        self.draw_bet_box(surface, 850, 604)


class DiceScene(CasinoGameScene):
    def __init__(self, app):
        super().__init__(app)
        self.selected = "high"
        self.dice = [1, 1]
        self.rolling = 0.0
        self.roll_elapsed = 0.0
        self.roll_duration = 1.35
        self.die_angles = [0, 0]
        self.die_offsets = [(0, 0), (0, 0)]
        self.roll_trails = [[], []]
        self.table_shake = 0.0
        self.die_start_offsets = [(0, 0), (0, 0)]
        self.die_spin_start = [0, 0]
        self.pending_result = None
        self.message = "Escolha o mercado e role os dados."

    def can_change_bet(self):
        return self.rolling <= 0

    def build_ui(self):
        self.buttons = [Button(pygame.Rect(24, 22, 112, 42), "Menu", lambda: self.app.set_scene("menu"), "secondary")]
        self.add_bet_buttons(850, 604)
        markets = [
            ("low", "Baixo 2-6", "1.95x"),
            ("seven", "Sete exato", "5.00x"),
            ("high", "Alto 8-12", "1.95x"),
            ("even", "Par", "1.95x"),
            ("odd", "Ímpar", "1.95x"),
        ]
        for i, (key, label, mult) in enumerate(markets):
            x = 74 + i * 220
            kind = "primary" if self.selected == key else "secondary"
            self.buttons.append(Button(pygame.Rect(x, 512, 190, 48), f"{label}  {mult}", lambda k=key: self.select(k), kind, self.rolling <= 0))
        self.buttons.append(Button(pygame.Rect(64, 604, 180, 52), "Rolar", self.roll, "success", self.rolling <= 0 and self.app.balance >= self.bet))

    def select(self, key):
        if self.rolling <= 0:
            self.selected = key

    def roll(self):
        if self.rolling > 0 or self.app.balance < self.bet:
            return
        self.app.balance -= self.bet
        self.roll_duration = 1.75
        self.roll_elapsed = 0.0
        self.rolling = self.roll_duration
        self.pending_result = [random.randint(1, 6), random.randint(1, 6)]
        self.die_start_offsets = [(-260, -78), (260, -92)]
        self.die_spin_start = [random.choice([-1, 1]) * random.randint(900, 1260), random.choice([-1, 1]) * random.randint(900, 1260)]
        self.die_angles = self.die_spin_start[:]
        self.roll_trails = [[], []]
        self.table_shake = 1.0
        self.message = "Os dados saltaram na mesa..."

    def update(self, dt):
        if self.rolling > 0:
            self.roll_elapsed += dt
            self.rolling -= dt
            progress = clamp(self.roll_elapsed / self.roll_duration, 0, 1)
            energy = (1 - progress) ** 1.7
            ease = 1 - (1 - progress) ** 3
            self.table_shake = energy
            for i in range(2):
                if random.random() < 0.35 + energy * 0.45:
                    self.dice[i] = random.randint(1, 6)
                sx, sy = self.die_start_offsets[i]
                roll_x = sx * (1 - ease)
                roll_y = sy * (1 - ease)
                bounce = abs(math.sin(progress * math.pi * 4.5 + i * 0.6)) * 88 * energy
                jitter_x = math.sin(self.roll_elapsed * 18 + i) * 16 * energy
                jitter_y = math.sin(self.roll_elapsed * 23 + i * 1.4) * 7 * energy
                self.die_angles[i] = self.die_spin_start[i] * (1 - ease) + math.sin(self.roll_elapsed * 20 + i) * 18 * energy
                self.die_offsets[i] = (int(roll_x + jitter_x), int(roll_y - bounce + jitter_y))
                base_x = 450 if i == 0 else 690
                self.roll_trails[i].append((base_x + 67 + self.die_offsets[i][0], 235 + 67 + self.die_offsets[i][1], energy))
                self.roll_trails[i] = self.roll_trails[i][-12:]
            if self.rolling <= 0:
                self.dice = self.pending_result
                self.die_angles = [0, 0]
                self.die_offsets = [(0, 0), (0, 0)]
                self.table_shake = 0.0
                self.finish_roll()

    def finish_roll(self):
        total = sum(self.dice)
        win = False
        multiplier = 1.95
        if self.selected == "low":
            win = 2 <= total <= 6
        elif self.selected == "seven":
            win = total == 7
            multiplier = 5.0
        elif self.selected == "high":
            win = 8 <= total <= 12
        elif self.selected == "even":
            win = total % 2 == 0
        elif self.selected == "odd":
            win = total % 2 == 1
        if win:
            payout = int(self.bet * multiplier)
            self.app.balance += payout
            self.message = f"Saiu {total}. Vitória! Pagamento de {br_money(payout)} fichas."
        else:
            self.message = f"Saiu {total}. Aposta perdida."

    def draw_die(self, surface, rect, value, angle=0, offset=(0, 0)):
        die_surface = pygame.Surface((rect.w + 24, rect.h + 24), pygame.SRCALPHA)
        local = pygame.Rect(8, 6, rect.w, rect.h)
        pygame.draw.rect(die_surface, (0, 0, 0, 70), pygame.Rect(14, 14, rect.w, rect.h), border_radius=22)
        rounded_rect(die_surface, local, CARD, 22, 3, (216, 210, 198))
        pygame.draw.rect(die_surface, (255, 255, 255, 95), pygame.Rect(local.x + 12, local.y + 12, local.w - 24, 28), border_radius=14)
        pygame.draw.line(die_surface, (210, 205, 193), (local.x + 18, local.bottom - 18), (local.right - 18, local.bottom - 18), 2)
        spots = {
            1: [(0.5, 0.5)],
            2: [(0.28, 0.28), (0.72, 0.72)],
            3: [(0.28, 0.28), (0.5, 0.5), (0.72, 0.72)],
            4: [(0.28, 0.28), (0.72, 0.28), (0.28, 0.72), (0.72, 0.72)],
            5: [(0.28, 0.28), (0.72, 0.28), (0.5, 0.5), (0.28, 0.72), (0.72, 0.72)],
            6: [(0.28, 0.24), (0.72, 0.24), (0.28, 0.5), (0.72, 0.5), (0.28, 0.76), (0.72, 0.76)],
        }
        for px, py in spots[value]:
            center = (local.x + int(local.w * px), local.y + int(local.h * py))
            pygame.draw.circle(die_surface, (5, 8, 14), center, 12)
            pygame.draw.circle(die_surface, (42, 47, 57), (center[0] - 3, center[1] - 3), 4)
        image = pygame.transform.rotozoom(die_surface, angle, 1.0)
        target = image.get_rect(center=(rect.centerx + offset[0], rect.centery + offset[1]))
        surface.blit(image, target)

    def draw(self, surface):
        self.draw_panel_title(surface, "Dice", "Dois dados, aposta rápida e pagamentos claros.")
        shake_x = int(math.sin(self.roll_elapsed * 40) * 5 * self.table_shake)
        stage = pygame.Rect(80 + shake_x, 178, 1120, 304)
        rounded_rect(surface, stage, PANEL, 24, 2, (75, 90, 116))
        felt = stage.inflate(-34, -30)
        rounded_rect(surface, felt, (12, 89, 67), 22, 2, (34, 138, 102))
        for i, trail in enumerate(self.roll_trails):
            for j, (x, y, energy) in enumerate(trail):
                alpha = int((j + 1) / max(1, len(trail)) * 46 * energy)
                ghost = pygame.Surface((60, 60), pygame.SRCALPHA)
                pygame.draw.circle(ghost, (255, 244, 210, alpha), (30, 30), 13 + j)
                surface.blit(ghost, (int(x - 30), int(y - 30)))
        pygame.draw.ellipse(surface, (9, 13, 24, 112), pygame.Rect(420 + self.die_offsets[0][0] // 4, 372, 210, 40))
        pygame.draw.ellipse(surface, (9, 13, 24, 112), pygame.Rect(660 + self.die_offsets[1][0] // 4, 372, 210, 40))
        self.draw_die(surface, pygame.Rect(450, 235, 134, 134), self.dice[0], self.die_angles[0], self.die_offsets[0])
        self.draw_die(surface, pygame.Rect(690, 235, 134, 134), self.dice[1], self.die_angles[1], self.die_offsets[1])
        total = sum(self.dice)
        draw_text(surface, str(total), self.app.fonts["mega"], GOLD_2, (640, 415), "center")
        msg_rect = pygame.Rect(292, 604, 510, 74)
        rounded_rect(surface, msg_rect, PANEL_2, 12, 1, (82, 96, 126))
        draw_centered_wrapped(surface, self.message, self.app.fonts["small"], WHITE, msg_rect)
        self.draw_bet_box(surface, 850, 604)


class RouletteScene(CasinoGameScene):
    red_numbers = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}
    wheel_order = [0, 32, 15, 19, 4, 21, 2, 25, 17, 34, 6, 27, 13, 36, 11, 30, 8, 23, 10, 5, 24, 16, 33, 1, 20, 14, 31, 9, 22, 18, 29, 7, 28, 12, 35, 3, 26]

    def __init__(self, app):
        super().__init__(app)
        self.active_bets = {
            "number": set(),
            "color": set(),
            "parity": set(),
            "range": set(),
            "dozen": set(),
        }
        self.current = 0
        self.spinning = 0.0
        self.spin_elapsed = 0.0
        self.spin_duration = 3.2
        self.ball_angle = self.angle_for_number(0)
        self.ball_start_angle = self.ball_angle
        self.ball_target_angle = self.ball_angle
        self.wheel_angle = 0.0
        self.wheel_start_angle = 0.0
        self.wheel_target_angle = 0.0
        self.target = 0
        self.message = "Escolha uma aposta e gire a roleta."
        self.number_rects = []

    def can_change_bet(self):
        return self.spinning <= 0

    def angle_for_number(self, number):
        index = self.wheel_order.index(number)
        return -math.pi / 2 + ((index + 0.5) / len(self.wheel_order)) * math.tau

    def number_from_angle(self, angle):
        normalized = (angle + math.pi / 2) % math.tau
        index = int(normalized / math.tau * len(self.wheel_order)) % len(self.wheel_order)
        return self.wheel_order[index]

    def option_specs(self):
        specs = [
            (("color", "red"), "Vermelho", "danger", 358, 386, 126, 42),
            (("color", "black"), "Preto", "secondary", 492, 386, 126, 42),
            (("parity", "even"), "Par", "blue", 626, 386, 106, 42),
            (("parity", "odd"), "Ímpar", "blue", 740, 386, 106, 42),
            (("range", "low"), "1-18", "ghost", 854, 386, 106, 42),
            (("range", "high"), "19-36", "ghost", 968, 386, 106, 42),
            (("dozen", 1), "1a dúzia", "ghost", 408, 436, 192, 42),
            (("dozen", 2), "2a dúzia", "ghost", 608, 436, 192, 42),
            (("dozen", 3), "3a dúzia", "ghost", 808, 436, 192, 42),
        ]
        return specs

    def bet_count(self):
        return sum(len(values) for values in self.active_bets.values())

    def is_bet_active(self, selection):
        kind, value = selection
        return value in self.active_bets[kind]

    def toggle_bet(self, selection):
        kind, value = selection
        if kind in ("color", "parity", "range"):
            if value in self.active_bets[kind]:
                self.active_bets[kind].clear()
            else:
                self.active_bets[kind] = {value}
        else:
            if value in self.active_bets[kind]:
                self.active_bets[kind].remove(value)
            else:
                self.active_bets[kind].add(value)

    def build_ui(self):
        self.buttons = [Button(pygame.Rect(24, 22, 112, 42), "Menu", lambda: self.app.set_scene("menu"), "secondary")]
        self.add_bet_buttons(850, 604)
        total_cost = self.bet * self.bet_count()
        self.buttons.append(Button(pygame.Rect(64, 604, 180, 52), "Girar", self.spin, "success", self.spinning <= 0 and self.bet_count() > 0 and self.app.balance >= total_cost))
        for selection, label, kind, x, y, w, h in self.option_specs():
            selected_kind = "primary" if self.is_bet_active(selection) else kind
            self.buttons.append(Button(pygame.Rect(x, y, w, h), label, lambda s=selection: self.select(s), selected_kind, self.spinning <= 0))

    def select(self, selection):
        if self.spinning <= 0:
            self.toggle_bet(selection)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self.spinning <= 0:
            for rect, num in self.number_rects:
                if rect.collidepoint(event.pos):
                    self.toggle_bet(("number", num))
                    return True
        return super().handle_event(event)

    def spin(self):
        total_cost = self.bet * self.bet_count()
        if self.spinning > 0 or self.bet_count() == 0 or self.app.balance < total_cost:
            return
        self.app.balance -= total_cost
        self.target = random.randint(0, 36)
        self.spin_duration = random.uniform(3.0, 3.7)
        self.spin_elapsed = 0.0
        self.spinning = self.spin_duration
        self.ball_start_angle = self.ball_angle
        self.wheel_start_angle = self.wheel_angle
        target_center = self.angle_for_number(self.target)
        self.wheel_target_angle = self.wheel_start_angle - math.tau * random.uniform(2.2, 3.4)
        final_wheel_angle = self.wheel_target_angle % math.tau
        final_ball_angle = target_center + final_wheel_angle
        delta = (final_ball_angle - self.ball_start_angle) % math.tau
        self.ball_target_angle = self.ball_start_angle + delta + math.tau * random.randint(5, 7)
        self.message = "A bolinha está girando..."

    def update(self, dt):
        if self.spinning > 0:
            self.spin_elapsed += dt
            self.spinning -= dt
            progress = clamp(self.spin_elapsed / self.spin_duration, 0, 1)
            eased = 1 - (1 - progress) ** 3
            wheel_ease = 1 - (1 - progress) ** 2.2
            self.wheel_angle = self.wheel_start_angle + (self.wheel_target_angle - self.wheel_start_angle) * wheel_ease
            self.ball_angle = self.ball_start_angle + (self.ball_target_angle - self.ball_start_angle) * eased
            self.current = self.number_from_angle(self.ball_angle - self.wheel_angle)
            if self.spinning <= 0:
                self.current = self.target
                self.wheel_angle = self.wheel_target_angle % math.tau
                self.ball_angle = self.angle_for_number(self.target) + self.wheel_angle
                self.finish_spin()

    def number_color(self, number):
        if number == 0:
            return GREEN
        return RED if number in self.red_numbers else BLACK

    def finish_spin(self):
        num = self.current
        payout = 0
        wins = []
        for value in self.active_bets["number"]:
            if num == value:
                payout += self.bet * 36
                wins.append(f"número {value}")
        for value in self.active_bets["color"]:
            if num != 0 and ((value == "red" and num in self.red_numbers) or (value == "black" and num not in self.red_numbers)):
                payout += self.bet * 2
                wins.append("vermelho" if value == "red" else "preto")
        for value in self.active_bets["parity"]:
            if num != 0 and ((value == "even" and num % 2 == 0) or (value == "odd" and num % 2 == 1)):
                payout += self.bet * 2
                wins.append("par" if value == "even" else "ímpar")
        for value in self.active_bets["range"]:
            if (value == "low" and 1 <= num <= 18) or (value == "high" and 19 <= num <= 36):
                payout += self.bet * 2
                wins.append("1-18" if value == "low" else "19-36")
        for value in self.active_bets["dozen"]:
            if num != 0 and (num - 1) // 12 + 1 == value:
                payout += self.bet * 3
                wins.append(f"{value}a dúzia")
        if payout:
            self.app.balance += payout
            self.message = f"Caiu {num}. Venceram: {', '.join(wins)}. Total: {br_money(payout)} fichas."
        else:
            self.message = f"Caiu {num}. Nenhuma aposta ativa venceu."

    def draw_wheel(self, surface, center, radius):
        pygame.draw.circle(surface, (12, 16, 26), center, radius + 16)
        pygame.draw.circle(surface, GOLD, center, radius + 12, 4)
        for i, number in enumerate(self.wheel_order):
            angle = self.wheel_angle - math.pi / 2 + (i / 37) * math.tau
            next_angle = self.wheel_angle - math.pi / 2 + ((i + 1) / 37) * math.tau
            points = [center]
            for a in (angle, (angle + next_angle) / 2, next_angle):
                points.append((int(center[0] + math.cos(a) * radius), int(center[1] + math.sin(a) * radius)))
            pygame.draw.polygon(surface, self.number_color(number), points)
            label_angle = (angle + next_angle) / 2
            label_pos = (int(center[0] + math.cos(label_angle) * (radius * 0.72)), int(center[1] + math.sin(label_angle) * (radius * 0.72)))
            draw_text(surface, str(number), self.app.fonts["tiny"], WHITE, label_pos, "center")
        pygame.draw.circle(surface, (17, 23, 37), center, int(radius * 0.62))
        pygame.draw.circle(surface, (89, 68, 37), center, int(radius * 0.32))
        pygame.draw.circle(surface, GOLD_2, center, int(radius * 0.14))
        angle = self.ball_angle
        ball = (int(center[0] + math.cos(angle) * (radius * 0.82)), int(center[1] + math.sin(angle) * (radius * 0.82)))
        pygame.draw.circle(surface, WHITE, ball, 10)
        draw_text(surface, str(self.current), self.app.fonts["h1"], WHITE, center, "center")

    def draw_number_grid(self, surface):
        self.number_rects = []
        x0, y0 = 408, 194
        cell, gap = 48, 4
        zero = pygame.Rect(x0 - 56, y0, cell, cell * 3 + gap * 2)
        self.number_rects.append((zero, 0))
        color = self.number_color(0)
        rounded_rect(surface, zero, color, 8, 2, GOLD if self.is_bet_active(("number", 0)) else (68, 82, 105))
        draw_text(surface, "0", self.app.fonts["h3"], WHITE, zero.center, "center")
        for n in range(1, 37):
            col = (n - 1) // 3
            row = 2 - ((n - 1) % 3)
            rect = pygame.Rect(x0 + col * (cell + gap), y0 + row * (cell + gap), cell, cell)
            self.number_rects.append((rect, n))
            border = GOLD if self.is_bet_active(("number", n)) else (68, 82, 105)
            rounded_rect(surface, rect, self.number_color(n), 7, 2, border)
            draw_text(surface, str(n), self.app.fonts["small"], WHITE, rect.center, "center")

    def selection_text(self):
        labels = []
        labels.extend(f"N{num}" for num in sorted(self.active_bets["number"]))
        labels.extend("Vermelho" if value == "red" else "Preto" for value in sorted(self.active_bets["color"]))
        labels.extend("Par" if value == "even" else "Ímpar" for value in sorted(self.active_bets["parity"]))
        labels.extend("1-18" if value == "low" else "19-36" for value in sorted(self.active_bets["range"]))
        labels.extend(f"{value}a dúzia" for value in sorted(self.active_bets["dozen"]))
        if not labels:
            return "nenhuma aposta"
        text = ", ".join(labels)
        return text if len(text) <= 62 else f"{text[:59]}..."

    def draw(self, surface):
        self.draw_panel_title(surface, "Roleta", "Mesa europeia 0-36 com apostas internas e externas.")
        self.draw_wheel(surface, (172, 326), 128)
        table = pygame.Rect(330, 182, 874, 354)
        rounded_rect(surface, table, (11, 101, 68), 18, 3, (30, 139, 94))
        draw_text(surface, "NÚMEROS", self.app.fonts["tiny"], (190, 232, 207), (354, 192))
        self.draw_number_grid(surface)
        options_panel = pygame.Rect(344, 368, 760, 126)
        rounded_rect(surface, options_panel, (15, 73, 58), 14, 1, (60, 152, 117))
        draw_text(surface, "APOSTAS EXTERNAS", self.app.fonts["tiny"], (190, 232, 207), (362, 374))
        draw_text(surface, f"Selecionado: {self.selection_text()}", self.app.fonts["body"], GOLD_2, (356, 506))
        draw_text(surface, f"{self.bet_count()} apostas | custo {br_money(self.bet * self.bet_count())}", self.app.fonts["small"], MUTED, (920, 506))
        msg_rect = pygame.Rect(292, 604, 510, 74)
        rounded_rect(surface, msg_rect, PANEL_2, 12, 1, (82, 96, 126))
        draw_centered_wrapped(surface, self.message, self.app.fonts["small"], WHITE, msg_rect)
        self.draw_bet_box(surface, 850, 604)


class SlotsScene(CasinoGameScene):
    reel_cell_w = 116
    reel_cell_h = 108
    reel_gap = 10
    reel_tape_size = 34
    reel_target_index = 8
    symbols = [
        ("67", 14, (255, 224, 119), 6),
        ("7", 11, (255, 95, 95), 8),
        ("TREINO", 9, (95, 210, 255), 10),
        ("JOGO", 7, (230, 230, 238), 12),
        ("41", 6, (186, 150, 255), 14),
        ("6", 5, (118, 212, 255), 17),
        ("CHERRY", 3, (255, 84, 105), 22),
    ]
    paylines = [
        [0, 0, 0, 0, 0],
        [1, 1, 1, 1, 1],
        [2, 2, 2, 2, 2],
        [0, 1, 2, 1, 0],
        [2, 1, 0, 1, 2],
    ]

    def __init__(self, app):
        super().__init__(app)
        self.grid = [[self.pick_symbol()[0] for _ in range(5)] for _ in range(3)]
        self.spinning = 0.0
        self.reels = [self.create_idle_reel(col) for col in range(5)]
        self.message = "Gire os rolos. Sequências da esquerda pagam."
        self.last_lines = []

    def can_change_bet(self):
        return self.spinning <= 0

    def reel_step(self):
        return self.reel_cell_h + self.reel_gap

    def random_symbol_name(self):
        return self.pick_symbol()[0]

    def create_tape(self, visible_symbols=None, target_symbols=None):
        tape = [self.random_symbol_name() for _ in range(self.reel_tape_size)]
        if visible_symbols:
            for i, symbol in enumerate(visible_symbols):
                tape[i] = symbol
        if target_symbols:
            for i, symbol in enumerate(target_symbols):
                tape[self.reel_target_index + i] = symbol
        return tape

    def create_idle_reel(self, col):
        visible = [self.grid[row][col] for row in range(3)]
        return {
            "symbols": self.create_tape(visible_symbols=visible),
            "offset": 0.0,
            "speed": 0.0,
            "stopping": False,
            "target": visible,
            "target_offset": 0.0,
            "start_offset": 0.0,
            "elapsed": 0.0,
            "duration": 0.0,
            "state": "idle",
            "stop_flash": 0.0,
        }

    def current_reel_visible(self, reel):
        step = self.reel_step()
        base_index = int(reel["offset"] // step)
        return [reel["symbols"][(base_index + row) % len(reel["symbols"])] for row in range(3)]

    def prepare_reel_spin(self, col, target_symbols):
        step = self.reel_step()
        reel = self.reels[col]
        current_visible = self.current_reel_visible(reel)
        tape = self.create_tape(visible_symbols=current_visible, target_symbols=target_symbols)
        current_offset = 0.0
        cycle = len(tape) * step
        target_base = self.reel_target_index * step
        cycles_to_clear_current = max(0, math.floor((current_offset - target_base) / cycle) + 1)
        target_offset = target_base + (cycles_to_clear_current + 1 + col) * cycle
        duration = 1.75 + col * 0.32
        reel.update(
            {
                "symbols": tape,
                "offset": current_offset,
                "speed": 0.0,
                "stopping": True,
                "target": target_symbols,
                "target_offset": target_offset,
                "start_offset": current_offset,
                "elapsed": 0.0,
                "duration": duration,
                "state": "spinning",
                "stop_flash": 0.0,
            }
        )

    def update_reel(self, reel, dt):
        if reel["state"] != "spinning":
            return False
        reel["elapsed"] += dt
        progress = clamp(reel["elapsed"] / reel["duration"], 0.0, 1.0)
        eased = 1 - (1 - progress) ** 3
        settle = clamp((progress - 0.78) / 0.22, 0.0, 1.0)
        bounce = math.sin(settle * math.pi) * (1 - settle) * self.reel_step() * 0.26
        previous = reel["offset"]
        reel["offset"] = reel["start_offset"] + (reel["target_offset"] - reel["start_offset"]) * eased + bounce
        reel["speed"] = (reel["offset"] - previous) / dt if dt > 0 else 0.0
        if progress >= 1:
            reel["offset"] = reel["target_offset"]
            reel["speed"] = 0.0
            reel["stopping"] = False
            reel["state"] = "settled"
            reel["stop_flash"] = 0.42
        return reel["state"] == "spinning"

    def pick_symbol(self):
        total = sum(weight for _, _, _, weight in self.symbols)
        r = random.uniform(0, total)
        upto = 0
        for symbol, base, color, weight in self.symbols:
            upto += weight
            if r <= upto:
                return symbol, base, color
        symbol, base, color, _ = self.symbols[-1]
        return symbol, base, color

    def symbol_info(self, symbol):
        for name, base, color, _ in self.symbols:
            if name == symbol:
                return base, color
        return 1, WHITE

    def symbol_label(self, symbol):
        labels = {"CHERRY": "Cereja", "VBUCKS": "V-Bucks"}
        return labels.get(symbol, symbol)

    def symbol_short_label(self, symbol):
        labels = {"CHERRY": "Cereja", "VBUCKS": "VB", "TREINO": "Treino", "JOGO": "Jogo"}
        return labels.get(symbol, symbol)

    def build_ui(self):
        self.buttons = [Button(pygame.Rect(24, 22, 112, 42), "Menu", lambda: self.app.set_scene("menu"), "secondary")]
        self.add_bet_buttons(850, 604)
        self.buttons.append(Button(pygame.Rect(64, 604, 180, 52), "Girar", self.spin, "success", self.spinning <= 0 and self.app.balance >= self.bet))

    def spin(self):
        if self.spinning > 0 or self.app.balance < self.bet:
            return
        self.app.balance -= self.bet
        final_grid = [[self.pick_symbol()[0] for _ in range(5)] for _ in range(3)]
        self.grid = final_grid
        for col in range(5):
            target_symbols = [final_grid[row][col] for row in range(3)]
            self.prepare_reel_spin(col, target_symbols)
        self.spinning = max(reel["duration"] for reel in self.reels)
        self.last_lines = []
        self.message = "Rolos girando..."

    def update(self, dt):
        any_spinning = False
        for reel in self.reels:
            if self.update_reel(reel, dt):
                any_spinning = True
            if reel["stop_flash"] > 0:
                reel["stop_flash"] = max(0.0, reel["stop_flash"] - dt)
        if self.spinning > 0:
            if any_spinning:
                self.spinning = max(max(0.0, reel["duration"] - reel["elapsed"]) for reel in self.reels)
            else:
                self.spinning = 0.0
                self.finish_spin()

    def finish_spin(self):
        payout_factor = 0
        self.last_lines = []
        for idx, line in enumerate(self.paylines):
            values = [self.grid[row][col] for col, row in enumerate(line)]
            first = values[0]
            count = 1
            for sym in values[1:]:
                if sym == first:
                    count += 1
                else:
                    break
            if count >= 3:
                base, _ = self.symbol_info(first)
                factor = base if count == 3 else int(base * 2.5) if count == 4 else base * 5
                payout_factor += factor
                self.last_lines.append((idx, count, first, factor))
        if payout_factor:
            payout = self.bet * payout_factor
            self.app.balance += payout
            lines = ", ".join(f"{self.symbol_label(sym)} x{count}" for _, count, sym, _ in self.last_lines)
            self.message = f"{lines}. Pagamento total: {br_money(payout)} fichas."
        else:
            self.message = "Sem sequência premiada desta vez."

    def draw_symbol(self, surface, rect, symbol):
        base, color = self.symbol_info(symbol)
        rounded_rect(surface, rect, (245, 239, 220), 14, 2, (203, 191, 164))
        inner = rect.inflate(-18, -18)
        rounded_rect(surface, inner, (28, 35, 54), 12, 1, (68, 81, 108))
        pygame.draw.rect(surface, (255, 255, 255, 38), pygame.Rect(inner.x + 8, inner.y + 8, inner.w - 16, 18), border_radius=9)
        if symbol == "7":
            draw_text(surface, "7", self.app.fonts["mega"], color, (rect.centerx, rect.centery - 4), "center")
            pygame.draw.line(surface, GOLD_2, (rect.centerx - 20, rect.centery + 28), (rect.centerx + 22, rect.centery + 28), 3)
        elif symbol == "67":
            draw_chip(surface, rect.center, 34, "67", self.app.fonts["h3"])
        elif symbol == "TREINO":
            band = pygame.Rect(inner.x + 10, inner.centery - 16, inner.w - 20, 32)
            rounded_rect(surface, band, (18, 21, 30), 8, 2, color)
            draw_text(surface, "Treino", self.app.fonts["small"], color, band.center, "center")
        elif symbol == "JOGO":
            band = pygame.Rect(inner.x + 10, inner.centery - 16, inner.w - 20, 32)
            rounded_rect(surface, band, (18, 21, 30), 8, 2, color)
            draw_text(surface, "Jogo", self.app.fonts["h3"], color, band.center, "center")
        elif symbol == "6":
            draw_text(surface, "6", self.app.fonts["mega"], color, rect.center, "center")
        elif symbol == "41":
            draw_text(surface, "41", self.app.fonts["h1"], color, rect.center, "center")
            pygame.draw.circle(surface, GOLD_2, (rect.centerx + 28, rect.centery - 28), 5)
        elif symbol == "VBUCKS":
            pygame.draw.circle(surface, (224, 247, 255), rect.center, 35)
            pygame.draw.circle(surface, color, rect.center, 35, 5)
            pygame.draw.circle(surface, (22, 92, 145), rect.center, 23, 3)
            draw_text(surface, "V", self.app.fonts["h1"], (22, 92, 145), (rect.centerx, rect.centery + 1), "center")
        elif symbol == "CHERRY":
            pygame.draw.line(surface, GREEN, (rect.centerx + 3, rect.centery - 22), (rect.centerx + 18, rect.centery - 42), 4)
            pygame.draw.circle(surface, color, (rect.centerx - 12, rect.centery + 8), 18)
            pygame.draw.circle(surface, (230, 38, 66), (rect.centerx + 13, rect.centery + 8), 18)
            pygame.draw.circle(surface, WHITE, (rect.centerx - 18, rect.centery + 1), 4)
            pygame.draw.circle(surface, WHITE, (rect.centerx + 7, rect.centery + 1), 4)
        else:
            draw_diamond(surface, rect.center, 34, color, WHITE, 2)
            draw_text(surface, symbol, self.app.fonts["h3"], (18, 29, 44), rect.center, "center")

    def draw_reel(self, surface, reel, reel_rect):
        step = self.reel_step()
        old_clip = surface.get_clip()
        surface.set_clip(reel_rect)
        rounded_rect(surface, reel_rect, (15, 19, 31), 12, 1, (52, 62, 86))
        base_index = int(reel["offset"] // step)
        fraction = (reel["offset"] % step) / step
        y_start = reel_rect.y - fraction * step
        for visual_row in range(-1, 5):
            symbol_index = (base_index + visual_row) % len(reel["symbols"])
            symbol = reel["symbols"][symbol_index]
            y = y_start + visual_row * step
            rect = pygame.Rect(reel_rect.x, int(y), self.reel_cell_w, self.reel_cell_h)
            self.draw_symbol(surface, rect, symbol)
        if reel["state"] == "spinning" and abs(reel["speed"]) > 900:
            blur_alpha = int(clamp(abs(reel["speed"]) / 6200, 0, 1) * 70)
            blur = pygame.Surface(reel_rect.size, pygame.SRCALPHA)
            pygame.draw.rect(blur, (9, 12, 22, blur_alpha), blur.get_rect(), 0)
            for x in range(14, reel_rect.w, 22):
                pygame.draw.line(blur, (255, 244, 200, blur_alpha), (x, 10), (x, reel_rect.h - 10), 2)
            surface.blit(blur, reel_rect)
        if reel["stop_flash"] > 0:
            flash = clamp(reel["stop_flash"] / 0.42, 0, 1)
            flash_layer = pygame.Surface(reel_rect.size, pygame.SRCALPHA)
            pygame.draw.rect(flash_layer, (*GOLD_2, int(90 * flash)), flash_layer.get_rect(), 3, border_radius=13)
            surface.blit(flash_layer, reel_rect)
        surface.set_clip(old_clip)

    def draw_paylines(self, surface, slot_rect):
        colors = [GOLD_2, BLUE, RED, GREEN, PURPLE]
        cell_w, cell_h, gap = 116, 108, 10
        x0 = slot_rect.x + (slot_rect.w - (5 * cell_w + 4 * gap)) // 2
        y0 = slot_rect.y + 35
        for idx, line in enumerate(self.paylines):
            if not any(found[0] == idx for found in self.last_lines):
                continue
            pts = []
            for col, row in enumerate(line):
                pts.append((x0 + col * (cell_w + gap) + cell_w // 2, y0 + row * (cell_h + gap) + cell_h // 2))
            pygame.draw.lines(surface, colors[idx], False, pts, 6)

    def draw(self, surface):
        self.draw_panel_title(surface, "Slots", "Cinco rolos, cinco linhas e símbolo 67 como prêmio máximo.")
        pay_rect = pygame.Rect(50, 178, 214, 388)
        rounded_rect(surface, pay_rect, PANEL, 18, 1, (76, 90, 118))
        draw_text(surface, "TABELA", self.app.fonts["tiny"], MUTED, (pay_rect.x + 18, pay_rect.y + 16))
        draw_text(surface, "3x   4x   5x", self.app.fonts["tiny"], GOLD_2, (pay_rect.x + 96, pay_rect.y + 42))
        for i, (sym, base, color, _) in enumerate(self.symbols):
            y = pay_rect.y + 68 + i * 44
            mini = pygame.Rect(pay_rect.x + 14, y, 66, 34)
            rounded_rect(surface, mini, (24, 31, 49), 8, 1, color)
            draw_text(surface, self.symbol_short_label(sym), self.app.fonts["tiny"], color, mini.center, "center")
            draw_text(surface, f"{base}", self.app.fonts["small"], WHITE, (pay_rect.x + 98, y + 7))
            draw_text(surface, f"{int(base * 2.5)}", self.app.fonts["small"], WHITE, (pay_rect.x + 136, y + 7))
            draw_text(surface, f"{base * 5}", self.app.fonts["small"], WHITE, (pay_rect.x + 178, y + 7))

        slot_rect = pygame.Rect(292, 178, 912, 388)
        rounded_rect(surface, slot_rect, (91, 18, 49), 24, 5, GOLD)
        inner = pygame.Rect(slot_rect.x + 16, slot_rect.y + 18, slot_rect.w - 32, slot_rect.h - 36)
        rounded_rect(surface, inner, (20, 25, 42), 18, 2, (116, 92, 63))
        cell_w, cell_h, gap = 116, 108, 10
        x0 = slot_rect.x + (slot_rect.w - (5 * cell_w + 4 * gap)) // 2
        y0 = slot_rect.y + 35
        for col, reel in enumerate(self.reels):
            reel_rect = pygame.Rect(x0 + col * (cell_w + gap), y0, cell_w, cell_h * 3 + gap * 2)
            self.draw_reel(surface, reel, reel_rect)
        self.draw_paylines(surface, slot_rect)
        msg_rect = pygame.Rect(292, 604, 510, 74)
        rounded_rect(surface, msg_rect, PANEL_2, 12, 1, (82, 96, 126))
        draw_centered_wrapped(surface, self.message, self.app.fonts["small"], WHITE, msg_rect)
        self.draw_bet_box(surface, 850, 604)


class PlinkoScene(CasinoGameScene):
    risk_profiles = {
        "low": {
            "label": "Baixo risco",
            "center": 0.8,
            "edge": 3.0,
            "curve": 1.9,
        },
        "medium": {
            "label": "Médio risco",
            "center": 0.5,
            "edge": 8.0,
            "curve": 2.35,
        },
        "high": {
            "label": "Alto risco",
            "center": 0.2,
            "edge": 26.0,
            "curve": 3.1,
        },
    }

    def __init__(self, app):
        super().__init__(app)
        self.rows = 10
        self.risk = "medium"
        self.state = "idle"
        self.message = "Escolha o risco, ajuste a aposta e solte a bola."
        self.balls = []
        self.bucket_hits = [0 for _ in range(self.rows + 1)]
        self.bucket_flash = [0.0 for _ in range(self.rows + 1)]
        self.segment_time = 0.17
        self.result_timer = 0.0
        self.round_cost = 0
        self.round_payout = 0
        self.finished_balls = 0
        self.launched_balls = 0
        self.next_ball_id = 0

    def can_change_bet(self):
        return True

    def board_geometry(self):
        pin_gap = 52 if self.rows <= 10 else 45 if self.rows <= 12 else 39
        row_gap = 31 if self.rows <= 10 else 27 if self.rows <= 12 else 24
        return {
            "center_x": 445,
            "top_y": 206,
            "row_gap": row_gap,
            "pin_gap": pin_gap,
            "bucket_y": 536,
        }

    def pin_position(self, row, col):
        geo = self.board_geometry()
        x = geo["center_x"] + (col - row / 2) * geo["pin_gap"]
        y = geo["top_y"] + row * geo["row_gap"]
        return (x, y)

    def bucket_center(self, index):
        geo = self.board_geometry()
        x = geo["center_x"] + (index - self.rows / 2) * geo["pin_gap"]
        return (x, geo["bucket_y"] - 18)

    def current_multipliers(self):
        profile = self.risk_profiles[self.risk]
        multipliers = []
        middle = self.rows / 2
        for index in range(self.rows + 1):
            distance = abs(index - middle) / middle if middle else 0
            value = profile["center"] + (profile["edge"] - profile["center"]) * (distance ** profile["curve"])
            multipliers.append(round(value, 1))
        return multipliers

    def active_ball_count(self):
        return sum(1 for ball in self.balls if ball["state"] in ("waiting", "dropping"))

    def build_ui(self):
        self.buttons = [Button(pygame.Rect(24, 22, 112, 42), "Menu", lambda: self.app.set_scene("menu"), "secondary")]
        self.add_bet_buttons(850, 604)
        self.buttons.append(Button(pygame.Rect(64, 604, 180, 52), "Soltar bola", self.start_drop, "success", self.app.balance >= self.bet))
        risk_buttons = [
            ("low", "Baixo", 878, 214),
            ("medium", "Médio", 966, 214),
            ("high", "Alto", 1054, 214),
        ]
        risk_enabled = self.active_ball_count() == 0
        for risk, label, x, y in risk_buttons:
            kind = "primary" if self.risk == risk else "secondary"
            self.buttons.append(Button(pygame.Rect(x, y, 78, 42), label, lambda r=risk: self.set_risk(r), kind, risk_enabled))
        column_buttons = [
            (10, "11", 878),
            (12, "13", 966),
            (14, "15", 1054),
        ]
        for rows, label, x in column_buttons:
            kind = "primary" if self.rows == rows else "secondary"
            self.buttons.append(Button(pygame.Rect(x, 314, 78, 42), label, lambda r=rows: self.set_rows(r), kind, risk_enabled))

    def set_risk(self, risk):
        if self.active_ball_count() > 0:
            return
        self.risk = risk
        self.message = f"Perfil selecionado: {self.risk_profiles[risk]['label']}."

    def set_rows(self, rows):
        if self.active_ball_count() > 0:
            return
        self.rows = rows
        self.bucket_hits = [0 for _ in range(self.rows + 1)]
        self.bucket_flash = [0.0 for _ in range(self.rows + 1)]
        self.balls = []
        self.message = f"Mesa ajustada para {self.rows + 1} colunas."

    def start_drop(self):
        if self.app.balance < self.bet:
            return
        if self.active_ball_count() == 0:
            self.balls = []
            self.round_cost = 0
            self.round_payout = 0
            self.finished_balls = 0
            self.launched_balls = 0
            self.bucket_hits = [0 for _ in range(self.rows + 1)]
            self.bucket_flash = [0.0 for _ in range(self.rows + 1)]
        self.app.balance -= self.bet
        self.round_cost += self.bet
        self.launched_balls += 1
        self.balls.append(self.create_ball(self.next_ball_id))
        self.next_ball_id += 1
        self.result_timer = 0.0
        self.state = "dropping"
        self.message = f"Bola lançada. Em queda: {self.active_ball_count()}."

    def generate_path(self):
        points = []
        steps = []
        pin_slots = []
        geo = self.board_geometry()
        slot = 0
        points.append((geo["center_x"], geo["top_y"] - 44))
        for row in range(self.rows):
            points.append(self.pin_position(row, slot))
            pin_slots.append(slot)
            step = random.choice([0, 1])
            steps.append(step)
            slot += step
        points.append(self.bucket_center(slot))
        return points, steps, slot, pin_slots

    def create_ball(self, index):
        path_points, path_steps, bucket_index, pin_slots = self.generate_path()
        multiplier = self.current_multipliers()[bucket_index]
        payout = int(self.bet * multiplier)
        colors = [
            (229, 48, 70),
            (88, 148, 255),
            (255, 174, 99),
            (90, 220, 184),
            (149, 119, 255),
        ]
        delay = 0.0
        start_x, start_y = path_points[0]
        spread = ((index % 5) - 2) * 5
        path_points = list(path_points)
        path_points[0] = (start_x + spread, start_y)
        return {
            "id": index,
            "pos": path_points[0],
            "path_points": path_points,
            "path_steps": path_steps,
            "pin_slots": pin_slots,
            "target_bucket": bucket_index,
            "multiplier": multiplier,
            "payout": payout,
            "elapsed": -delay,
            "duration": (len(path_points) - 1) * self.segment_time,
            "state": "waiting",
            "finished": False,
            "credited": False,
            "color": colors[index % len(colors)],
            "radius": 11,
        }

    def update(self, dt):
        for i in range(len(self.bucket_flash)):
            self.bucket_flash[i] = max(0.0, self.bucket_flash[i] - dt)
        if self.state == "dropping":
            for ball in self.balls:
                self.update_ball(ball, dt)
            active = self.active_ball_count()
            self.message = f"Em queda: {active} | Payout parcial: {br_money(self.round_payout)} fichas."
            if self.balls and all(ball["finished"] for ball in self.balls):
                self.finish_round()
        elif self.state == "result":
            self.result_timer += dt

    def update_ball(self, ball, dt):
        if ball["finished"]:
            return
        ball["elapsed"] += dt
        if ball["elapsed"] < 0:
            ball["state"] = "waiting"
            return
        ball["state"] = "dropping"
        if ball["elapsed"] >= ball["duration"]:
            ball["pos"] = ball["path_points"][-1]
            self.finish_ball(ball)
            return
        total_segments = len(ball["path_points"]) - 1
        segment = min(total_segments - 1, int(ball["elapsed"] / self.segment_time))
        local = (ball["elapsed"] - segment * self.segment_time) / self.segment_time
        local = clamp(local, 0.0, 1.0)
        ball["pos"] = self.interpolate_ball(ball, segment, local)

    def interpolate_ball(self, ball, segment, local):
        x1, y1 = ball["path_points"][segment]
        x2, y2 = ball["path_points"][segment + 1]
        eased = local * local * (3 - 2 * local)
        x = x1 + (x2 - x1) * eased
        y = y1 + (y2 - y1) * eased
        arc = math.sin(local * math.pi) * 13
        wobble = math.sin((segment + 1) * 1.7 + ball["id"] * 0.9 + local * math.pi) * 4 * (1 - abs(local - 0.5))
        return (x + wobble, y - arc)

    def finish_ball(self, ball):
        if ball["credited"]:
            return
        ball["finished"] = True
        ball["state"] = "finished"
        ball["credited"] = True
        self.app.balance += ball["payout"]
        self.round_payout += ball["payout"]
        self.finished_balls += 1
        bucket = ball["target_bucket"]
        self.bucket_hits[bucket] += 1
        self.bucket_flash[bucket] = 0.65

    def finish_round(self):
        self.state = "result"
        self.result_timer = 0.0
        self.message = f"Rodada concluída: {self.finished_balls} bolas, pagamento total de {br_money(self.round_payout)} fichas."

    def active_pin_glow(self, row, col):
        if self.state != "dropping":
            return 0.0
        glow = 0.0
        for ball in self.balls:
            if ball["state"] != "dropping" or ball["elapsed"] < 0:
                continue
            segment = int(ball["elapsed"] / self.segment_time)
            local = (ball["elapsed"] - segment * self.segment_time) / self.segment_time
            pin_row = segment - 1
            if 0 <= pin_row < self.rows and local < 0.36 and ball["pin_slots"][pin_row] == col and pin_row == row:
                glow = max(glow, 1 - local / 0.36)
        return glow

    def draw_pin_board(self, surface, board_rect):
        rounded_rect(surface, board_rect, (12, 24, 37), 24, 2, (74, 91, 116))
        inner = board_rect.inflate(-24, -24)
        rounded_rect(surface, inner, (8, 70, 57), 20, 1, (30, 139, 94))
        pygame.draw.arc(surface, (224, 184, 95), pygame.Rect(board_rect.x + 74, board_rect.y + 42, board_rect.w - 148, board_rect.h - 78), math.pi, math.tau, 3)
        for row in range(self.rows):
            for col in range(row + 1):
                x, y = self.pin_position(row, col)
                pulse = self.active_pin_glow(row, col)
                pygame.draw.circle(surface, (15, 31, 41), (int(x), int(y + 4)), 8)
                pygame.draw.circle(surface, lerp_color((214, 191, 140), GOLD_2, pulse), (int(x), int(y)), int(5 + pulse * 4))
                pygame.draw.circle(surface, WHITE, (int(x - 1), int(y - 2)), 2)

    def draw_buckets(self, surface):
        multipliers = self.current_multipliers()
        geo = self.board_geometry()
        bucket_w = max(34, min(46, int(geo["pin_gap"] - 4)))
        colors = [(44, 90, 80), (54, 102, 82), (75, 110, 78), (93, 113, 72), (105, 100, 68), (121, 78, 72)]
        for i, mult in enumerate(multipliers):
            cx, _ = self.bucket_center(i)
            rect = pygame.Rect(int(cx - bucket_w / 2), 512, bucket_w, 54)
            distance = abs(i - self.rows / 2) / (self.rows / 2)
            color = lerp_color(colors[0], (126, 35, 54), distance)
            selected = self.bucket_hits[i] > 0
            if selected:
                pulse = max(self.bucket_flash[i], (math.sin(self.result_timer * 8) + 1) / 2 * 0.45 if self.state == "result" else 0)
                glow = pygame.Surface((rect.w + 26, rect.h + 26), pygame.SRCALPHA)
                pygame.draw.rect(glow, (*GOLD_2, int(55 + pulse * 85)), pygame.Rect(13, 13, rect.w, rect.h), border_radius=10)
                surface.blit(glow, (rect.x - 13, rect.y - 13))
            rounded_rect(surface, rect, color, 8, 2, GOLD_2 if selected else (84, 99, 128))
            draw_text(surface, f"{mult:g}x", self.app.fonts["tiny"], WHITE, rect.center, "center")
            if self.bucket_hits[i] > 1:
                draw_text(surface, f"x{self.bucket_hits[i]}", self.app.fonts["tiny"], GOLD_2, (rect.centerx, rect.y - 10), "center")

    def draw_ball(self, surface, ball):
        x, y = ball["pos"]
        radius = ball["radius"]
        shadow = pygame.Surface((44, 44), pygame.SRCALPHA)
        pygame.draw.circle(shadow, (0, 0, 0, 90), (22, 25), radius)
        surface.blit(shadow, (int(x - 22), int(y - 18)))
        pygame.draw.circle(surface, ball["color"], (int(x), int(y)), radius)
        pygame.draw.circle(surface, lerp_color(ball["color"], WHITE, 0.45), (int(x - radius * 0.35), int(y - radius * 0.35)), max(3, radius // 3))
        pygame.draw.circle(surface, GOLD_2, (int(x), int(y)), radius, 2)
        if ball["finished"]:
            draw_text(surface, f"{ball['multiplier']:g}x", self.app.fonts["tiny"], WHITE, (int(x), int(y - 25)), "center")

    def draw_balls(self, surface):
        if not self.balls:
            geo = self.board_geometry()
            idle_ball = {
                "pos": (geo["center_x"], geo["top_y"] - 44),
                "radius": 14,
                "color": (229, 48, 70),
                "finished": False,
                "multiplier": 0,
            }
            self.draw_ball(surface, idle_ball)
            return
        for ball in sorted(self.balls, key=lambda item: item["pos"][1]):
            if ball["state"] in ("waiting", "dropping", "finished"):
                self.draw_ball(surface, ball)

    def draw_side_panel(self, surface):
        side = pygame.Rect(850, 152, 330, 414)
        rounded_rect(surface, side, PANEL, 18, 1, (76, 90, 118))
        draw_text(surface, "RISCO", self.app.fonts["tiny"], MUTED, (878, 184))
        draw_text(surface, self.risk_profiles[self.risk]["label"], self.app.fonts["small"], WHITE, (878, 262))
        draw_text(surface, "COLUNAS", self.app.fonts["tiny"], MUTED, (878, 292))
        draw_text(surface, f"{self.rows + 1} buckets", self.app.fonts["small"], WHITE, (878, 362))
        draw_text(surface, "LANÇAMENTO", self.app.fonts["tiny"], MUTED, (878, 392))
        launch_rect = pygame.Rect(878, 414, 270, 38)
        draw_wrapped_text(surface, "Cada clique solta uma bola independente.", self.app.fonts["small"], WHITE, launch_rect, 4, 2)
        draw_text(surface, "RODADA ATUAL", self.app.fonts["tiny"], MUTED, (878, 466))
        launched = self.launched_balls if self.balls else 0
        active = self.active_ball_count()
        draw_text(surface, f"Lançadas: {launched}", self.app.fonts["small"], WHITE, (878, 492))
        draw_text(surface, f"Em queda: {active}", self.app.fonts["small"], MUTED, (878, 516))
        multipliers = self.current_multipliers()
        best = max(multipliers)
        center = multipliers[len(multipliers) // 2]
        draw_text(surface, f"Payout: {br_money(self.round_payout)}", self.app.fonts["small"], GOLD_2, (878, 540))
        draw_text(surface, f"Custo: {br_money(self.round_cost)}", self.app.fonts["small"], MUTED, (1030, 540))
        draw_text(surface, f"Borda {best:g}x | Centro {center:g}x", self.app.fonts["tiny"], GOLD_2, (878, 562))

    def draw(self, surface):
        self.draw_panel_title(surface, "Plinko", "Solte a bola, acompanhe os quiques e ganhe pelo bucket final.")
        board_rect = pygame.Rect(70, 166, 748, 424)
        self.draw_pin_board(surface, board_rect)
        self.draw_buckets(surface)
        self.draw_balls(surface)
        self.draw_side_panel(surface)
        msg_rect = pygame.Rect(292, 604, 510, 74)
        rounded_rect(surface, msg_rect, PANEL_2, 12, 1, (82, 96, 126))
        draw_centered_wrapped(surface, self.message, self.app.fonts["small"], WHITE, msg_rect)
        self.draw_bet_box(surface, 850, 604)


class CoinFlipScene(CasinoGameScene):
    def __init__(self, app):
        super().__init__(app)
        self.choice = "heads"
        self.result = None
        self.flipping = 0.0
        self.flip_elapsed = 0.0
        self.flip_duration = 1.55
        self.coin_spin = 0.0
        self.coin_tilt = 0.0
        self.message = "Escolha cara ou coroa e lance a moeda."

    def can_change_bet(self):
        return self.flipping <= 0

    def build_ui(self):
        self.buttons = [Button(pygame.Rect(24, 22, 112, 42), "Menu", lambda: self.app.set_scene("menu"), "secondary")]
        self.add_bet_buttons(850, 604)
        options = [("heads", "Cara", 420), ("tails", "Coroa", 620)]
        for key, label, x in options:
            kind = "primary" if self.choice == key else "secondary"
            self.buttons.append(Button(pygame.Rect(x, 508, 168, 50), label, lambda k=key: self.select(k), kind, self.flipping <= 0))
        self.buttons.append(Button(pygame.Rect(64, 604, 180, 52), "Lançar", self.flip, "success", self.flipping <= 0 and self.app.balance >= self.bet))

    def select(self, choice):
        if self.flipping <= 0:
            self.choice = choice
            self.message = f"Escolha marcada: {'cara' if choice == 'heads' else 'coroa'}."

    def flip(self):
        if self.flipping > 0 or self.app.balance < self.bet:
            return
        self.app.balance -= self.bet
        self.result = random.choice(["heads", "tails"])
        self.flip_elapsed = 0.0
        self.flipping = self.flip_duration
        self.coin_spin = 0.0
        self.message = "Moeda girando..."

    def update(self, dt):
        if self.flipping > 0:
            self.flip_elapsed += dt
            self.flipping -= dt
            progress = clamp(self.flip_elapsed / self.flip_duration, 0, 1)
            ease = 1 - (1 - progress) ** 3
            self.coin_spin = ease * math.tau * 8
            self.coin_tilt = math.sin(progress * math.pi * 2.5) * (1 - progress)
            if self.flipping <= 0:
                win = self.result == self.choice
                if win:
                    payout = int(self.bet * 1.95)
                    self.app.balance += payout
                    self.message = f"Deu {'cara' if self.result == 'heads' else 'coroa'}! Pagamento: {br_money(payout)} fichas."
                else:
                    self.message = f"Deu {'cara' if self.result == 'heads' else 'coroa'}. Aposta perdida."

    def draw_coin(self, surface, center):
        progress = clamp(self.flip_elapsed / self.flip_duration, 0, 1) if self.flip_duration else 1
        lift = math.sin(progress * math.pi) * 92 if self.flipping > 0 else 0
        tilt_shift = int(self.coin_tilt * 18) if self.flipping > 0 else 0
        width = max(18, int(146 * abs(math.cos(self.coin_spin))))
        coin_rect = pygame.Rect(0, 0, width, 146)
        coin_rect.center = (center[0] + tilt_shift, int(center[1] - lift))
        pygame.draw.ellipse(surface, (0, 0, 0, 85), pygame.Rect(center[0] - 118, center[1] + 90, 236, 34))
        edge_rect = coin_rect.inflate(10, 8)
        pygame.draw.ellipse(surface, (134, 82, 28), edge_rect)
        pygame.draw.ellipse(surface, GOLD_2, coin_rect)
        pygame.draw.ellipse(surface, (116, 70, 24), coin_rect, 5)
        pygame.draw.ellipse(surface, (255, 240, 154), coin_rect.inflate(-20, -20), 3)
        pygame.draw.ellipse(surface, (173, 107, 35), coin_rect.inflate(-42, -42), 2)
        for angle in range(0, 360, 30):
            rad = math.radians(angle)
            x1 = coin_rect.centerx + int(math.cos(rad) * width * 0.42)
            y1 = coin_rect.centery + int(math.sin(rad) * 61)
            x2 = coin_rect.centerx + int(math.cos(rad) * width * 0.48)
            y2 = coin_rect.centery + int(math.sin(rad) * 70)
            pygame.draw.line(surface, (118, 72, 24), (x1, y1), (x2, y2), 2)
        face = self.result if self.flipping <= 0 and self.result else ("heads" if math.cos(self.coin_spin) >= 0 else "tails")
        label = "Cara" if face == "heads" else "Coroa"
        if width > 48:
            draw_text(surface, label, self.app.fonts["h2"], (83, 49, 18), coin_rect.center, "center")
            draw_text(surface, "CASINO 67", self.app.fonts["tiny"], (116, 70, 24), (coin_rect.centerx, coin_rect.centery + 38), "center")

    def draw(self, surface):
        self.draw_panel_title(surface, "Cara ou Coroa", "Escolha um lado da moeda animada e tente quase dobrar a aposta.")
        stage = pygame.Rect(80, 166, 1120, 416)
        rounded_rect(surface, stage, (13, 27, 43), 24, 2, (75, 90, 116))
        rounded_rect(surface, stage.inflate(-34, -34), (10, 81, 70), 22, 2, (36, 143, 112))
        self.draw_coin(surface, (640, 320))
        draw_text(surface, "CARA", self.app.fonts["h3"], GOLD_2 if self.choice == "heads" else MUTED, (504, 452), "center")
        draw_text(surface, "COROA", self.app.fonts["h3"], GOLD_2 if self.choice == "tails" else MUTED, (704, 452), "center")
        msg_rect = pygame.Rect(292, 604, 510, 74)
        rounded_rect(surface, msg_rect, PANEL_2, 12, 1, (82, 96, 126))
        draw_centered_wrapped(surface, self.message, self.app.fonts["small"], WHITE, msg_rect)
        self.draw_bet_box(surface, 850, 604)


class CrashScene(CasinoGameScene):
    def __init__(self, app):
        super().__init__(app)
        self.state = "idle"
        self.multiplier = 1.0
        self.crash_point = 2.0
        self.elapsed = 0.0
        self.stake = 0
        self.history = []
        self.message = "Comece a rodada e saque antes do crash."

    def can_change_bet(self):
        return self.state != "running"

    def build_ui(self):
        self.buttons = [Button(pygame.Rect(24, 22, 112, 42), "Menu", lambda: self.app.set_scene("menu"), "secondary")]
        self.add_bet_buttons(850, 604)
        self.buttons.append(Button(pygame.Rect(64, 604, 180, 52), "Começar", self.start_round, "success", self.state != "running" and self.app.balance >= self.bet))
        self.buttons.append(Button(pygame.Rect(256, 604, 180, 52), "Sacar", self.cashout, "primary", self.state == "running"))

    def start_round(self):
        if self.state == "running" or self.app.balance < self.bet:
            return
        self.app.balance -= self.bet
        self.stake = self.bet
        self.elapsed = 0.0
        self.multiplier = 1.0
        self.crash_point = max(1.05, round(1 + random.random() ** 2.3 * 12, 2))
        self.history = []
        self.state = "running"
        self.message = "Multiplicador subindo..."

    def cashout(self):
        if self.state != "running":
            return
        payout = int(self.stake * self.multiplier)
        self.app.balance += payout
        self.state = "result"
        self.message = f"Saque em {self.multiplier:.2f}x: {br_money(payout)} fichas."

    def update(self, dt):
        if self.state != "running":
            return
        self.elapsed += dt
        self.multiplier = 1 + self.elapsed * 0.65 + (self.elapsed ** 2) * 0.42
        self.history.append(self.multiplier)
        self.history = self.history[-90:]
        if self.multiplier >= self.crash_point:
            self.multiplier = self.crash_point
            self.state = "result"
            self.message = f"Crash em {self.crash_point:.2f}x. Aposta perdida."

    def draw_graph(self, surface, rect):
        rounded_rect(surface, rect, (9, 16, 28), 20, 2, (75, 90, 116))
        for i in range(6):
            y = rect.bottom - 34 - i * 48
            pygame.draw.line(surface, (38, 49, 70), (rect.x + 28, y), (rect.right - 28, y), 1)
        points = []
        values = self.history if self.history else [self.multiplier]
        max_val = max(3.0, max(values) + 0.5)
        for i, value in enumerate(values):
            t = i / max(1, len(values) - 1)
            x = rect.x + 44 + t * (rect.w - 88)
            y = rect.bottom - 42 - ((value - 1) / (max_val - 1)) * (rect.h - 84)
            points.append((x, y))
        if len(points) > 1:
            pygame.draw.lines(surface, GREEN if self.state == "running" else RED, False, points, 6)
            pygame.draw.circle(surface, GOLD_2, (int(points[-1][0]), int(points[-1][1])), 9)
        draw_text(surface, f"{self.multiplier:.2f}x", self.app.fonts["mega"], GOLD_2 if self.state == "running" else RED, rect.center, "center")

    def draw(self, surface):
        self.draw_panel_title(surface, "Crash 67", "Segure a coragem, mas saque antes do multiplicador explodir.")
        self.draw_graph(surface, pygame.Rect(90, 166, 720, 416))
        panel = pygame.Rect(850, 166, 330, 416)
        rounded_rect(surface, panel, PANEL, 18, 1, (76, 90, 118))
        draw_text(surface, "RODADA", self.app.fonts["tiny"], MUTED, (878, 198))
        draw_text(surface, "Rodando" if self.state == "running" else "Pronto", self.app.fonts["h3"], WHITE, (878, 228))
        draw_text(surface, "MULTIPLICADOR", self.app.fonts["tiny"], MUTED, (878, 286))
        draw_text(surface, f"{self.multiplier:.2f}x", self.app.fonts["h2"], GOLD_2, (878, 318))
        draw_text(surface, "SAQUE AGORA", self.app.fonts["tiny"], MUTED, (878, 386))
        draw_text(surface, f"{br_money(int(self.stake * self.multiplier))} fichas", self.app.fonts["h3"], GREEN, (878, 418))
        msg_rect = pygame.Rect(292, 604, 510, 74)
        rounded_rect(surface, msg_rect, PANEL_2, 12, 1, (82, 96, 126))
        draw_centered_wrapped(surface, self.message, self.app.fonts["small"], WHITE, msg_rect)
        self.draw_bet_box(surface, 850, 604)


class MinesScene(CasinoGameScene):
    def __init__(self, app):
        super().__init__(app)
        self.mine_count = 5
        self.active = False
        self.revealed = set()
        self.mines = set()
        self.multiplier = 1.0
        self.stake = 0
        self.message = "Escolha a aposta, defina as minas e comece."
        self.grid_rects = []
        self.round_over = False
        self.flip_anims = {}

    def can_change_bet(self):
        return not self.active

    def update(self, dt):
        for index in list(self.flip_anims):
            self.flip_anims[index] -= dt
            if self.flip_anims[index] <= 0:
                del self.flip_anims[index]

    def build_ui(self):
        self.buttons = [Button(pygame.Rect(24, 22, 112, 42), "Menu", lambda: self.app.set_scene("menu"), "secondary")]
        self.add_bet_buttons(850, 604)
        self.buttons.extend(
            [
                Button(pygame.Rect(64, 604, 166, 52), "Começar", self.start_round, "success", not self.active and self.app.balance >= self.bet),
                Button(pygame.Rect(244, 604, 166, 52), "Sacar", self.cashout, "primary", self.active and len(self.revealed) > 0),
                Button(pygame.Rect(872, 518, 44, 42), "-", lambda: self.change_mines(-1), "secondary", not self.active),
                Button(pygame.Rect(924, 518, 44, 42), "+", lambda: self.change_mines(1), "secondary", not self.active),
            ]
        )

    def change_mines(self, amount):
        if self.active:
            return
        self.mine_count = clamp(self.mine_count + amount, 1, 20)

    def start_round(self):
        if self.active or self.app.balance < self.bet:
            return
        self.app.balance -= self.bet
        self.stake = self.bet
        cells = list(range(25))
        random.shuffle(cells)
        self.mines = set(cells[: self.mine_count])
        self.revealed = set()
        self.multiplier = 1.0
        self.active = True
        self.round_over = False
        self.flip_anims = {}
        self.message = "Abra casas seguras. Quanto mais abrir, maior o multiplicador."

    def cashout(self):
        if not self.active or len(self.revealed) == 0:
            return
        payout = int(self.stake * self.multiplier)
        self.app.balance += payout
        self.active = False
        self.round_over = True
        self.message = f"Saque realizado em {self.multiplier:.2f}x: {br_money(payout)} fichas."

    def reveal(self, index):
        if not self.active or index in self.revealed:
            return
        if index in self.mines:
            self.flip_anims[index] = 0.34
            self.active = False
            self.round_over = True
            self.message = "Explodiu. A aposta ficou na mesa."
            return
        safe_before = len(self.revealed)
        total_left = 25 - safe_before
        safe_left = 25 - self.mine_count - safe_before
        probability = safe_left / total_left
        self.multiplier *= 0.96 / probability
        self.revealed.add(index)
        self.flip_anims[index] = 0.34
        if len(self.revealed) == 25 - self.mine_count:
            payout = int(self.stake * self.multiplier)
            self.app.balance += payout
            self.active = False
            self.round_over = True
            self.message = f"Mesa limpa! Pagamento máximo: {br_money(payout)} fichas."
        else:
            self.message = f"Seguro. Multiplicador atual: {self.multiplier:.2f}x."

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            for rect, index in self.grid_rects:
                if rect.collidepoint(event.pos):
                    self.reveal(index)
                    return True
        return super().handle_event(event)

    def draw_grid(self, surface):
        self.grid_rects = []
        size, gap = 78, 10
        x0, y0 = 342, 174
        for row in range(5):
            for col in range(5):
                index = row * 5 + col
                rect = pygame.Rect(x0 + col * (size + gap), y0 + row * (size + gap), size, size)
                self.grid_rects.append((rect, index))
                revealed = index in self.revealed
                mine_visible = self.round_over and index in self.mines
                anim_timer = self.flip_anims.get(index, 0)
                if anim_timer > 0:
                    progress = 1 - clamp(anim_timer / 0.34, 0, 1)
                    scale = max(0.08, abs(math.cos(progress * math.pi)))
                    display_rect = pygame.Rect(0, rect.y, max(6, int(rect.w * scale)), rect.h)
                    display_rect.center = rect.center
                    showing_front = progress >= 0.5
                else:
                    display_rect = rect
                    showing_front = True
                show_mine = mine_visible and showing_front
                show_safe = revealed and showing_front
                if show_mine:
                    color = RED
                elif show_safe:
                    color = (34, 118, 194)
                else:
                    color = (26, 54, 92) if self.active else (22, 37, 65)
                rounded_rect(surface, display_rect, color, 14, 2, (118, 207, 255) if show_safe else (68, 92, 132))
                if display_rect.w > 28:
                    if show_mine:
                        pygame.draw.circle(surface, (93, 18, 28), display_rect.center, 22)
                        pygame.draw.circle(surface, WHITE, (display_rect.centerx - 8, display_rect.centery - 8), 4)
                    elif show_safe:
                        draw_diamond(surface, display_rect.center, 24, (109, 203, 255), WHITE, 2)
                        draw_diamond(surface, display_rect.center, 12, (31, 124, 219))
                    else:
                        draw_text(surface, "?", self.app.fonts["h2"], MUTED, display_rect.center, "center")

    def draw(self, surface):
        self.draw_panel_title(surface, "Mines", "Abra casas seguras, aumente o risco e saque antes da bomba.")
        board = pygame.Rect(310, 160, 510, 444)
        rounded_rect(surface, board, (13, 24, 42), 24, 2, (57, 102, 153))
        self.draw_grid(surface)
        side = pygame.Rect(850, 156, 330, 402)
        rounded_rect(surface, side, (18, 31, 54), 18, 1, (57, 102, 153))
        draw_text(surface, "RISCO", self.app.fonts["tiny"], MUTED, (878, 184))
        draw_text(surface, f"{self.mine_count} minas", self.app.fonts["h2"], WHITE, (878, 212))
        draw_text(surface, "MULTIPLICADOR", self.app.fonts["tiny"], MUTED, (878, 294))
        draw_text(surface, f"{self.multiplier:.2f}x", self.app.fonts["h1"], GOLD_2, (878, 326))
        draw_text(surface, "CASAS SEGURAS", self.app.fonts["tiny"], MUTED, (878, 418))
        draw_text(surface, f"{len(self.revealed)} / {25 - self.mine_count}", self.app.fonts["h2"], WHITE, (878, 446))
        msg_rect = pygame.Rect(442, 604, 380, 74)
        rounded_rect(surface, msg_rect, PANEL_2, 12, 1, (82, 96, 126))
        draw_centered_wrapped(surface, self.message, self.app.fonts["small"], WHITE, msg_rect)
        self.draw_bet_box(surface, 850, 604)


class RankingScene(Scene):
    def __init__(self, app):
        super().__init__(app)
        self.rankings = []
        self.name_text = ""
        self.input_active = True
        self.message = "Digite seu nome e salve sua pontuação."
        self.input_rect = pygame.Rect(106, 246, 430, 54)

    def on_enter(self):
        self.message = "Digite seu nome e salve sua pontuação."
        self.rankings = self.load_rankings()
        self.input_active = True

    def build_ui(self):
        self.buttons = [
            Button(pygame.Rect(24, 22, 112, 42), "Voltar", lambda: self.app.set_scene("menu"), "secondary"),
            Button(pygame.Rect(106, 322, 210, 52), "Salvar ranking", self.save_current_ranking, "primary"),
            Button(pygame.Rect(334, 322, 142, 52), "Limpar", self.clear_name, "ghost"),
        ]

    def rankings_path(self):
        return self.app.base_dir / "rankings.json"

    def load_rankings(self):
        path = self.rankings_path()
        if not path.exists():
            try:
                path.write_text("[]", encoding="utf-8")
            except OSError:
                self.message = "Não foi possível criar rankings.json."
                return []
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            self.message = "Ranking vazio ou corrompido. Um novo ranking será usado."
            return []
        if not isinstance(data, list):
            return []
        cleaned = []
        for item in data:
            if not isinstance(item, dict):
                continue
            name = str(item.get("name", "Apostador")).strip()[:24] or "Apostador"
            try:
                chips = int(item.get("chips", 0))
            except (TypeError, ValueError):
                chips = 0
            cleaned.append({"name": name, "chips": max(0, chips)})
        return sorted(cleaned, key=lambda item: item["chips"], reverse=True)

    def write_rankings(self):
        path = self.rankings_path()
        try:
            path.write_text(json.dumps(self.rankings, ensure_ascii=False, indent=2), encoding="utf-8")
            return True
        except OSError:
            self.message = "Não foi possível salvar o ranking."
            return False

    def save_current_ranking(self):
        name = self.name_text.strip()[:24] or "Apostador"
        self.rankings.append({"name": name, "chips": int(self.app.balance)})
        self.rankings = sorted(self.rankings, key=lambda item: item["chips"], reverse=True)
        if self.write_rankings():
            self.name_text = ""
            self.message = f"Ranking salvo: {name} com {br_money(self.app.balance)} fichas."

    def clear_name(self):
        self.name_text = ""
        self.input_active = True

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.input_active = self.input_rect.collidepoint(event.pos)
        if super().handle_event(event):
            return True
        if event.type == pygame.TEXTINPUT and self.input_active:
            if len(self.name_text) < 24 and event.text.isprintable():
                self.name_text += event.text
            return True
        if event.type == pygame.KEYDOWN and self.input_active:
            if event.key == pygame.K_BACKSPACE:
                self.name_text = self.name_text[:-1]
                return True
            if event.key == pygame.K_RETURN:
                self.save_current_ranking()
                return True
        return False

    def draw_ranking_rows(self, surface, rect):
        rounded_rect(surface, rect, PANEL, 18, 1, (76, 90, 118))
        draw_text(surface, "TOP 10", self.app.fonts["tiny"], MUTED, (rect.x + 24, rect.y + 20))
        if not self.rankings:
            draw_centered_wrapped(surface, "Nenhum ranking salvo ainda.", self.app.fonts["body"], MUTED, rect.inflate(-40, -80))
            return
        for i, item in enumerate(self.rankings[:10]):
            y = rect.y + 58 + i * 42
            row = pygame.Rect(rect.x + 18, y, rect.w - 36, 34)
            color = (31, 39, 60) if i % 2 == 0 else (26, 33, 52)
            rounded_rect(surface, row, color, 8, 1, (58, 70, 96))
            rank_color = GOLD_2 if i < 3 else MUTED
            draw_text(surface, f"{i + 1}.", self.app.fonts["small"], rank_color, (row.x + 14, row.y + 8))
            draw_text(surface, item["name"], self.app.fonts["small"], WHITE, (row.x + 58, row.y + 8))
            draw_text(surface, f"{br_money(item['chips'])} fichas", self.app.fonts["small"], GOLD_2, (row.right - 16, row.y + 8), "topright")

    def draw(self, surface):
        self.draw_panel_title(surface, "Rankings", "Salve seu saldo atual e compare os melhores apostadores.")
        form = pygame.Rect(78, 166, 502, 414)
        rounded_rect(surface, form, PANEL, 18, 1, (76, 90, 118))
        draw_text(surface, "APOSTADOR", self.app.fonts["tiny"], MUTED, (106, 206))
        border = GOLD_2 if self.input_active else (82, 96, 126)
        rounded_rect(surface, self.input_rect, (16, 23, 38), 12, 2, border)
        shown = self.name_text if self.name_text else "Digite seu nome"
        color = WHITE if self.name_text else (110, 122, 138)
        draw_text(surface, shown, self.app.fonts["body"], color, (self.input_rect.x + 18, self.input_rect.y + 16))
        if self.input_active and int(pygame.time.get_ticks() / 420) % 2 == 0:
            caret_x = self.input_rect.x + 18 + self.app.fonts["body"].size(self.name_text)[0] + 3
            pygame.draw.line(surface, GOLD_2, (caret_x, self.input_rect.y + 14), (caret_x, self.input_rect.bottom - 14), 2)
        draw_text(surface, "FICHAS ATUAIS", self.app.fonts["tiny"], MUTED, (106, 414))
        draw_text(surface, f"{br_money(self.app.balance)} fichas", self.app.fonts["h2"], GOLD_2, (106, 444))
        draw_wrapped_text(surface, self.message, self.app.fonts["small"], MUTED, pygame.Rect(106, 504, 410, 42), 4, 2)
        self.draw_ranking_rows(surface, pygame.Rect(618, 166, 584, 414))


class CasinoApp:
    def __init__(self):
        pygame.init()
        self.base_dir = Path(__file__).resolve().parent
        self.audio_enabled = False
        try:
            pygame.mixer.init()
            self.audio_enabled = True
        except pygame.error:
            self.audio_enabled = False
        pygame.display.set_caption("Casino 67")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.fonts = self.load_fonts()
        self.images, self.sounds = self.load_assets()
        self.balance = 10000
        self.running = True
        self.scenes = {
            "agegate": AgeGateScene(self),
            "menu": MenuScene(self),
            "rankings": RankingScene(self),
            "blackjack": BlackjackScene(self),
            "dice": DiceScene(self),
            "roulette": RouletteScene(self),
            "slots": SlotsScene(self),
            "plinko": PlinkoScene(self),
            "mines": MinesScene(self),
            "coinflip": CoinFlipScene(self),
            "crash": CrashScene(self),
        }
        self.scene_name = "agegate"
        self.scene = self.scenes[self.scene_name]
        self.bg_stars = [(random.randrange(WIDTH), random.randrange(HEIGHT), random.randrange(1, 3)) for _ in range(80)]

    def load_fonts(self):
        families = "segoe ui,arial,verdana"
        return {
            "mega": pygame.font.SysFont(families, 72, bold=True),
            "h1": pygame.font.SysFont(families, 46, bold=True),
            "h2": pygame.font.SysFont(families, 34, bold=True),
            "h3": pygame.font.SysFont(families, 26, bold=True),
            "body": pygame.font.SysFont(families, 22),
            "button": pygame.font.SysFont(families, 18, bold=True),
            "small": pygame.font.SysFont(families, 17),
            "tiny": pygame.font.SysFont(families, 13, bold=True),
            "card": pygame.font.SysFont(families, 24, bold=True),
            "icon": pygame.font.SysFont(families, 36, bold=True),
        }

    def load_assets(self):
        images = {}
        sounds = {}
        image_base = self.base_dir / "assets" / "menu" / "blackjack_hover"
        for ext in (".png", ".jpg", ".jpeg", ".webp"):
            path = image_base.with_suffix(ext)
            if path.exists():
                try:
                    images["blackjack_hover"] = pygame.image.load(str(path)).convert_alpha()
                    break
                except pygame.error:
                    pass
        if self.audio_enabled:
            sound_base = self.base_dir / "assets" / "sounds" / "blackjack_hover"
            for ext in (".wav", ".ogg", ".mp3"):
                path = sound_base.with_suffix(ext)
                if path.exists():
                    try:
                        sounds["blackjack_hover"] = pygame.mixer.Sound(str(path))
                        sounds["blackjack_hover"].set_volume(0.45)
                        break
                    except pygame.error:
                        pass
        return images, sounds

    def play_sound(self, name):
        sound = self.sounds.get(name)
        if sound:
            sound.play()

    def set_scene(self, name):
        self.scene_name = name
        self.scene = self.scenes[name]
        self.scene.on_enter()

    def quit_game(self):
        self.running = False

    def refill_balance(self):
        self.balance = 10000

    def draw_background(self):
        for y in range(HEIGHT):
            t = y / HEIGHT
            color = (
                int(BG_TOP[0] * (1 - t) + BG_BOTTOM[0] * t),
                int(BG_TOP[1] * (1 - t) + BG_BOTTOM[1] * t),
                int(BG_TOP[2] * (1 - t) + BG_BOTTOM[2] * t),
            )
            pygame.draw.line(self.screen, color, (0, y), (WIDTH, y))
        for x, y, r in self.bg_stars:
            pygame.draw.circle(self.screen, (255, 236, 176, 40), (x, y), r)
        pygame.draw.circle(self.screen, (45, 87, 76), (1080, 650), 260, 2)
        pygame.draw.circle(self.screen, (91, 66, 33), (122, 90), 170, 2)

    def draw_top_bar(self):
        rect = pygame.Rect(0, 0, WIDTH, 86)
        rounded_rect(self.screen, rect, (11, 15, 27), 0)
        pygame.draw.line(self.screen, (59, 70, 91), (0, 86), (WIDTH, 86), 1)
        draw_text(self.screen, "Casino 67", self.fonts["h3"], GOLD_2, (158, 25))
        draw_text(self.screen, "André B  |  Christian S  |  Rony F", self.fonts["small"], MUTED, (158, 55))
        draw_chip(self.screen, (82, 43), 31, "67", self.fonts["body"])
        balance_rect = pygame.Rect(962, 18, 254, 50)
        rounded_rect(self.screen, balance_rect, (24, 34, 51), 12, 1, (88, 103, 130))
        draw_text(self.screen, "SALDO", self.fonts["tiny"], MUTED, (982, 26))
        draw_text(self.screen, f"{br_money(self.balance)} fichas", self.fonts["h3"], GOLD_2, (982, 41))

    def handle_global(self, event):
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_ESCAPE:
                if self.scene_name in ("agegate", "menu"):
                    self.running = False
                else:
                    self.set_scene("menu")

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self.scene.build_ui()
            for event in pygame.event.get():
                self.handle_global(event)
                if not self.running:
                    break
                self.scene.handle_event(event)
                if not self.running:
                    break
            if not self.running:
                break
            self.scene.update(dt)
            self.scene.build_ui()
            self.draw_background()
            self.draw_top_bar()
            self.scene.draw(self.screen)
            mouse = pygame.mouse.get_pos()
            for button in self.scene.buttons:
                button.draw(self.screen, self.fonts, mouse)
            self.draw_footer()
            pygame.display.flip()
        pygame.quit()

    def draw_footer(self):
        draw_text(self.screen, "ESC volta ao menu / fecha no salão principal", self.fonts["tiny"], (115, 128, 143), (24, HEIGHT - 24))
        draw_text(self.screen, "Casino fictício para estudo e entretenimento", self.fonts["tiny"], (115, 128, 143), (WIDTH - 24, HEIGHT - 24), "topright")


def main():
    CasinoApp().run()


if __name__ == "__main__":
    main()
