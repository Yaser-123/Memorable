"""
MEMORABLE — Main Entry Point
Pure Python interactive narrative using Pygame and Groq API.
"""

import sys
import os
import pygame

# Initialize pygame early to allow font loading
pygame.init()
pygame.font.init()

from constants import SCREEN_W, SCREEN_H, FPS, VOID
from utils import load_font, create_vignette, create_scanlines
from engine.audio_engine import AudioEngine
from engine.glitch_engine import GlitchEngine
from engine.transition_engine import TransitionEngine
from engine.data_loader import load_scenes, load_characters

from screens.title import TitleScreen
from screens.intro import CinematicIntro
from screens.game_scene import GameScene
from screens.ending import EndingScreen

class MemorableGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.SCALED)
        pygame.display.set_caption("MEMORABLE")
        
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Globals
        base_dir = os.path.dirname(__file__)
        self.fonts = {
            'title':    load_font(base_dir, 'orbitron', 72),
            'subtitle': load_font(base_dir, 'orbitron', 24),
            'prompt':   load_font(base_dir, 'rajdhani_m', 20),
            'intro':    load_font(base_dir, 'rajdhani_l', 42),
            'body':     load_font(base_dir, 'rajdhani', 28),
            'speaker':  load_font(base_dir, 'audiowide', 22),
        }
        
        self.vignette = create_vignette(SCREEN_W, SCREEN_H, 0.8)
        self.scanlines = create_scanlines(SCREEN_W, SCREEN_H, 20)
        
        # Engines
        self.audio = AudioEngine()
        self.glitch = GlitchEngine(self.audio)
        self.transitions = TransitionEngine()
        
        # Data
        self.scenes = load_scenes()
        self.characters = load_characters()
        
        # Screens
        self.screens = {
            'title': TitleScreen(self.fonts, self.audio),
            'intro': CinematicIntro(self.fonts, self.audio, self.transitions),
            'game':  GameScene(self.fonts, self.audio, self.glitch, self.transitions, self.scenes, self.characters),
            'ending': EndingScreen(self.fonts, self.audio)
        }
        
        self.current_screen = 'title'
        self.screens['title'].enter()

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            
            # 1. Events
            self.handle_events()
            
            # 2. Update
            self.update(dt)
            
            # 3. Draw
            self.draw()
            
            pygame.display.flip()
            
        pygame.quit()
        sys.exit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.current_screen == 'ending' and self.screens['ending'].timer > 5.0:
                        self.running = False
                    # Allow skipping title
                
                if self.current_screen == 'title':
                    self._change_screen('intro')
                    
                elif self.current_screen == 'intro':
                    # Allow skipping intro
                    self._change_screen('game')
                    self.screens['game'].enter('scene_apartment_wake')
                    
                elif self.current_screen == 'game':
                    if event.key == pygame.K_SPACE:
                        # Skip typewriter
                        self.screens['game'].handle_click((-1, -1))
                        
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Left click
                    if self.current_screen == 'title':
                        self._change_screen('intro')
                    elif self.current_screen == 'intro':
                        self._change_screen('game')
                        self.screens['game'].enter('scene_apartment_wake')
                    elif self.current_screen == 'game':
                        self.screens['game'].handle_click(pygame.mouse.get_pos())

    def _change_screen(self, screen_name: str):
        if screen_name in self.screens:
            self.current_screen = screen_name
            if hasattr(self.screens[screen_name], 'enter'):
                # Note: 'game' and 'ending' need arguments for their enter() 
                # so we don't call them automatically here if they require args.
                if screen_name in ['title', 'intro']:
                    self.screens[screen_name].enter()

    def update(self, dt: float):
        # Update current screen logic
        screen_obj = self.screens[self.current_screen]
        if self.current_screen == 'game':
            screen_obj.update(dt, pygame.mouse.get_pos())
            
            # Check if game reached the end
            if hasattr(screen_obj, 'state') and getattr(screen_obj.state, 'reached_ending', None):
                 # It's over.
                 self._change_screen('ending')
                 self.screens['ending'].enter(screen_obj.state.reached_ending)
        else:
            screen_obj.update(dt)
            
            if self.current_screen == 'intro' and getattr(screen_obj, 'is_done', False):
                self._change_screen('game')
                self.screens['game'].enter('scene_apartment_wake')
                
        # Global engines
        self.glitch.update(dt)
        self.transitions.update(dt)
        
        # Time tracking
        if self.current_screen == 'game':
            self.screens['game'].state.tick(dt)

    def draw(self):
        # 1. Base clear
        self.screen.fill(VOID)
        
        # 2. Render Screen
        base_surface = pygame.Surface((SCREEN_W, SCREEN_H))
        self.screens[self.current_screen].draw(base_surface)
        
        # 3. Global Effects
        glitched = self.glitch.apply_glitch(base_surface)
        
        # Draw the resulting game layer
        self.screen.blit(glitched, (0, 0))
        
        # Add overlays (Vignette, Scanlines)
        self.screen.blit(self.scanlines, (0, 0))
        self.screen.blit(self.vignette, (0, 0))
        
        # Transitions & Flashes over everything
        self.transitions.draw(self.screen)
        self.glitch.draw_flash(self.screen)

if __name__ == "__main__":
    game = MemorableGame()
    game.run()
