import random
import sys
import pygame

# =========================
# 설정
# =========================
COLS, ROWS = 10, 20
BLOCK = 30
MARGIN = 20
PANEL_W = 200

W = MARGIN * 2 + COLS * BLOCK + PANEL_W
H = MARGIN * 2 + ROWS * BLOCK

FPS = 60

BG = (18, 18, 22)
GRID_LINE = (35, 35, 45)
TEXT = (235, 235, 245)

BGM_FILE = "tetris_bgm.mp3"

COLORS = {
    "I": (0, 240, 240),
    "O": (240, 240, 0),
    "T": (160, 0, 240),
    "S": (0, 240, 0),
    "Z": (240, 0, 0),
    "J": (0, 80, 240),
    "L": (240, 160, 0),
}

SHAPES = {
    "I": [
        ["....", "XXXX", "....", "...."],
        ["..X.", "..X.", "..X.", "..X."],
    ],
    "O": [
        [".XX.", ".XX.", "....", "...."],
    ],
    "T": [
        [".X..", "XXX.", "....", "...."],
        [".X..", ".XX.", ".X..", "...."],
        ["....", "XXX.", ".X..", "...."],
        [".X..", "XX..", ".X..", "...."],
    ],
    "S": [
        [".XX.", "XX..", "....", "...."],
        [".X..", ".XX.", "..X.", "...."],
    ],
    "Z": [
        ["XX..", ".XX.", "....", "...."],
        ["..X.", ".XX.", ".X..", "...."],
    ],
    "J": [
        ["X...", "XXX.", "....", "...."],
        [".XX.", ".X..", ".X..", "...."],
        ["....", "XXX.", "..X.", "...."],
        [".X..", ".X..", "XX..", "...."],
    ],
    "L": [
        ["..X.", "XXX.", "....", "...."],
        [".X..", ".X..", ".XX.", "...."],
        ["....", "XXX.", "X...", "...."],
        ["XX..", ".X..", ".X..", "...."],
    ],
}

# =========================
# 유틸
# =========================
def shape_cells(shape_key, rot_idx):
    mat = SHAPES[shape_key][rot_idx]
    cells = []
    for y in range(4):
        for x in range(4):
            if mat[y][x] == "X":
                cells.append((x, y))
    return cells

def empty_board():
    return [[None for _ in range(COLS)] for _ in range(ROWS)]

def in_bounds(x, y):
    return 0 <= x < COLS and 0 <= y < ROWS

def can_place(board, shape_key, rot_idx, px, py):
    for dx, dy in shape_cells(shape_key, rot_idx):
        x = px + dx
        y = py + dy
        if y < 0:
            continue
        if not in_bounds(x, y):
            return False
        if board[y][x] is not None:
            return False
    return True

def lock_piece(board, shape_key, rot_idx, px, py):
    for dx, dy in shape_cells(shape_key, rot_idx):
        x = px + dx
        y = py + dy
        if y >= 0:
            board[y][x] = COLORS[shape_key]

def clear_lines(board):
    new_rows = []
    cleared = 0
    for y in range(ROWS):
        if all(board[y][x] is not None for x in range(COLS)):
            cleared += 1
        else:
            new_rows.append(board[y])
    while len(new_rows) < ROWS:
        new_rows.insert(0, [None for _ in range(COLS)])
    for y in range(ROWS):
        board[y] = new_rows[y]
    return cleared

def hard_drop_y(board, shape_key, rot_idx, px, py):
    y = py
    while can_place(board, shape_key, rot_idx, px, y + 1):
        y += 1
    return y

