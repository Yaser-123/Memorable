"""
MEMORABLE — Title Screen
"""

import pygame
import math
import random
from utils import draw_centered_glow, draw_centered
from constants import SCREEN_W, SCREEN_H, CYAN, WHITE, VOID

class TitleScreen:
    def __init__(self, fonts, audio):
        self.fonts = fonts
        self.audio = audio
        self.timer = 0.0
        self.particles = []
        for _ in range(50):
            self.particles.append({
                'x': random.randint(0, SCREEN_W),
                'y': random.randint(0, SCREEN_H),
                'speed': random.uniform(5, 15),
                'size': random.uniform(1, 3)
            })

    def enter(self):
        self.audio.play_music('ambient_cyberpunk')

    def update(self, dt: float):
        self.timer += dt
        for p in self.particles:
            p['y'] -= p['speed'] * dt
            if p['y'] < 0:
                p['y'] = SCREEN_H
                p['x'] = random.randint(0, SCREEN_W)

    def draw(self, surface: pygame.Surface):
        surface.fill(VOID)
        
        # Particles
        for p in self.particles:
            pygame.draw.rect(surface, (0, 100, 100), (p['x'], p['y'], p['size'], p['size']))
            
        # Title
        title_y = SCREEN_H // 2 - 80
        draw_centered_glow(surface, self.fonts['title'], "MEMORABLE", title_y, WHITE, CYAN, 4)
        
        # Subtitle
        draw_centered(surface, self.fonts['subtitle'], "A Cinematic Interactive Experience", title_y + 80, CYAN)
        
        # Prompt
        alpha = int((math.sin(self.timer * 3) + 1) * 127)
        prompt_surf = self.fonts['prompt'].render("PRESS ANY KEY", True, WHITE)
        prompt_surf.set_alpha(alpha)
        surface.blit(prompt_surf, (SCREEN_W//2 - prompt_surf.get_width()//2, SCREEN_H - 150))
