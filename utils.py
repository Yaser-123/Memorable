"""
MEMORABLE — Rendering utilities.
Image loading, text wrapping, glow effects, vignette, scanlines.
"""

import os
import math
import pygame

from constants import SCREEN_W, SCREEN_H, CYAN, VOID


# ── Image loading ────────────────────────────────────────────────

_image_cache: dict = {}

def load_image(path: str, size: tuple | None = None, alpha: bool = True) -> pygame.Surface:
    """Load and cache an image, scaling to `size` if given."""
    key = (path, size)
    if key in _image_cache:
        return _image_cache[key]

    if not os.path.exists(path):
        # Return a dark placeholder
        w, h = size or (400, 300)
        surf = pygame.Surface((w, h))
        surf.fill(VOID)
        _image_cache[key] = surf
        return surf

    try:
        img = pygame.image.load(path)
        img = img.convert_alpha() if alpha else img.convert()
        if size:
            img = pygame.transform.smoothscale(img, size)
        _image_cache[key] = img
        return img
    except Exception as e:
        print(f"[utils] Image load failed: {path} — {e}")
        w, h = size or (400, 300)
        surf = pygame.Surface((w, h))
        surf.fill(VOID)
        _image_cache[key] = surf
        return surf


def load_portrait(path: str, max_height: int) -> pygame.Surface:
    """Load a portrait, scaled proportionally to max_height."""
    if not os.path.exists(path):
        surf = pygame.Surface((int(max_height * 0.55), max_height))
        surf.fill((20, 20, 35))
        return surf
    try:
        img = pygame.image.load(path).convert_alpha()
        ratio = max_height / img.get_height()
        new_w = max(1, int(img.get_width() * ratio))
        return pygame.transform.smoothscale(img, (new_w, max_height))
    except Exception as e:
        print(f"[utils] Portrait load failed: {path} — {e}")
        surf = pygame.Surface((int(max_height * 0.55), max_height))
        surf.fill((20, 20, 35))
        return surf


# ── Font loading ─────────────────────────────────────────────────

_font_cache: dict = {}

_FONT_PATHS = {
    'orbitron':   'fonts/Orbitron/Orbitron-VariableFont_wght.ttf',
    'audiowide':  'fonts/Audiowide/Audiowide-Regular.ttf',
    'rajdhani':   'fonts/Rajdhani/Rajdhani-Regular.ttf',
    'rajdhani_b': 'fonts/Rajdhani/Rajdhani-Bold.ttf',
    'rajdhani_l': 'fonts/Rajdhani/Rajdhani-Light.ttf',
    'rajdhani_m': 'fonts/Rajdhani/Rajdhani-Medium.ttf',
}

def load_font(base_dir: str, name: str, size: int) -> pygame.font.Font:
    key = (name, size)
    if key in _font_cache:
        return _font_cache[key]
    path = os.path.join(base_dir, _FONT_PATHS.get(name, ''))
    try:
        f = pygame.font.Font(path, size)
    except Exception:
        f = pygame.font.SysFont('courier', size, bold=('b' in name))
    _font_cache[key] = f
    return f


# ── Text rendering ───────────────────────────────────────────────

def wrap_text(font: pygame.font.Font, text: str, max_width: int) -> list[str]:
    """Break text into lines that fit within max_width pixels."""
    words = text.split()
    lines, current = [], []
    for word in words:
        test = ' '.join(current + [word])
        if font.size(test)[0] <= max_width:
            current.append(word)
        else:
            if current:
                lines.append(' '.join(current))
            current = [word]
    if current:
        lines.append(' '.join(current))
    return lines or ['']


def draw_text_wrapped(surface, font, text, pos, color, max_width, line_spacing=4):
    """Render multi-line wrapped text to surface. Returns total height used."""
    x, y = pos
    lines = wrap_text(font, text, max_width)
    lh = font.get_linesize() + line_spacing
    for i, line in enumerate(lines):
        surf = font.render(line, True, color)
        surface.blit(surf, (x, y + i * lh))
    return len(lines) * lh


def draw_centered(surface, font, text, cy, color):
    """Draw text horizontally centered on screen at vertical position cy."""
    surf = font.render(text, True, color)
    x = SCREEN_W // 2 - surf.get_width() // 2
    surface.blit(surf, (x, cy))
    return surf.get_width(), surf.get_height()


# ── Glow text ────────────────────────────────────────────────────

def draw_glow_text(surface, font, text, pos, color, glow_color=CYAN,
                   glow_passes=3, base_alpha=40):
    """Render text with a multi-pass glow effect."""
    x, y = pos
    txt_surf = font.render(text, True, color)

    for i in range(glow_passes, 0, -1):
        radius = i * 3
        alpha = min(255, base_alpha + i * 20)
        glow = pygame.Surface(
            (txt_surf.get_width() + radius * 2,
             txt_surf.get_height() + radius * 2),
            pygame.SRCALPHA
        )
        g = font.render(text, True, glow_color)
        g.set_alpha(alpha)
        # Blit at multiple offsets
        for dx in range(-radius, radius + 1, max(1, radius // 2)):
            for dy in range(-radius, radius + 1, max(1, radius // 2)):
                glow.blit(g, (radius + dx, radius + dy))
        surface.blit(glow, (x - radius, y - radius))

    surface.blit(txt_surf, pos)


def draw_centered_glow(surface, font, text, cy, color, glow_color=CYAN, glow_passes=3):
    """draw_glow_text but horizontally centered."""
    w = font.size(text)[0]
    x = SCREEN_W // 2 - w // 2
    draw_glow_text(surface, font, text, (x, cy), color, glow_color, glow_passes)


# ── Vignette ─────────────────────────────────────────────────────

def create_vignette(width: int, height: int, strength: float = 0.85) -> pygame.Surface:
    """Pre-render a vignette overlay (call once at startup)."""
    surf = pygame.Surface((width, height), pygame.SRCALPHA)
    max_dim = max(width, height)

    # Top and bottom gradient
    edge = height // 3
    for i in range(edge):
        t = 1 - i / edge
        alpha = int(t ** 2.2 * 210 * strength)
        pygame.draw.line(surf, (0, 0, 0, alpha), (0, i), (width, i))
        pygame.draw.line(surf, (0, 0, 0, alpha), (0, height - 1 - i), (width, height - 1 - i))

    # Left and right gradient
    side = width // 5
    for i in range(side):
        t = 1 - i / side
        alpha = int(t ** 2.5 * 160 * strength)
        pygame.draw.line(surf, (0, 0, 0, alpha), (i, 0), (i, height))
        pygame.draw.line(surf, (0, 0, 0, alpha), (width - 1 - i, 0), (width - 1 - i, height))

    return surf


# ── Scanlines ────────────────────────────────────────────────────

def create_scanlines(width: int, height: int, alpha: int = 18) -> pygame.Surface:
    """Pre-render static scanline overlay."""
    surf = pygame.Surface((width, height), pygame.SRCALPHA)
    for y in range(0, height, 4):
        pygame.draw.line(surf, (0, 0, 0, alpha), (0, y), (width, y))
    return surf


# ── Misc ─────────────────────────────────────────────────────────

def alpha_surface(color_rgb, size, alpha):
    """Create a solid-color surface with given alpha."""
    surf = pygame.Surface(size, pygame.SRCALPHA)
    surf.fill((*color_rgb, alpha))
    return surf


def lerp(a, b, t):
    return a + (b - a) * t


def clamp(val, lo, hi):
    return max(lo, min(hi, val))


def ease_in_out(t):
    return t * t * (3 - 2 * t)
