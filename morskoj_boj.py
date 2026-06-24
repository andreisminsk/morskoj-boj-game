"""
Morskoj Boj (Морской Бой) — Soviet Sea Battle Periscope Arcade
A retro 2D arcade game inspired by the classic Soviet periscope slot machine.
All graphics and audio are generated procedurally — no external assets required.
"""

import pygame
import sys
import math
import random
import struct

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SCREEN_W, SCREEN_H = 800, 600
FPS = 60
HORIZON_Y = 180                # Where the sky meets the water
PERISCOPE_CX = SCREEN_W // 2   # Center of the periscope view
PERISCOPE_CY = SCREEN_H // 2
PERISCOPE_RADIUS = 270          # Radius of the circular viewing mask
MAX_TORPEDOES = 10
BONUS_THRESHOLD = 10            # Hits needed for bonus round
TORPEDO_SPEED = 5.0            # Pixels per frame (vertical rise)
SHIP_SPAWN_INTERVAL = 120       # Frames between ship spawns (base)
WORLD_WIDTH = 2400              # Virtual world width in pixels

# Colors (retro neon palette)
BLACK       = (0, 0, 0)
DARK_SEA    = (0, 12, 8)
NEON_GREEN  = (0, 255, 70)
NEON_CYAN   = (0, 255, 255)
NEON_RED    = (255, 50, 50)
DIM_GREEN   = (0, 80, 30)
DIM_CYAN    = (0, 80, 80)
WHITE       = (255, 255, 255)
YELLOW      = (255, 255, 0)
ORANGE      = (255, 160, 0)
DARK_GRAY   = (30, 30, 30)
MID_GRAY    = (60, 60, 60)
WATER_COLOR = (0, 30, 50)
SKY_COLOR   = (0, 5, 15)


# ---------------------------------------------------------------------------
# Procedural Sound Generation
# ---------------------------------------------------------------------------
def _make_sound_buffer(samples_iter, sample_rate=22050):
    """Convert an iterable of float samples in [-1, 1] to a pygame Sound."""
    buf = bytearray()
    for s in samples_iter:
        clamped = max(-1.0, min(1.0, s))
        packed = struct.pack('<h', int(clamped * 32767))
        buf.extend(packed)
    return pygame.mixer.Sound(buffer=bytes(buf))


def generate_torpedo_sound(sample_rate=22050):
    """Short rising-frequency chirp for torpedo launch."""
    duration = 0.18
    n = int(sample_rate * duration)
    def samples():
        for i in range(n):
            t = i / sample_rate
            freq = 400 + 2000 * (i / n)  # sweep 400→2400 Hz
            yield 0.3 * math.sin(2 * math.pi * freq * t) * (1 - i / n)
    return _make_sound_buffer(samples(), sample_rate)


def generate_explosion_sound(sample_rate=22050):
    """Noise burst with decay — classic 8-bit explosion."""
    duration = 0.45
    n = int(sample_rate * duration)
    rng = random.Random(42)  # deterministic noise
    def samples():
        for i in range(n):
            t = i / sample_rate
            decay = max(0, 1 - t / duration)
            noise = rng.uniform(-1, 1)
            low_boom = 0.4 * math.sin(2 * math.pi * 60 * t) * decay
            yield (low_boom + 0.6 * noise * decay) * 0.5
    return _make_sound_buffer(samples(), sample_rate)


def generate_miss_sound(sample_rate=22050):
    """Low splash thud for a miss."""
    duration = 0.25
    n = int(sample_rate * duration)
    def samples():
        for i in range(n):
            t = i / sample_rate
            decay = max(0, 1 - t / duration)
            yield 0.25 * math.sin(2 * math.pi * 120 * t) * decay
    return _make_sound_buffer(samples(), sample_rate)


