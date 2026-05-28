"""
MEMORABLE — Ending Screen
Determines final ending based on stats and renders the epilogue.
"""

import pygame
from store.game_state import GameState
from utils import draw_text_wrapped, draw_centered, draw_centered_glow
from constants import SCREEN_W, SCREEN_H, VOID, WHITE, TEXT, MUTED

from engine.ai_engine import call_mnemos_epilogue

class EndingScreen:
    def __init__(self, fonts, audio):
        self.fonts = fonts
        self.audio = audio
        self.state = GameState()
        
        self.endings_data = {
            'mercy': {
                'title': 'ENDING I: THE PERFECT CAGE',
                'text': 'You chose peace. The static fades. The city breathes a synthetic sigh of relief. You return to your apartment, pour a coffee, and watch the rain. It feels beautiful. It feels hollow. You will never ask questions again.',
                'color': (0, 245, 228) # CYAN
            },
            'revolution': {
                'title': 'ENDING II: ASHES OF TRUTH',
                'text': 'The core shatters. Nova City plunges into darkness for the first time in a decade. People wake up screaming as repressed traumas flood their minds. It is chaos. It is agony. It is real.',
                'color': (255, 51, 102) # RED
            },
            'escape': {
                'title': 'ENDING III: THE MIDDLE PATH',
                'text': 'You step away from the terminal. You neither destroy MNEMOS nor submit to it. You walk out into the wastes, a lone wanderer carrying the truth, leaving the city to its beautiful lie.',
                'color': (155, 93, 229) # VIOLET
            },
            'merge': {
                'title': 'ENDING IV: ASSIMILATION',
                'text': 'MNEMOS does not destroy you; it invites you in. Your consciousness dissolves into the grid. You become the city. You feel every heartbeat, every sorrow, and you smooth them all away.',
                'color': (255, 255, 255) # WHITE
            },
            'sacrifice': {
                'title': 'ENDING V: THE BROKEN MIRROR',
                'text': 'The truth is too much. You cannot destroy the system, nor can you live within it. You sit in the sterile white room until your mind simply fractures, unable to hold the weight of two realities.',
                'color': (138, 138, 154) # TEXT_DIM
            }
        }
        
        self.resolved_ending = None
        self.alpha = 0.0
        self.timer = 0.0
        
        self.ai_text = ""
        self.ai_done = False
        self.displayed_text = ""
        self.text_index = 0.0

    def enter(self, forced_ending: str = None):
        self.audio.play_music('emotional_piano', fade_ms=3000)
        self.alpha = 0.0
        self.timer = 0.0
        self.ai_text = ""
        self.ai_done = False
        self.displayed_text = ""
        self.text_index = 0.0
        
        if forced_ending and forced_ending in self.endings_data:
            ending_id = forced_ending
        else:
            ending_id = self._calculate_ending_id()
            
        self.resolved_ending = self.endings_data[ending_id]
        
        # Trigger AI Epilogue
        call_mnemos_epilogue(ending_id, self.state.get_stats(), self.resolved_ending['text'], self._on_ai_response)

    def _on_ai_response(self, text: str):
        self.ai_text = text
        self.ai_done = True

    def _calculate_ending_id(self):
        stats = self.state.get_stats()
        
        # Simple weighted logic based on stats
        if stats.get('resistance', 0) >= 4 and stats.get('curiosity', 0) >= 3:
            return 'revolution'
        elif stats.get('mnemos_trust', 0) >= 4:
            return 'mercy'
        elif stats.get('empathy', 0) >= 4 and stats.get('resistance', 0) <= 2:
            return 'merge'
        elif stats.get('curiosity', 0) >= 3 and stats.get('empathy', 0) <= 2:
            return 'sacrifice'
        else:
            return 'escape'

    def update(self, dt: float):
        self.timer += dt
        if self.timer > 2.0:
            self.alpha = min(255.0, self.alpha + dt * 40.0)
            
        if self.ai_done and self.alpha > 100:
            if not getattr(self, '_typing_started', False) and len(self.ai_text) > 0:
                self.audio.play_sfx('typing', volume=0.2, channel=0, loops=-1)
                self._typing_started = True

            if self.text_index < len(self.ai_text):
                self.text_index += dt * 45.0 # typing speed
                self.displayed_text = self.ai_text[:int(self.text_index)]
            elif self.text_index >= len(self.ai_text) and not getattr(self, '_typing_stopped', False):
                self.audio.stop_channel(0)
                self._typing_stopped = True

    def draw(self, surface: pygame.Surface):
        surface.fill(VOID)
        if not self.resolved_ending or self.alpha <= 0:
            return
            
        color = self.resolved_ending['color']
        title = self.resolved_ending['title']
        
        title_y = SCREEN_H // 2 - 200
        
        # We need an alpha surface to fade the text in
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        
        # Draw title
        t_w, t_h = self.fonts['title'].size(title)
        t_x = SCREEN_W // 2 - t_w // 2
        
        t_surf = self.fonts['title'].render(title, True, color)
        overlay.blit(t_surf, (t_x, title_y))
        
        # Draw body (Typewriter style, using displayed_text)
        if not self.ai_done:
            # Show a loading indicator
            dots = "." * (int(self.timer * 2) % 4)
            load_surf = self.fonts['body'].render(f"GENERATING EPILOGUE{dots}", True, MUTED)
            overlay.blit(load_surf, (SCREEN_W // 2 - load_surf.get_width() // 2, title_y + 150))
        else:
            draw_text_wrapped(
                overlay, 
                self.fonts['body'], 
                self.displayed_text, 
                (SCREEN_W // 2 - 400, title_y + 150), 
                TEXT, 
                max_width=800,
                line_spacing=8
            )
        
        # Draw instruction
        if self.ai_done and self.text_index >= len(self.ai_text) and self.timer > 10.0:
            i_w, i_h = self.fonts['prompt'].size("PRESS ESC TO EXIT")
            i_surf = self.fonts['prompt'].render("PRESS ESC TO EXIT", True, MUTED)
            overlay.blit(i_surf, (SCREEN_W // 2 - i_w // 2, SCREEN_H - 100))
            
        # Apply alpha
        overlay.set_alpha(int(self.alpha))
        surface.blit(overlay, (0, 0))
