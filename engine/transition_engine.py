"""
MEMORABLE — Transition Engine
Cinematic screen transitions for Pygame.
"""

import pygame
from utils import alpha_surface, SCREEN_W, SCREEN_H

class TransitionEngine:
    def __init__(self):
        self.active = False
        self.type = 'none'
        self.duration = 0.0
        self.timer = 0.0
        self.midpoint_reached = False
        self.callback = None
        
        self.color = (0, 0, 0)
        self.static_img = None

    def start(self, trans_type: str, duration: float, callback=None):
        self.active = True
        self.type = trans_type
        self.duration = duration
        self.timer = 0.0
        self.midpoint_reached = False
        self.callback = callback
        
        if trans_type == 'white_flash':
            self.color = (255, 255, 255)
        elif trans_type == 'dissolve':
            self.color = (10, 10, 15)
        else:
            self.color = (0, 0, 0)

    def update(self, dt: float):
        if not self.active:
            return

        self.timer += dt
        
        # Midpoint callback
        half_dur = self.duration / 2.0
        if not self.midpoint_reached and self.timer >= half_dur:
            self.midpoint_reached = True
            if self.callback:
                self.callback()
                
        if self.timer >= self.duration:
            self.active = False
            self.timer = self.duration

    def draw(self, surface: pygame.Surface):
        if not self.active:
            return

        t = self.timer / self.duration
        
        # Peak opacity at midpoint (t=0.5)
        if t <= 0.5:
            alpha = int((t / 0.5) * 255)
        else:
            alpha = int((1.0 - ((t - 0.5) / 0.5)) * 255)
            
        alpha = max(0, min(255, alpha))

        if self.type == 'glitch_cut':
            # Fast RGB flashing
            frames = [
                (255, 0, 51, 128),
                (0, 51, 255, 100),
                (0, 0, 0, 255),
                (255, 255, 255, 255),
                (0, 0, 0, 255)
            ]
            idx = min(int((t * len(frames))), len(frames)-1)
            r, g, b, a = frames[idx]
            overlay = alpha_surface((r,g,b), (SCREEN_W, SCREEN_H), a)
            surface.blit(overlay, (0, 0))
            
        elif self.type == 'static_storm':
            # Simple noise approximation
            overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            overlay.fill((5, 5, 16, alpha))
            import random
            for _ in range(50):
                pygame.draw.line(overlay, (0, 245, 228, alpha//4), 
                                 (0, random.randint(0, SCREEN_H)),
                                 (SCREEN_W, random.randint(0, SCREEN_H)))
            surface.blit(overlay, (0, 0))
            
        elif self.type == 'iris_in':
            overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 255))
            
            if t > 0.1:
                # Carve out a circle that grows
                radius = int((t - 0.1) * 1.2 * max(SCREEN_W, SCREEN_H))
                pygame.draw.circle(overlay, (0, 0, 0, 0), (SCREEN_W//2, SCREEN_H//2), radius)
                
            surface.blit(overlay, (0, 0))
            
        else:
            # Standard fade (fade_black, dissolve, white_flash)
            overlay = alpha_surface(self.color, (SCREEN_W, SCREEN_H), alpha)
            surface.blit(overlay, (0, 0))

    def is_blocking(self) -> bool:
        return self.active and self.timer < (self.duration / 2.0)
