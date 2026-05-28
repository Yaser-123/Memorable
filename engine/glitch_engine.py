"""
MEMORABLE — Glitch Engine
Dynamic visual distortion effects for Pygame surfaces.
"""

import random
import pygame
from store.game_state import GameState

class GlitchEngine:
    def __init__(self, audio_engine):
        self.audio = audio_engine
        self.state = GameState()
        
        self.burst_timer = 0.0
        self.burst_intensity = 0.0
        
        self.flash_timer = 0.0
        self.flash_color = (255, 255, 255)

    def trigger_burst(self, duration: float = 0.4, intensity: float = 0.6):
        """Trigger a sudden intense glitch spike."""
        self.burst_timer = duration
        self.burst_intensity = intensity
        self.audio.play_sfx('glitch', volume=0.5, channel=1)

    def trigger_flash(self, color=(255, 255, 255), duration: float = 0.2):
        """Full screen color flash."""
        self.flash_timer = duration
        self.flash_color = color

    def update(self, dt: float):
        if self.burst_timer > 0:
            self.burst_timer -= dt
            if self.burst_timer <= 0:
                self.burst_timer = 0
                self.burst_intensity = 0.0
                
        if self.flash_timer > 0:
            self.flash_timer -= dt
            if self.flash_timer < 0:
                self.flash_timer = 0

        # Pass glitch intensity to audio degradation
        current_intensity = self.get_intensity()
        if current_intensity > 0.05:
            self.audio.set_glitch_degradation(current_intensity)
        else:
            self.audio.set_glitch_degradation(0.0)

    def get_intensity(self) -> float:
        """Combine base state intensity with active burst intensity."""
        return min(1.0, self.state.glitch_intensity + (self.burst_intensity if self.burst_timer > 0 else 0))

    def apply_glitch(self, surface: pygame.Surface) -> pygame.Surface:
        """Apply visual glitch effects to a surface based on intensity."""
        intensity = self.get_intensity()
        if intensity <= 0.02:
            return surface

        w, h = surface.get_size()
        out = surface.copy()
        
        # 1. RGB Split
        if intensity > 0.15 or self.burst_timer > 0:
            offset = int((intensity * 12) + (random.random() * 4))
            
            # Create semi-transparent red/blue copies
            red_surf = pygame.Surface((w, h))
            red_surf.fill((255, 0, 0))
            red_surf.blit(surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            red_surf.set_alpha(int(100 * intensity))
            
            blue_surf = pygame.Surface((w, h))
            blue_surf.fill((0, 0, 255))
            blue_surf.blit(surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            blue_surf.set_alpha(int(100 * intensity))
            
            out.blit(red_surf, (-offset, 0))
            out.blit(blue_surf, (offset, 0))

        # 2. Horizontal Tears (slice and shift)
        if intensity > 0.3 or (self.burst_timer > 0 and random.random() > 0.3):
            num_tears = max(1, int(intensity * 10))
            for _ in range(num_tears):
                tear_y = random.randint(0, h - 2)
                tear_h = random.randint(4, 25)
                tear_h = min(tear_h, h - tear_y)
                shift = random.randint(-int(intensity * 30), int(intensity * 30))
                
                slice_rect = pygame.Rect(0, tear_y, w, tear_h)
                slice_surf = surface.subsurface(slice_rect).copy()
                
                # Draw black over original spot
                pygame.draw.rect(out, (0, 0, 0), slice_rect)
                # Blit shifted
                out.blit(slice_surf, (shift, tear_y))
                
        return out

    def draw_flash(self, surface: pygame.Surface):
        """Draw active screen flash overlay."""
        if self.flash_timer > 0:
            alpha = int(255 * (self.flash_timer / 0.2)) # Assuming 0.2s max flash
            alpha = max(0, min(255, alpha))
            overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            overlay.fill((*self.flash_color, alpha))
            surface.blit(overlay, (0, 0))
