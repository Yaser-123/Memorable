"""
MEMORABLE — Dialogue Engine
Handles typewriter effect, pacing, and text rendering.
"""

import pygame
from utils import draw_text_wrapped, draw_glow_text, wrap_text
from constants import (
    CYAN, RED_GLOW, TEXT, VIOLET, MUTED,
    DLGBOX_X, DLGBOX_Y, DLGBOX_W, DLGBOX_H,
    DLGTXT_X, DLGTXT_Y, DLGTXT_W,
    SPEAKER_X, SPEAKER_Y,
    PANEL_BG
)

class DialogueEngine:
    def __init__(self, audio_engine, fonts):
        self.audio = audio_engine
        self.fonts = fonts
        
        self.speaker = ""
        self.full_text = ""
        self.current_text = ""
        self.char_index = 0
        
        self.emotion = "neutral"
        self.is_done = True
        
        self.type_timer = 0.0
        self.base_speed = 0.04
        self.pause_timer = 0.0
        
        self.speaker_colors = {
            "Ash": CYAN,
            "MNEMOS": VIOLET,
            "System": RED_GLOW,
            "Dr. Ashworth": MUTED
        }

    def start(self, speaker: str, text: str, emotion: str = "neutral"):
        self.speaker = speaker
        self.full_text = text
        self.emotion = emotion
        
        self.current_text = ""
        self.char_index = 0
        self.is_done = False
        self.type_timer = 0.0
        self.pause_timer = 0.0
        
        if emotion == 'urgent':
            self.base_speed = 0.015
        elif emotion == 'hesitant':
            self.base_speed = 0.07
        elif emotion == 'glitch':
            self.base_speed = 0.05
        else:
            self.base_speed = 0.035
            
        # Start continuous looping typing sound
        self.audio.stop_channel(0)
        if text.strip():
            self.audio.play_sfx('typing', volume=0.4, channel=0, loops=-1)

    def skip(self):
        """Instantly finish typing."""
        if not self.is_done:
            self.current_text = self.full_text
            self.char_index = len(self.full_text)
            self.is_done = True
            self.pause_timer = 0.0
            self.audio.stop_channel(0)

    def update(self, dt: float):
        if self.is_done:
            return
            
        if self.pause_timer > 0:
            self.pause_timer -= dt
            if self.pause_timer <= 0:
                self.audio.unpause_channel(0)
            return

        self.type_timer += dt
        
        chars_to_add = 0
        while self.type_timer >= self.base_speed and not self.is_done:
            self.type_timer -= self.base_speed
            chars_to_add += 1
            
        if chars_to_add > 0:
            end_idx = min(self.char_index + chars_to_add, len(self.full_text))
            new_chars = self.full_text[self.char_index:end_idx]
            
            self.current_text += new_chars
            self.char_index = end_idx
            
            # Check for punctuation pauses
            if new_chars:
                last_char = new_chars[-1]
                if last_char in ['.', '!', '?']:
                    self.pause_timer = 0.4
                elif last_char in [',', ';', '-']:
                    self.pause_timer = 0.15
                    
            if self.char_index >= len(self.full_text):
                self.is_done = True
                self.audio.stop_channel(0)
            elif self.pause_timer > 0:
                self.audio.pause_channel(0)

    def draw(self, surface: pygame.Surface):
        if not self.speaker and not self.full_text:
            return
            
        # Draw semi-transparent panel
        panel = pygame.Surface((DLGBOX_W, DLGBOX_H), pygame.SRCALPHA)
        panel.fill((*PANEL_BG, 220))
        # Top border line
        pygame.draw.line(panel, MUTED, (0, 0), (DLGBOX_W, 0), 2)
        
        surface.blit(panel, (DLGBOX_X, DLGBOX_Y))
        
        # Draw speaker
        if self.speaker:
            color = self.speaker_colors.get(self.speaker, CYAN)
            if self.emotion == 'glitch':
                color = RED_GLOW
            
            draw_glow_text(
                surface, 
                self.fonts['speaker'], 
                self.speaker.upper(), 
                (SPEAKER_X, SPEAKER_Y), 
                color,
                glow_passes=2,
                base_alpha=60
            )
            
        # Draw text
        color = TEXT
        if self.emotion == 'system':
            color = RED_GLOW
        elif self.emotion == 'mnemos':
            color = VIOLET
            
        draw_text_wrapped(
            surface, 
            self.fonts['body'], 
            self.current_text, 
            (DLGTXT_X, DLGTXT_Y), 
            color, 
            max_width=DLGTXT_W,
            line_spacing=6
        )
