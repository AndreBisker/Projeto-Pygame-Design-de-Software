import math
import random
from dataclasses import dataclass

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
    total_h = len(lines) * font.get_height() + max(0, len(lines) - 1) * line_gap
    y = rect.centery - total_h // 2
    for line in lines:
        rendered = font.render(line, True, color)
        r = rendered.get_rect(centerx=rect.centerx, top=y)
        surface.blit(rendered, r)
        y += font.get_height() + line_gap


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
        draw_text(surface, title, self.app.fonts["h2"], WHITE, (64, 118))
        if subtitle:
            draw_text(surface, subtitle, self.app.fonts["small"], MUTED, (66, 158))


class CasinoGameScene(Scene):
    min_bet = 25
    max_bet = 1000

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
                Button(pygame.Rect(x + 180, y + 15, 44, 44), "-", lambda: self.change_bet(-25), "secondary", enabled),
                Button(pygame.Rect(x + 232, y + 15, 44, 44), "+", lambda: self.change_bet(25), "secondary", enabled),
                Button(pygame.Rect(x + 284, y + 15, 72, 44), "MAX", self.maximize_bet, "ghost", enabled),
            ]
        )

    def maximize_bet(self):
        if not self.can_change_bet():
            return
        self.bet = min(self.max_bet, max(self.min_bet, self.app.balance))