def generate_bonus_sound(sample_rate=22050):
    """Ascending arpeggio for bonus round activation."""
    duration = 0.6
    n = int(sample_rate * duration)
    notes = [523, 659, 784, 1047]  # C5 E5 G5 C6
    def samples():
        for i in range(n):
            t = i / sample_rate
            seg = min(int(t / duration * len(notes)), len(notes) - 1)
            freq = notes[seg]
            decay = max(0, 1 - t / duration)
            yield 0.3 * math.sin(2 * math.pi * freq * t) * decay
    return _make_sound_buffer(samples(), sample_rate)


# ---------------------------------------------------------------------------
# Periscope — draws the HUD overlay (circle mask, crosshair, bearing scale)
# ---------------------------------------------------------------------------
class Periscope:
    def __init__(self):
        self.bearing = 0.0  # Current bearing in degrees (0 = North)
        self.target_bearing = 0.0
        # Bearing is mapped to world offset:
        #   world_offset = bearing * (WORLD_WIDTH / 360)
        #   so rotating the periscope scrolls the world left/right.

    def update(self, keys, mouse_rel):
        """Update bearing from keyboard or mouse input."""
        rotate_speed = 1.5  # degrees per frame
        if keys[pygame.K_LEFT]:
            self.target_bearing -= rotate_speed
        if keys[pygame.K_RIGHT]:
            self.target_bearing += rotate_speed
        # Mouse horizontal movement rotates periscope
        self.target_bearing += mouse_rel[0] * 0.3
        # Clamp bearing to ±60 degrees (visible arc)
        self.target_bearing = max(-60, min(60, self.target_bearing))
        # Smooth interpolation toward target
        self.bearing += (self.target_bearing - self.bearing) * 0.12

    @property
    def world_offset(self):
        """Convert bearing to a pixel offset in the virtual world.
        The world is WORLD_WIDTH pixels wide; 360° maps to the full width.
        This means each degree of bearing = WORLD_WIDTH/360 pixels of scroll.
        """
        return self.bearing * (WORLD_WIDTH / 360.0)

    def draw(self, surface):
        """Draw the periscope HUD overlay."""
        cx, cy, r = PERISCOPE_CX, PERISCOPE_CY, PERISCOPE_RADIUS

        # --- Black out everything outside the circular viewport ---
        # We draw four corner rects and four edge fills, then a circle mask.
        mask_surf = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        mask_surf.fill((0, 0, 0, 255))
        pygame.draw.circle(mask_surf, (0, 0, 0, 0), (cx, cy), r)
        surface.blit(mask_surf, (0, 0))

        # --- Periscope ring ---
        pygame.draw.circle(surface, DIM_GREEN, (cx, cy), r, 3)
        pygame.draw.circle(surface, NEON_GREEN, (cx, cy), r, 1)

        # --- Crosshair lines ---
        # Horizontal waterline
        pygame.draw.line(surface, DIM_GREEN, (cx - r, HORIZON_Y), (cx + r, HORIZON_Y), 1)
        # Vertical center line
        pygame.draw.line(surface, DIM_GREEN, (cx, cy - r), (cx, cy + r), 1)
        # Short tick marks on crosshair
        for offset in range(-200, 201, 50):
            pygame.draw.line(surface, DIM_GREEN,
                             (cx + offset, HORIZON_Y - 6),
                             (cx + offset, HORIZON_Y + 6), 1)

        # --- Bearing scale at top ---
        self._draw_bearing_scale(surface)

        # --- Range marks on vertical axis ---
        self._draw_range_marks(surface)

    def _draw_bearing_scale(self, surface):
        """Draw a degree scale across the top of the viewport."""
        cx, r = PERISCOPE_CX, PERISCOPE_RADIUS
        y_top = PERISCOPE_CY - r + 30
        # Bearing labels every 10 degrees relative to center
        for deg in range(-60, 61, 10):
            x = cx + int(deg * (r / 60.0))
            if cx - r < x < cx + r:
                pygame.draw.line(surface, DIM_GREEN, (x, y_top), (x, y_top + 8), 1)
                label_bearing = int(self.bearing + deg)
                font = pygame.font.SysFont("consolas", 11)
                txt = font.render(f"{label_bearing}°", True, DIM_GREEN)
                surface.blit(txt, (x - txt.get_width() // 2, y_top + 9))

    def _draw_range_marks(self, surface):
        """Draw horizontal range lines below the horizon."""
        cx, r = PERISCOPE_CX, PERISCOPE_RADIUS
        for i, frac in enumerate([0.25, 0.5, 0.75]):
            y = HORIZON_Y + int((SCREEN_H - HORIZON_Y) * frac)
            half_w = int(r * (1 - frac * 0.5))
            pygame.draw.line(surface, (0, 40, 30), (cx - half_w, y), (cx + half_w, y), 1)
            font = pygame.font.SysFont("consolas", 10)
            rng_txt = font.render(f"R{i+1}", True, (0, 60, 40))
            surface.blit(rng_txt, (cx + half_w + 4, y - 6))


# ---------------------------------------------------------------------------
# Ship — enemy target vessel
# ---------------------------------------------------------------------------
class Ship:
    # Ship type definitions: (name, width, height, speed_range, color, points)
    TYPES = [
        ("Destroyer",  60, 18, (1.0, 2.0), NEON_GREEN, 1),
        ("Cruiser",    80, 22, (0.7, 1.5), NEON_CYAN,   2),
        ("Battleship", 100, 28, (0.4, 1.0), NEON_RED,   3),
    ]

    def __init__(self, world_x=None):
        self.type_info = random.choice(self.TYPES)
        self.name, self.base_w, self.base_h, (spd_lo, spd_hi), self.color, self.points = self.type_info
        # Depth factor: ships further away are smaller and slower
        self.depth = random.uniform(0.6, 1.0)  # 1.0 = closest
        self.width = int(self.base_w * self.depth)
        self.height = int(self.base_h * self.depth)
        self.speed = random.uniform(spd_lo, spd_hi) * self.depth
        # Direction: +1 = moving right, -1 = moving left
        self.direction = random.choice([-1, 1])
        # World x position (wraps around WORLD_WIDTH)
        if world_x is None:
            self.world_x = random.uniform(0, WORLD_WIDTH)
        else:
            self.world_x = world_x
        self.alive = True
        # Y position on screen (near horizon, offset by depth)
        self.screen_y = HORIZON_Y + int((1.0 - self.depth) * 20) + random.randint(0, 15)

    def update(self):
        """Move ship horizontally in world coordinates."""
        self.world_x += self.speed * self.direction
        # Wrap around world boundaries
        if self.world_x > WORLD_WIDTH:
            self.world_x -= WORLD_WIDTH
        elif self.world_x < 0:
            self.world_x += WORLD_WIDTH

    def screen_x(self, world_offset):
        """Convert world position to screen position, accounting for periscope offset.
        The screen x is: world_x - world_offset + PERISCOPE_CX
        This maps the world coordinate system so that the center of the
        periscope view corresponds to world_offset, and objects to the
        right of that offset appear to the right on screen, etc.
        """
        sx = self.world_x - world_offset + PERISCOPE_CX
        # Handle wrapping: pick the closest representation
        if sx > WORLD_WIDTH / 2:
            sx -= WORLD_WIDTH
        elif sx < -WORLD_WIDTH / 2:
            sx += WORLD_WIDTH
        return sx

    def draw(self, surface, world_offset):
        """Draw the ship as a pixel-art silhouette."""
        sx = self.screen_x(world_offset)
        # Cull if off-screen
        if sx < -self.width or sx > SCREEN_W + self.width:
            return
        # Hull — main body rectangle
        hull_rect = pygame.Rect(int(sx - self.width // 2),
                                self.screen_y,
                                self.width, self.height)
        pygame.draw.rect(surface, self.color, hull_rect, 0)
        # Superstructure — small rectangle on top
        ss_w = max(4, self.width // 4)
        ss_h = max(3, self.height // 2)
        ss_rect = pygame.Rect(int(sx - ss_w // 2),
                               self.screen_y - ss_h,
                               ss_w, ss_h)
        pygame.draw.rect(surface, self.color, ss_rect, 0)
        # Mast — thin vertical line
        mast_h = max(4, int(self.height * 0.8))
        pygame.draw.line(surface, self.color,
                         (int(sx), self.screen_y - ss_h - mast_h),
                         (int(sx), self.screen_y - ss_h), 1)
        # Glow effect — draw again with alpha for bloom
        glow_surf = pygame.Surface((self.width + 8, self.height + 8), pygame.SRCALPHA)
        glow_color = (*self.color[:3], 40)
        pygame.draw.rect(glow_surf, glow_color,
                         (0, 0, self.width + 8, self.height + 8), 0)
        surface.blit(glow_surf,
                     (int(sx - self.width // 2 - 4),
                      self.screen_y - 4))

    def get_hitbox(self, world_offset):
        """Return a screen-space Rect for collision detection."""
        sx = self.screen_x(world_offset)
        return pygame.Rect(int(sx - self.width // 2),
                           self.screen_y - self.height,
                           self.width, self.height + self.height // 2)


# ---------------------------------------------------------------------------
# Torpedo — player's projectile
# ---------------------------------------------------------------------------
class Torpedo:
    def __init__(self, start_x):
        self.x = start_x
        self.y = SCREEN_H - 40  # Launch from bottom of periscope view
        self.speed = TORPEDO_SPEED
        self.alive = True
        self.trail = []  # List of (x, y) for trail effect

    def update(self):
        """Move torpedo upward toward the horizon."""
        self.trail.append((self.x, self.y))
        if len(self.trail) > 8:
            self.trail.pop(0)
        self.y -= self.speed
        # Torpedo dies if it goes past the horizon
        if self.y < HORIZON_Y - 30:
            self.alive = False

    def draw(self, surface):
        """Draw torpedo as a bright dot with a trailing line."""
        # Trail
        for i, (tx, ty) in enumerate(self.trail):
            alpha = int(255 * (i + 1) / len(self.trail)) if self.trail else 255
            c = (0, min(255, alpha), min(255, alpha))
            pygame.draw.circle(surface, c, (int(tx), int(ty)), 1)
        # Head
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), 3)
        pygame.draw.circle(surface, NEON_CYAN, (int(self.x), int(self.y)), 2)

    def get_hitbox(self):
        """Small hitbox for the torpedo head."""
        return pygame.Rect(int(self.x) - 4, int(self.y) - 4, 8, 8)


# ---------------------------------------------------------------------------
# Explosion — animated expanding circles on hit
# ---------------------------------------------------------------------------
class Explosion:
    def __init__(self, x, y, color=ORANGE):
        self.x = x
        self.y = y
        self.color = color
        self.frame = 0
        self.max_frames = 30
        self.alive = True
        self.max_radius = random.randint(20, 35)

    def update(self):
        self.frame += 1
        if self.frame >= self.max_frames:
            self.alive = False

    def draw(self, surface):
        """Draw expanding pixelated circles with color fade."""
        progress = self.frame / self.max_frames
        radius = int(self.max_radius * progress)
        if radius < 1:
            return
        # Outer ring
        alpha = max(0, int(255 * (1 - progress)))
        color_faded = (
            min(255, self.color[0]),
            min(255, int(self.color[1] * (1 - progress * 0.5))),
            min(255, int(self.color[2] * (1 - progress)))
        )
        pygame.draw.circle(surface, color_faded, (int(self.x), int(self.y)), radius, 2)
        # Inner flash
        if progress < 0.3:
            inner_r = max(1, int(radius * 0.5))
            pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), inner_r, 0)
        # Pixel debris particles
        if self.frame % 3 == 0:
            for angle in range(0, 360, 45):
                px = self.x + math.cos(math.radians(angle)) * radius * 0.8
                py = self.y + math.sin(math.radians(angle)) * radius * 0.8
                pygame.draw.circle(surface, YELLOW, (int(px), int(py)), 2)


# ---------------------------------------------------------------------------
# Splash — miss effect (water splash)
# ---------------------------------------------------------------------------
class Splash:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.frame = 0
        self.max_frames = 20
        self.alive = True

    def update(self):
        self.frame += 1
        if self.frame >= self.max_frames:
            self.alive = False

    def draw(self, surface):
        progress = self.frame / self.max_frames
        radius = int(15 * progress)
        alpha = max(0, int(200 * (1 - progress)))
        color = (0, min(255, 100 + alpha), min(255, 200 + alpha // 2))
        if radius > 0:
            pygame.draw.circle(surface, color, (int(self.x), int(self.y)), radius, 1)
            if progress < 0.4:
                pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), max(1, radius // 3), 0)


# ---------------------------------------------------------------------------
# Game — main game controller
# ---------------------------------------------------------------------------
class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("Морской Бой — Morskoj Boj (Sea Battle)")
        self.clock = pygame.time.Clock()

        # Procedural sound effects
        self.snd_torpedo = generate_torpedo_sound()
        self.snd_explosion = generate_explosion_sound()
        self.snd_miss = generate_miss_sound()
        self.snd_bonus = generate_bonus_sound()

        # Game objects
        self.periscope = Periscope()
        self.ships = []
        self.torpedoes = []
        self.explosions = []
        self.splashes = []

        # Game state
        self.torpedoes_left = MAX_TORPEDOES
        self.score = 0
        self.hits = 0
        self.bonus_round = False
        self.game_over = False
        self.spawn_timer = 0
        self.frame_count = 0

        # Fonts
        self.font_large = pygame.font.SysFont("consolas", 28, bold=True)
        self.font_medium = pygame.font.SysFont("consolas", 20)
        self.font_small = pygame.font.SysFont("consolas", 14)

        # Stars (static background decoration)
        self.stars = [(random.randint(0, SCREEN_W), random.randint(0, HORIZON_Y - 20))
                      for _ in range(40)]

        # Wave animation offset
        self.wave_offset = 0.0

    def spawn_ship(self):
        """Spawn a new ship at a random world position."""
        self.ships.append(Ship())

    def fire_torpedo(self):
        """Launch a torpedo from the bottom center of the periscope view."""
        if self.torpedoes_left > 0 and not self.game_over:
            # Torpedo launches from center-bottom of periscope view
            # It travels straight up, so its x is always PERISCOPE_CX
            t = Torpedo(PERISCOPE_CX)
            self.torpedoes.append(t)
            self.torpedoes_left -= 1
            self.snd_torpedo.play()

    def check_collisions(self):
        """Check torpedo-ship collisions at the horizon level."""
        world_offset = self.periscope.world_offset
        for torpedo in self.torpedoes:
            if not torpedo.alive:
                continue
            t_box = torpedo.get_hitbox()
            hit = False
            for ship in self.ships:
                if not ship.alive:
                    continue
                s_box = ship.get_hitbox(world_offset)
                if t_box.colliderect(s_box):
                    # Hit!
                    ship.alive = False
                    torpedo.alive = False
                    self.explosions.append(Explosion(torpedo.x, torpedo.y, ship.color))
                    self.score += ship.points
                    self.hits += 1
                    self.snd_explosion.play()
                    hit = True
                    break
            if not hit and not torpedo.alive:
                # Torpedo reached horizon without hitting — it's a miss
                # (torpedo.alive was set to False in update when y < horizon)
                pass

        # Check for torpedoes that went past horizon without hitting (miss)
        for torpedo in self.torpedoes:
            if not torpedo.alive and torpedo.y < HORIZON_Y:
                # Only count as miss splash if not already processed as hit
                already_hit = any(e for e in self.explosions
                                  if abs(e.x - torpedo.x) < 30 and e.frame < 5)
                if not already_hit:
                    self.splashes.append(Splash(torpedo.x, HORIZON_Y))
                    self.snd_miss.play()

    def check_bonus(self):
        """Check if player qualifies for a bonus round."""
        if self.hits >= BONUS_THRESHOLD and not self.bonus_round:
            self.bonus_round = True
            self.torpedoes_left += MAX_TORPEDOES
            self.snd_bonus.play()

    def check_game_over(self):
        """End game when out of torpedoes and none in flight."""
        if self.torpedoes_left <= 0 and len(self.torpedoes) == 0:
            self.game_over = True

    def draw_background(self, surface):
        """Draw the sea, sky, and stars."""
        # Sky gradient
        for y in range(HORIZON_Y):
            frac = y / HORIZON_Y
            r = int(0 + 5 * frac)
            g = int(5 + 20 * frac)
            b = int(15 + 40 * frac)
            pygame.draw.line(surface, (r, g, b), (0, y), (SCREEN_W, y))

        # Stars
        for sx, sy in self.stars:
            brightness = random.randint(120, 200) if random.random() > 0.95 else 160
            pygame.draw.circle(surface, (brightness, brightness, brightness), (sx, sy), 1)

        # Water
        for y in range(HORIZON_Y, SCREEN_H):
            depth_frac = (y - HORIZON_Y) / (SCREEN_H - HORIZON_Y)
            r = int(0)
            g = int(30 + 40 * depth_frac)
            b = int(50 + 60 * depth_frac)
            pygame.draw.line(surface, (r, g, b), (0, y), (SCREEN_W, y))

        # Animated wave lines
        self.wave_offset += 0.02
        for i in range(5):
            y_wave = HORIZON_Y + 30 + i * 60
            points = []
            for x in range(0, SCREEN_W + 20, 20):
                wy = y_wave + math.sin(self.wave_offset + x * 0.02 + i) * 3
                points.append((x, wy))
            if len(points) > 1:
                pygame.draw.lines(surface, (0, 60 + i * 8, 80 + i * 10), False, points, 1)

    def draw_hud(self, surface):
        """Draw the heads-up display with score, torpedoes, and status."""
        # Torpedo counter (left side)
        label_t = self.font_medium.render("ТОРПЕДЫ", True, NEON_GREEN)
        surface.blit(label_t, (20, 20))
        for i in range(MAX_TORPEDOES):
            x = 20 + i * 22
            y = 48
            color = NEON_CYAN if i < self.torpedoes_left else DARK_GRAY
            # Draw torpedo icon
            pygame.draw.rect(surface, color, (x, y, 16, 6), 0)
            pygame.draw.polygon(surface, color, [(x + 16, y), (x + 22, y + 3), (x + 16, y + 6)])

        # Score (right side)
        score_text = f"СЧЁТ: {self.score}"
        label_s = self.font_medium.render(score_text, True, NEON_GREEN)
        surface.blit(label_s, (SCREEN_W - label_s.get_width() - 20, 20))

        hits_text = f"ПОПАДАНИЯ: {self.hits}"
        label_h = self.font_small.render(hits_text, True, DIM_GREEN)
        surface.blit(label_h, (SCREEN_W - label_h.get_width() - 20, 48))

        # Bonus round indicator
        if self.bonus_round:
            bonus_text = "★ БОНУСНЫЙ РАУНД ★"
            pulse = int(128 + 127 * math.sin(self.frame_count * 0.1))
            bt = self.font_large.render(bonus_text, True, (pulse, pulse, 0))
            surface.blit(bt, (SCREEN_W // 2 - bt.get_width() // 2, 80))

        # Bearing indicator
        bearing_text = f"КУРС: {int(self.periscope.bearing):+d}°"
        label_b = self.font_small.render(bearing_text, True, DIM_GREEN)
        surface.blit(label_b, (SCREEN_W // 2 - label_b.get_width() // 2, SCREEN_H - 30))

        # Game over
        if self.game_over:
            overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            surface.blit(overlay, (0, 0))
            go_text = "КОНЕЦ ИГРЫ"
            go_surf = self.font_large.render(go_text, True, NEON_RED)
            surface.blit(go_surf, (SCREEN_W // 2 - go_surf.get_width() // 2,
                                    SCREEN_H // 2 - 40))
            final_text = f"ФИНАЛЬНЫЙ СЧЁТ: {self.score}  |  ПОПАДАНИЯ: {self.hits}"
            ft_surf = self.font_medium.render(final_text, True, NEON_CYAN)
            surface.blit(ft_surf, (SCREEN_W // 2 - ft_surf.get_width() // 2,
                                    SCREEN_H // 2 + 10))
            restart_text = "НАЖМИТЕ R ДЛЯ ПЕРЕЗАПУСКА"
            rt_surf = self.font_small.render(restart_text, True, DIM_GREEN)
            surface.blit(rt_surf, (SCREEN_W // 2 - rt_surf.get_width() // 2,
                                    SCREEN_H // 2 + 50))

    def reset(self):
        """Reset the game to initial state."""
        self.ships.clear()
        self.torpedoes.clear()
        self.explosions.clear()
        self.splashes.clear()
        self.torpedoes_left = MAX_TORPEDOES
        self.score = 0
        self.hits = 0
        self.bonus_round = False
        self.game_over = False
        self.spawn_timer = 0
        self.periscope = Periscope()

    def run(self):
        """Main game loop."""
        pygame.mouse.set_visible(False)
        running = True

        while running:
            # --- Event handling ---
            mouse_rel = (0, 0)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
                        if not self.game_over:
                            self.fire_torpedo()
                    elif event.key == pygame.K_r:
                        if self.game_over:
                            self.reset()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1 and not self.game_over:
                        self.fire_torpedo()
                elif event.type == pygame.MOUSEMOTION:
                    mouse_rel = event.rel

            keys = pygame.key.get_pressed()

            if not self.game_over:
                # --- Update ---
                self.periscope.update(keys, mouse_rel)

                # Spawn ships periodically
                self.spawn_timer += 1
                spawn_interval = max(40, SHIP_SPAWN_INTERVAL - self.hits * 3)
                if self.spawn_timer >= spawn_interval:
                    self.spawn_ship()
                    self.spawn_timer = 0

                # Update ships
                for ship in self.ships:
                    ship.update()

                # Update torpedoes
                for torpedo in self.torpedoes:
                    torpedo.update()

                # Update explosions
                for explosion in self.explosions:
                    explosion.update()

                # Update splashes
                for splash in self.splashes:
                    splash.update()

                # Collision detection
                self.check_collisions()

                # Check bonus
                self.check_bonus()

                # Clean up dead objects
                self.ships = [s for s in self.ships if s.alive]
                self.torpedoes = [t for t in self.torpedoes if t.alive]
                self.explosions = [e for e in self.explosions if e.alive]
                self.splashes = [s for s in self.splashes if s.alive]

                # Remove ships that have scrolled far off screen
                world_offset = self.periscope.world_offset
                self.ships = [s for s in self.ships
                              if -200 < s.screen_x(world_offset) < SCREEN_W + 200
                              or True]  # Keep all — they wrap in world coords

                # Check game over
                self.check_game_over()

            self.frame_count += 1

            # --- Draw ---
            self.screen.fill(BLACK)
            self.draw_background(self.screen)

            # Draw ships
            world_offset = self.periscope.world_offset
            for ship in self.ships:
                ship.draw(self.screen, world_offset)

            # Draw torpedoes
            for torpedo in self.torpedoes:
                torpedo.draw(self.screen)

            # Draw explosions
            for explosion in self.explosions:
                explosion.draw(self.screen)

            # Draw splashes
            for splash in self.splashes:
                splash.draw(self.screen)

            # Draw periscope overlay (masks edges, draws HUD)
            self.periscope.draw(self.screen)

            # Draw HUD
            self.draw_hud(self.screen)

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.mouse.set_visible(True)
        pygame.quit()
        sys.exit()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    game = Game()
    game.run()