# =========================
# 게임
# =========================
class Tetris:
    def __init__(self):
        self.board = empty_board()
        self.score = 0
        self.lines = 0
        self.level = 1

        self.game_over = False
        self.paused = False

        self.cur = None
        self.next = self._new_piece()
        self._spawn()

        self.fall_acc = 0
        self.last_tick = pygame.time.get_ticks()

    def _new_piece(self):
        key = random.choice(list(SHAPES.keys()))
        rot = 0
        px = COLS // 2 - 2
        py = -2
        return {"k": key, "r": rot, "x": px, "y": py}

    def _spawn(self):
        self.cur = self.next
        self.next = self._new_piece()
        if not can_place(self.board, self.cur["k"], self.cur["r"], self.cur["x"], self.cur["y"]):
            self.game_over = True

    def toggle_pause(self):
        if self.game_over:
            return
        self.paused = not self.paused
        # 멈춘 동안 시간 누적 방지(재개 시 순간 낙하 방지)
        self.last_tick = pygame.time.get_ticks()
        self.fall_acc = 0

    def fall_ms(self):
        # 레벨이 오를수록 빨라짐 (최소 80ms)
        base = 500
        ms = base - (self.level - 1) * 40
        return max(80, ms)

    def recalc_level(self):
        # 10줄마다 레벨 +1
        self.level = 1 + (self.lines // 10)

    def move(self, dx):
        if self.game_over or self.paused:
            return
        nx = self.cur["x"] + dx
        if can_place(self.board, self.cur["k"], self.cur["r"], nx, self.cur["y"]):
            self.cur["x"] = nx

    def soft_drop(self):
        if self.game_over or self.paused:
            return
        if can_place(self.board, self.cur["k"], self.cur["r"], self.cur["x"], self.cur["y"] + 1):
            self.cur["y"] += 1
            self.score += 1  # 소프트드롭 점수(선택)
        else:
            self._lock_and_next()

    def rotate_cw(self):
        if self.game_over or self.paused:
            return
        k = self.cur["k"]
        r = self.cur["r"]
        nr = (r + 1) % len(SHAPES[k])
        for kick in [0, -1, 1, -2, 2]:
            nx = self.cur["x"] + kick
            if can_place(self.board, k, nr, nx, self.cur["y"]):
                self.cur["r"] = nr
                self.cur["x"] = nx
                return

    def hard_drop(self):
        if self.game_over or self.paused:
            return
        y0 = self.cur["y"]
        y1 = hard_drop_y(self.board, self.cur["k"], self.cur["r"], self.cur["x"], self.cur["y"])
        self.cur["y"] = y1
        self.score += max(0, (y1 - y0)) * 2  # 하드드롭 점수(선택)
        self._lock_and_next()

    def _lock_and_next(self):
        lock_piece(self.board, self.cur["k"], self.cur["r"], self.cur["x"], self.cur["y"])
        cleared = clear_lines(self.board)
        if cleared:
            self.lines += cleared
            # 라인 점수 (테트리스 스타일)
            # 1줄 100, 2줄 300, 3줄 500, 4줄 800 * 레벨
            self.score += [0, 100, 300, 500, 800][cleared] * self.level
            self.recalc_level()
        self._spawn()

    def update(self):
        if self.game_over or self.paused:
            return

        now = pygame.time.get_ticks()
        dt = now - self.last_tick
        self.last_tick = now
        self.fall_acc += dt

        if self.fall_acc >= self.fall_ms():
            self.fall_acc %= self.fall_ms()
            if can_place(self.board, self.cur["k"], self.cur["r"], self.cur["x"], self.cur["y"] + 1):
                self.cur["y"] += 1
            else:
                self._lock_and_next()

# =========================
# 렌더링
# =========================
def draw_board(screen, board):
    ox = MARGIN
    oy = MARGIN

    pygame.draw.rect(screen, (24, 24, 30), (ox, oy, COLS * BLOCK, ROWS * BLOCK), border_radius=8)

    for x in range(COLS + 1):
        pygame.draw.line(screen, GRID_LINE,
                         (ox + x * BLOCK, oy),
                         (ox + x * BLOCK, oy + ROWS * BLOCK))
    for y in range(ROWS + 1):
        pygame.draw.line(screen, GRID_LINE,
                         (ox, oy + y * BLOCK),
                         (ox + COLS * BLOCK, oy + y * BLOCK))

    for y in range(ROWS):
        for x in range(COLS):
            c = board[y][x]
            if c is None:
                continue
            px = ox + x * BLOCK
            py = oy + y * BLOCK
            pygame.draw.rect(screen, c, (px + 2, py + 2, BLOCK - 4, BLOCK - 4), border_radius=6)

def draw_piece(screen, piece, ghost_y=None):
    ox = MARGIN
    oy = MARGIN
    k, r, x, y = piece["k"], piece["r"], piece["x"], piece["y"]
    color = COLORS[k]

    if ghost_y is not None:
        for dx, dy in shape_cells(k, r):
            gx = x + dx
            gy = ghost_y + dy
            if gy < 0:
                continue
            px = ox + gx * BLOCK
            py = oy + gy * BLOCK
            pygame.draw.rect(screen, (90, 90, 100),
                             (px + 6, py + 6, BLOCK - 12, BLOCK - 12), border_radius=6)

    for dx, dy in shape_cells(k, r):
        bx = x + dx
        by = y + dy
        if by < 0:
            continue
        px = ox + bx * BLOCK
        py = oy + by * BLOCK
        pygame.draw.rect(screen, color, (px + 2, py + 2, BLOCK - 4, BLOCK - 4), border_radius=6)

def draw_panel(screen, game, font):
    px = MARGIN * 2 + COLS * BLOCK
    py = MARGIN
    w = PANEL_W - MARGIN
    h = ROWS * BLOCK

    pygame.draw.rect(screen, (24, 24, 30), (px, py, w, h), border_radius=8)

    def line(label, value, yoff):
        s = font.render(f"{label}: {value}", True, TEXT)
        screen.blit(s, (px + 14, py + yoff))

    line("Score", game.score, 14)
    line("Lines", game.lines, 44)
    line("Level", game.level, 74)
    line("Speed(ms)", game.fall_ms(), 104)

    title = font.render("Next", True, TEXT)
    screen.blit(title, (px + 14, py + 140))

    k = game.next["k"]
    preview_x = px + 20
    preview_y = py + 175
    mini = 18
    for dx, dy in shape_cells(k, 0):
        rx = preview_x + dx * mini
        ry = preview_y + dy * mini
        pygame.draw.rect(screen, COLORS[k], (rx, ry, mini - 2, mini - 2), border_radius=4)

    guide = [
        "←/→ : 이동",
        "↑   : 회전",
        "↓   : 아래로",
        "Space: 바로 떨어뜨리기",
        "P   : 일시정지",
        "R   : (게임오버) 재시작",
    ]
    y = py + h - 160
    for g in guide:
        s = font.render(g, True, (200, 200, 210))
        screen.blit(s, (px + 14, y))
        y += 22

def draw_overlay_center(screen, text, font, sub=None, subfont=None):
    overlay = pygame.Surface((COLS * BLOCK, ROWS * BLOCK), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 140))
    screen.blit(overlay, (MARGIN, MARGIN))

    msg = font.render(text, True, (240, 240, 240))
    rect = msg.get_rect(center=(MARGIN + (COLS * BLOCK)//2, MARGIN + (ROWS * BLOCK)//2 - 20))
    screen.blit(msg, rect)

    if sub and subfont:
        s2 = subfont.render(sub, True, (220, 220, 220))
        r2 = s2.get_rect(center=(MARGIN + (COLS * BLOCK)//2, MARGIN + (ROWS * BLOCK)//2 + 20))
        screen.blit(s2, r2)

# =========================
# 메인
# =========================
def main():
    pygame.init()

    # 🎵 배경음악
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(BGM_FILE)
        pygame.mixer.music.set_volume(0.4)
        pygame.mixer.music.play(-1)
    except pygame.error as e:
        print(f"[BGM 경고] 배경음악 재생 불가: {e}")

    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Tetris (pygame)")
    clock = pygame.time.Clock()

    font = pygame.font.SysFont(None, 24)
    big = pygame.font.SysFont(None, 44)

    game = Tetris()

    while True:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                try:
                    pygame.mixer.music.stop()
                except pygame.error:
                    pass
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    game.toggle_pause()
                elif event.key == pygame.K_LEFT:
                    game.move(-1)
                elif event.key == pygame.K_RIGHT:
                    game.move(1)
                elif event.key == pygame.K_UP:
                    game.rotate_cw()
                elif event.key == pygame.K_DOWN:
                    game.soft_drop()
                elif event.key == pygame.K_SPACE:
                    game.hard_drop()
                elif event.key == pygame.K_r and game.game_over:
                    game = Tetris()

        game.update()

        screen.fill(BG)
        draw_board(screen, game.board)

        if not game.game_over:
            ghost = hard_drop_y(game.board, game.cur["k"], game.cur["r"], game.cur["x"], game.cur["y"])
            draw_piece(screen, game.cur, ghost_y=ghost)
        else:
            draw_overlay_center(screen, "GAME OVER", big, "Press R to restart", font)

        if game.paused and not game.game_over:
            draw_overlay_center(screen, "PAUSED", big, "Press P to resume", font)

        draw_panel(screen, game, font)
        pygame.display.flip()

if __name__ == "__main__":
    main()
