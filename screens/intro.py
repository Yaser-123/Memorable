"""
MEMORABLE — Cinematic Intro
"""

import pygame
from utils import draw_text_wrapped, SCREEN_W, SCREEN_H
from constants import VOID, TEXT

class CinematicIntro:
    def __init__(self, fonts, audio, transitions):
        self.fonts = fonts
        self.audio = audio
        self.transitions = transitions
        
        self.lines = [
            "2074.",
            "Nova City.",
            "A metropolis built on the ruins of human emotion.",
            "They promised us peace.",
            "They gave us MNEMOS.",
            "The system that remembers...",
            "...so you don't have to."
        ]
        
        self.timer = 0.0
        self.current_line = 0
        self.state = 'fade_in' # fade_in, hold, fade_out
        self.alpha = 0.0
        self.is_done = False

    def enter(self):
        self.audio.play_music('emotional_piano')
        self.timer = 0.0
        self.current_line = 0
        self.state = 'fade_in'
        self.alpha = 0.0
        self.is_done = False

    def update(self, dt: float):
        if self.is_done:
            return
            
        # Simple state machine for fading text in and out
        fade_speed = 255 * dt
        
        if self.state == 'fade_in':
            self.alpha += fade_speed
            if self.alpha >= 255:
                self.alpha = 255
                self.state = 'hold'
                self.timer = 1.0 # hold for 1 second
        elif self.state == 'hold':
            self.timer -= dt
            if self.timer <= 0:
                self.state = 'fade_out'
        elif self.state == 'fade_out':
            self.alpha -= fade_speed
            if self.alpha <= 0:
                self.alpha = 0
                self.current_line += 1
                if self.current_line >= len(self.lines):
                    self.is_done = True
                else:
                    self.state = 'fade_in'

    def draw(self, surface: pygame.Surface):
        surface.fill(VOID)
        if self.is_done or self.current_line >= len(self.lines):
            return
            
        line = self.lines[self.current_line]
        font = self.fonts['intro']
        
        w, h = font.size(line)
        x = SCREEN_W // 2 - w // 2
        y = SCREEN_H // 2 - h // 2
        
        surf = font.render(line, True, TEXT)
        surf.set_alpha(int(self.alpha))
        surface.blit(surf, (x, y))