class MenuScene(Scene):
    def __init__(self, app):
        super().__init__(app)
        self.card_rects = []

    def build_ui(self):
        self.buttons = []
        games = [
            ("blackjack", "Blackjack", "21 com dealer, dobrar e seguro de empate", "♠"),
            ("dice", "Dice", "Baixo, sete exato ou alto em dois dados", "◆"),
            ("roulette", "Roleta", "Números, cores, paridade e dúzias clássicas", "0"),
            ("slots", "Slots", "5 rolos, 3 linhas e pagamentos por sequência", "67"),
            ("mines", "Mines", "Risco progressivo, multiplicador e saque", "*"),
        ]
        self.card_rects = []
        start_x, start_y = 72, 342
        card_w, card_h, gap = 220, 266, 24
        for i, (scene, title, desc, icon) in enumerate(games):
            rect = pygame.Rect(start_x + i * (card_w + gap), start_y, card_w, card_h)
            self.card_rects.append((rect, scene, title, desc, icon))
            self.buttons.append(Button(pygame.Rect(rect.x + 24, rect.bottom - 62, rect.w - 48, 44), "Jogar", lambda s=scene: self.app.set_scene(s), "primary"))
        self.buttons.append(Button(pygame.Rect(1030, 214, 170, 46), "Recarregar", self.app.refill_balance, "secondary"))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            for rect, scene, *_ in self.card_rects:
                if rect.collidepoint(event.pos):
                    self.app.set_scene(scene)
                    return True
        return super().handle_event(event)

    def draw(self, surface):
        fonts = self.app.fonts
        draw_text(surface, "Casino 67", fonts["mega"], GOLD_2, (72, 122))
        draw_text(surface, "Aura + Ego", fonts["h1"], WHITE, (75, 205))
        draw_text(surface, "feito por: André B, Christian S, Rony F", fonts["body"], MUTED, (78, 258))
        draw_chip(surface, (1080, 150), 78, "67", fonts["h1"])
        draw_text(surface, "Salão principal", fonts["h2"], WHITE, (72, 294))
        mouse = pygame.mouse.get_pos()
        for rect, scene, title, desc, icon in self.card_rects:
            hovered = rect.collidepoint(mouse)
            color = (34, 43, 64) if hovered else PANEL
            border = GOLD if hovered else (71, 84, 112)
            rounded_rect(surface, rect, color, 16, 2, border)
            icon_rect = pygame.Rect(rect.x + 24, rect.y + 24, 72, 72)
            pygame.draw.rect(surface, (12, 17, 29), icon_rect, border_radius=16)
            pygame.draw.rect(surface, GOLD, icon_rect, 2, border_radius=16)
            draw_text(surface, icon, fonts["icon"], GOLD_2, icon_rect.center, "center")
            draw_text(surface, title, fonts["h3"], WHITE, (rect.x + 24, rect.y + 118))
            desc_rect = pygame.Rect(rect.x + 24, rect.y + 156, rect.w - 48, 42)
            draw_centered_wrapped(surface, desc, fonts["small"], MUTED, desc_rect)


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

    def on_enter(self):
        self.message = "Ajuste a aposta e distribua as cartas."
        if self.app.balance < self.bet:
            self.bet = max(self.min_bet, min(self.bet, self.app.balance))

    def can_change_bet(self):
        return self.phase in ("ready", "result")

    def build_ui(self):
        self.buttons = [Button(pygame.Rect(24, 22, 112, 42), "Menu", lambda: self.app.set_scene("menu"), "secondary")]
        self.add_bet_buttons(850, 604)
        if self.phase in ("ready", "result"):
            self.buttons.append(Button(pygame.Rect(64, 604, 180, 52), "Dar cartas", self.start_hand, "primary", self.app.balance >= self.bet))
        if self.phase == "player":
            self.buttons.extend(
                [
                    Button(pygame.Rect(64, 604, 126, 52), "Carta", self.hit, "blue"),
                    Button(pygame.Rect(204, 604, 126, 52), "Parar", self.stand, "success"),
                    Button(
                        pygame.Rect(344, 604, 126, 52),
                        "Dobrar",
                        self.double_down,
                        "primary",
                        len(self.player) == 2 and self.app.balance >= self.stake,
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

    def start_hand(self):
        if self.app.balance < self.bet:
            self.message = "Saldo insuficiente para esta aposta."
            return
        self.app.balance -= self.bet
        self.stake = self.bet
        self.make_deck()
        self.player = [self.draw_card_from_deck(), self.draw_card_from_deck()]
        self.dealer = [self.draw_card_from_deck(), self.draw_card_from_deck()]
        self.phase = "player"
        self.message = "Sua vez: peça carta, pare ou dobre."
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
        self.player.append(self.draw_card_from_deck())
        value = self.hand_value(self.player)
        if value > 21:
            self.phase = "result"
            self.message = f"Estourou com {value}. A banca fica com a aposta."
        elif value == 21:
            self.stand()
        else:
            self.message = f"Sua mão vale {value}. Continue ou pare."

    def stand(self):
        if self.phase != "player":
            return
        while self.hand_value(self.dealer) < 17:
            self.dealer.append(self.draw_card_from_deck())
        player_value = self.hand_value(self.player)
        dealer_value = self.hand_value(self.dealer)
        self.phase = "result"
        if dealer_value > 21 or player_value > dealer_value:
            payout = self.stake * 2
            self.app.balance += payout
            self.message = f"Você venceu {player_value} x {dealer_value}. Pagamento: {br_money(payout)}."
        elif player_value == dealer_value:
            self.app.balance += self.stake
            self.message = f"Empate em {player_value}. Aposta devolvida."
        else:
            self.message = f"Dealer venceu {dealer_value} x {player_value}."

    def double_down(self):
        if self.phase != "player" or len(self.player) != 2 or self.app.balance < self.stake:
            return
        self.app.balance -= self.stake
        self.stake *= 2
        self.player.append(self.draw_card_from_deck())
        if self.hand_value(self.player) > 21:
            self.phase = "result"
            self.message = f"Dobrou e estourou com {self.hand_value(self.player)}."
        else:
            self.stand()

    def draw_card(self, surface, card, x, y, hidden=False):
        rect = pygame.Rect(x, y, 86, 122)
        if hidden:
            rounded_rect(surface, rect, (115, 28, 50), 12, 2, GOLD)
            for i in range(8):
                pygame.draw.line(surface, (154, 44, 72), (x + 12, y + 16 + i * 13), (x + 74, y + 16 + i * 13), 2)
            draw_text(surface, "67", self.app.fonts["h3"], GOLD_2, rect.center, "center")
            return
        rank, suit = card
        color = RED if suit in ("♥", "♦") else INK
        rounded_rect(surface, rect, CARD, 12, 2, (224, 218, 202))
        draw_text(surface, rank, self.app.fonts["card"], color, (x + 12, y + 10))
        draw_text(surface, suit, self.app.fonts["h2"], color, rect.center, "center")
        draw_text(surface, rank, self.app.fonts["card"], color, (x + 74, y + 112), "bottomright")

    def draw_hand(self, surface, title, hand, x, y, hide_first=False):
        draw_text(surface, title, self.app.fonts["body"], MUTED, (x, y - 34))
        for i, card in enumerate(hand):
            self.draw_card(surface, card, x + i * 96, y, hidden=hide_first and i == 0)

    def draw(self, surface):
        self.draw_panel_title(surface, "Blackjack", "Chegue a 21 sem estourar. Blackjack paga 3:2.")
        table = pygame.Rect(50, 178, 1180, 390)
        rounded_rect(surface, table, (12, 92, 67), 24, 4, (31, 135, 100))
        pygame.draw.ellipse(surface, (16, 117, 82), pygame.Rect(96, 210, 1088, 306), 8)
        dealer_hidden = self.phase == "player"
        self.draw_hand(surface, "Dealer", self.dealer, 154, 238, dealer_hidden)
        self.draw_hand(surface, "Você", self.player, 154, 412, False)
        player_value = self.hand_value(self.player) if self.player else 0
        dealer_value = self.hand_value(self.dealer) if self.dealer and not dealer_hidden else "?"
        info_rect = pygame.Rect(760, 228, 360, 248)
        rounded_rect(surface, info_rect, (18, 26, 42), 18, 1, (80, 97, 124))
        draw_text(surface, "PLACAR DA MÃO", self.app.fonts["tiny"], MUTED, (info_rect.x + 24, info_rect.y + 22))
        draw_text(surface, f"Você: {player_value}", self.app.fonts["h2"], WHITE, (info_rect.x + 24, info_rect.y + 58))
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
        self.rolling = 1.15
        self.pending_result = [random.randint(1, 6), random.randint(1, 6)]
        self.message = "Os dados estão rolando..."

    def update(self, dt):
        if self.rolling > 0:
            self.rolling -= dt
            self.dice = [random.randint(1, 6), random.randint(1, 6)]
            if self.rolling <= 0:
                self.dice = self.pending_result
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

    def draw_die(self, surface, rect, value):
        rounded_rect(surface, rect, CARD, 18, 3, (216, 210, 198))
        spots = {
            1: [(0.5, 0.5)],
            2: [(0.28, 0.28), (0.72, 0.72)],
            3: [(0.28, 0.28), (0.5, 0.5), (0.72, 0.72)],
            4: [(0.28, 0.28), (0.72, 0.28), (0.28, 0.72), (0.72, 0.72)],
            5: [(0.28, 0.28), (0.72, 0.28), (0.5, 0.5), (0.28, 0.72), (0.72, 0.72)],
            6: [(0.28, 0.24), (0.72, 0.24), (0.28, 0.5), (0.72, 0.5), (0.28, 0.76), (0.72, 0.76)],
        }
        for px, py in spots[value]:
            pygame.draw.circle(surface, INK, (rect.x + int(rect.w * px), rect.y + int(rect.h * py)), 10)

    def draw(self, surface):
        self.draw_panel_title(surface, "Dice", "Dois dados, aposta rápida e pagamentos claros.")
        stage = pygame.Rect(80, 166, 1120, 316)
        rounded_rect(surface, stage, PANEL, 24, 2, (75, 90, 116))
        pygame.draw.arc(surface, GOLD, pygame.Rect(210, 196, 860, 240), 0, math.pi, 4)
        self.draw_die(surface, pygame.Rect(450, 235, 134, 134), self.dice[0])
        self.draw_die(surface, pygame.Rect(690, 235, 134, 134), self.dice[1])
        total = sum(self.dice)
        draw_text(surface, str(total), self.app.fonts["mega"], GOLD_2, (640, 415), "center")
        msg_rect = pygame.Rect(292, 604, 510, 74)
        rounded_rect(surface, msg_rect, PANEL_2, 12, 1, (82, 96, 126))
        draw_centered_wrapped(surface, self.message, self.app.fonts["small"], WHITE, msg_rect)
        self.draw_bet_box(surface, 850, 604)


class RouletteScene(CasinoGameScene):
    red_numbers = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}

    def __init__(self, app):
        super().__init__(app)
        self.selected = ("color", "red")
        self.current = 0
        self.spinning = 0.0
        self.target = 0
        self.message = "Escolha uma aposta e gire a roleta."
        self.number_rects = []

    def can_change_bet(self):
        return self.spinning <= 0

    def build_ui(self):
        self.buttons = [Button(pygame.Rect(24, 22, 112, 42), "Menu", lambda: self.app.set_scene("menu"), "secondary")]
        self.add_bet_buttons(850, 604)
        self.buttons.append(Button(pygame.Rect(64, 604, 180, 52), "Girar", self.spin, "success", self.spinning <= 0 and self.app.balance >= self.bet))
        options = [
            (("color", "red"), "Vermelho", "danger"),
            (("color", "black"), "Preto", "secondary"),
            (("parity", "even"), "Par", "blue"),
            (("parity", "odd"), "Ímpar", "blue"),
            (("range", "low"), "1-18", "ghost"),
            (("range", "high"), "19-36", "ghost"),
            (("dozen", 1), "1a dúzia", "ghost"),
            (("dozen", 2), "2a dúzia", "ghost"),
            (("dozen", 3), "3a dúzia", "ghost"),
        ]
        for i, (selection, label, kind) in enumerate(options):
            row, col = divmod(i, 3)
            x = 820 + col * 132
            y = 194 + row * 54
            selected_kind = "primary" if self.selected == selection else kind
            self.buttons.append(Button(pygame.Rect(x, y, 118, 42), label, lambda s=selection: self.select(s), selected_kind, self.spinning <= 0))

    def select(self, selection):
        if self.spinning <= 0:
            self.selected = selection

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self.spinning <= 0:
            for rect, num in self.number_rects:
                if rect.collidepoint(event.pos):
                    self.selected = ("number", num)
                    return True
        return super().handle_event(event)

    def spin(self):
        if self.spinning > 0 or self.app.balance < self.bet:
            return
        self.app.balance -= self.bet
        self.target = random.randint(0, 36)
        self.spinning = 2.2
        self.message = "A bolinha está girando..."

    def update(self, dt):
        if self.spinning > 0:
            self.spinning -= dt
            self.current = random.randint(0, 36)
            if self.spinning <= 0:
                self.current = self.target
                self.finish_spin()

    def number_color(self, number):
        if number == 0:
            return GREEN
        return RED if number in self.red_numbers else BLACK

    def finish_spin(self):
        num = self.current
        sel_type, sel_value = self.selected
        multiplier = 0
        win = False
        if sel_type == "number":
            win = num == sel_value
            multiplier = 36
        elif sel_type == "color":
            win = num != 0 and ((sel_value == "red" and num in self.red_numbers) or (sel_value == "black" and num not in self.red_numbers))
            multiplier = 2
        elif sel_type == "parity":
            win = num != 0 and ((sel_value == "even" and num % 2 == 0) or (sel_value == "odd" and num % 2 == 1))
            multiplier = 2
        elif sel_type == "range":
            win = (sel_value == "low" and 1 <= num <= 18) or (sel_value == "high" and 19 <= num <= 36)
            multiplier = 2
        elif sel_type == "dozen":
            win = num != 0 and (num - 1) // 12 + 1 == sel_value
            multiplier = 3
        if win:
            payout = self.bet * multiplier
            self.app.balance += payout
            self.message = f"Caiu {num}. Vitória na roleta: {br_money(payout)} fichas."
        else:
            self.message = f"Caiu {num}. A banca levou esta rodada."

    def draw_wheel(self, surface, center, radius):
        pygame.draw.circle(surface, (12, 16, 26), center, radius + 16)
        pygame.draw.circle(surface, GOLD, center, radius + 12, 4)
        for i in range(37):
            angle = -math.pi / 2 + (i / 37) * math.tau
            next_angle = -math.pi / 2 + ((i + 1) / 37) * math.tau
            points = [center]
            for a in (angle, (angle + next_angle) / 2, next_angle):
                points.append((int(center[0] + math.cos(a) * radius), int(center[1] + math.sin(a) * radius)))
            pygame.draw.polygon(surface, self.number_color(i), points)
        pygame.draw.circle(surface, (17, 23, 37), center, int(radius * 0.62))
        pygame.draw.circle(surface, (89, 68, 37), center, int(radius * 0.32))
        pygame.draw.circle(surface, GOLD_2, center, int(radius * 0.14))
        angle = -math.pi / 2 + (self.current / 37) * math.tau
        ball = (int(center[0] + math.cos(angle) * (radius * 0.82)), int(center[1] + math.sin(angle) * (radius * 0.82)))
        pygame.draw.circle(surface, WHITE, ball, 10)
        draw_text(surface, str(self.current), self.app.fonts["h1"], WHITE, center, "center")

    def draw_number_grid(self, surface):
        self.number_rects = []
        x0, y0 = 360, 198
        zero = pygame.Rect(x0 - 64, y0, 54, 164)
        self.number_rects.append((zero, 0))
        color = self.number_color(0)
        rounded_rect(surface, zero, color, 8, 2, GOLD if self.selected == ("number", 0) else (68, 82, 105))
        draw_text(surface, "0", self.app.fonts["h3"], WHITE, zero.center, "center")
        for n in range(1, 37):
            col = (n - 1) // 3
            row = 2 - ((n - 1) % 3)
            rect = pygame.Rect(x0 + col * 54, y0 + row * 54, 50, 50)
            self.number_rects.append((rect, n))
            border = GOLD if self.selected == ("number", n) else (68, 82, 105)
            rounded_rect(surface, rect, self.number_color(n), 7, 2, border)
            draw_text(surface, str(n), self.app.fonts["small"], WHITE, rect.center, "center")

    def selection_text(self):
        kind, value = self.selected
        names = {
            ("color", "red"): "Vermelho",
            ("color", "black"): "Preto",
            ("parity", "even"): "Par",
            ("parity", "odd"): "Ímpar",
            ("range", "low"): "1-18",
            ("range", "high"): "19-36",
            ("dozen", 1): "1a dúzia",
            ("dozen", 2): "2a dúzia",
            ("dozen", 3): "3a dúzia",
        }
        if kind == "number":
            return f"Número {value}"
        return names.get(self.selected, str(self.selected))

    def draw(self, surface):
        self.draw_panel_title(surface, "Roleta", "Mesa europeia 0-36 com apostas internas e externas.")
        self.draw_wheel(surface, (170, 330), 128)
        table = pygame.Rect(280, 168, 500, 246)
        rounded_rect(surface, table, (11, 101, 68), 18, 3, (30, 139, 94))
        self.draw_number_grid(surface)
        side = pygame.Rect(800, 168, 404, 246)
        rounded_rect(surface, side, PANEL, 18, 1, (76, 90, 118))
        draw_text(surface, "APOSTAS EXTERNAS", self.app.fonts["tiny"], MUTED, (820, 182))
        draw_text(surface, f"Selecionado: {self.selection_text()}", self.app.fonts["body"], GOLD_2, (820, 368))
        msg_rect = pygame.Rect(292, 604, 510, 74)
        rounded_rect(surface, msg_rect, PANEL_2, 12, 1, (82, 96, 126))
        draw_centered_wrapped(surface, self.message, self.app.fonts["small"], WHITE, msg_rect)
        self.draw_bet_box(surface, 850, 604)


class SlotsScene(CasinoGameScene):
    symbols = [
        ("67", 12, (255, 224, 119), 6),
        ("AURA", 8, (118, 212, 255), 9),
        ("EGO", 6, (255, 122, 177), 11),
        ("◆", 5, (115, 232, 187), 13),
        ("BAR", 4, (230, 230, 238), 16),
        ("7", 3, (255, 95, 95), 20),
        ("C", 2, (255, 174, 99), 25),
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
        self.reel_stop = [0, 0, 0, 0, 0]
        self.message = "Gire os rolos. Sequências da esquerda pagam."
        self.last_lines = []

    def can_change_bet(self):
        return self.spinning <= 0

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

    def build_ui(self):
        self.buttons = [Button(pygame.Rect(24, 22, 112, 42), "Menu", lambda: self.app.set_scene("menu"), "secondary")]
        self.add_bet_buttons(850, 604)
        self.buttons.append(Button(pygame.Rect(64, 604, 180, 52), "Girar", self.spin, "success", self.spinning <= 0 and self.app.balance >= self.bet))

    def spin(self):
        if self.spinning > 0 or self.app.balance < self.bet:
            return
        self.app.balance -= self.bet
        self.spinning = 1.8
        self.reel_stop = [1.0 + i * 0.18 for i in range(5)]
        self.last_lines = []
        self.message = "Rolos girando..."

    def update(self, dt):
        if self.spinning > 0:
            self.spinning -= dt
            for col in range(5):
                if self.reel_stop[col] > 0:
                    self.reel_stop[col] -= dt
                    for row in range(3):
                        self.grid[row][col] = self.pick_symbol()[0]
            if self.spinning <= 0:
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
            lines = ", ".join(f"{sym} x{count}" for _, count, sym, _ in self.last_lines)
            self.message = f"{lines}. Pagamento total: {br_money(payout)} fichas."
        else:
            self.message = "Sem sequência premiada desta vez."

    def draw_symbol(self, surface, rect, symbol):
        base, color = self.symbol_info(symbol)
        rounded_rect(surface, rect, (244, 239, 225), 14, 2, (203, 191, 164))
        pygame.draw.circle(surface, (34, 40, 58), rect.center, min(rect.w, rect.h) // 2 - 16)
        size = self.app.fonts["h3"] if len(symbol) > 2 else self.app.fonts["h1"]
        draw_text(surface, symbol, size, color, rect.center, "center")

    def draw_paylines(self, surface, slot_rect):
        colors = [GOLD_2, BLUE, RED, GREEN, PURPLE]
        cell_w, cell_h, gap = 128, 108, 12
        x0, y0 = slot_rect.x + 26, slot_rect.y + 28
        for idx, line in enumerate(self.paylines):
            if not any(found[0] == idx for found in self.last_lines):
                continue
            pts = []
            for col, row in enumerate(line):
                pts.append((x0 + col * (cell_w + gap) + cell_w // 2, y0 + row * (cell_h + gap) + cell_h // 2))
            pygame.draw.lines(surface, colors[idx], False, pts, 6)

    def draw(self, surface):
        self.draw_panel_title(surface, "Slots", "Cinco rolos, cinco linhas e símbolo 67 como prêmio máximo.")
        slot_rect = pygame.Rect(240, 162, 800, 410)
        rounded_rect(surface, slot_rect, (90, 19, 48), 24, 5, GOLD)
        inner = pygame.Rect(slot_rect.x + 16, slot_rect.y + 18, slot_rect.w - 32, slot_rect.h - 36)
        rounded_rect(surface, inner, (20, 25, 42), 18, 2, (116, 92, 63))
        cell_w, cell_h, gap = 128, 108, 12
        x0, y0 = slot_rect.x + 26, slot_rect.y + 28
        for row in range(3):
            for col in range(5):
                rect = pygame.Rect(x0 + col * (cell_w + gap), y0 + row * (cell_h + gap), cell_w, cell_h)
                self.draw_symbol(surface, rect, self.grid[row][col])
        self.draw_paylines(surface, slot_rect)
        for i, (sym, base, color, _) in enumerate(self.symbols[:5]):
            y = 184 + i * 42
            draw_text(surface, f"{sym}", self.app.fonts["body"], color, (70, y))
            draw_text(surface, f"3x paga {base}x", self.app.fonts["small"], MUTED, (140, y + 3))
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

    def can_change_bet(self):
        return not self.active

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
        x0, y0 = 342, 160
        for row in range(5):
            for col in range(5):
                index = row * 5 + col
                rect = pygame.Rect(x0 + col * (size + gap), y0 + row * (size + gap), size, size)
                self.grid_rects.append((rect, index))
                revealed = index in self.revealed
                mine_visible = self.round_over and index in self.mines
                if mine_visible:
                    color = RED
                elif revealed:
                    color = GREEN
                else:
                    color = (35, 47, 72) if self.active else (29, 38, 57)
                rounded_rect(surface, rect, color, 14, 2, GOLD if revealed else (68, 82, 105))
                if mine_visible:
                    pygame.draw.circle(surface, (93, 18, 28), rect.center, 22)
                    pygame.draw.circle(surface, WHITE, (rect.centerx - 8, rect.centery - 8), 4)
                elif revealed:
                    pygame.draw.polygon(
                        surface,
                        WHITE,
                        [
                            (rect.centerx - 19, rect.centery),
                            (rect.centerx - 5, rect.centery + 16),
                            (rect.centerx + 22, rect.centery - 18),
                            (rect.centerx + 14, rect.centery - 23),
                            (rect.centerx - 6, rect.centery + 3),
                            (rect.centerx - 14, rect.centery - 7),
                        ],
                    )
                else:
                    draw_text(surface, "?", self.app.fonts["h2"], MUTED, rect.center, "center")

    def draw(self, surface):
        self.draw_panel_title(surface, "Mines", "Abra casas seguras, aumente o risco e saque antes da bomba.")
        board = pygame.Rect(310, 128, 510, 484)
        rounded_rect(surface, board, PANEL, 24, 2, (76, 90, 118))
        self.draw_grid(surface)
        side = pygame.Rect(850, 156, 330, 402)
        rounded_rect(surface, side, PANEL, 18, 1, (76, 90, 118))
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


class CasinoApp:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Casino 67 Aura + Ego")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.fonts = self.load_fonts()
        self.balance = 5000
        self.running = True
        self.scenes = {
            "menu": MenuScene(self),
            "blackjack": BlackjackScene(self),
            "dice": DiceScene(self),
            "roulette": RouletteScene(self),
            "slots": SlotsScene(self),
            "mines": MinesScene(self),
        }
        self.scene_name = "menu"
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

    def set_scene(self, name):
        self.scene_name = name
        self.scene = self.scenes[name]
        self.scene.on_enter()

    def refill_balance(self):
        self.balance = 5000

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
        draw_text(self.screen, "Casino 67 Aura + Ego", self.fonts["h3"], GOLD_2, (158, 25))
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
                if self.scene_name == "menu":
                    self.running = False
                else:
                    self.set_scene("menu")

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self.scene.build_ui()
            for event in pygame.event.get():
                self.handle_global(event)
                self.scene.handle_event(event)
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
