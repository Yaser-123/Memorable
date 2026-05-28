"""
MEMORABLE — Game Scene
Main gameplay loop: renders backgrounds, characters, dialogue, choices.
Integrates heavily with AI engine and GameState.
"""

import pygame
from store.game_state import GameState
from engine.audio_engine import AudioEngine
from engine.glitch_engine import GlitchEngine
from engine.transition_engine import TransitionEngine
from engine.dialogue_engine import DialogueEngine
from engine.ai_engine import call_mnemos
from utils import load_image, load_portrait, draw_text_wrapped, alpha_surface
from constants import (
    SCREEN_W, SCREEN_H, VOID, CYAN, TEXT, MUTED,
    CHOICE_W, CHOICE_ROW_H, CHOICE_HEADER, PANEL_BG, PORTRAIT_H, PORTRAIT_MARGIN
)

class GameScene:
    def __init__(self, fonts, audio, glitch, transitions, scenes, characters):
        self.fonts = fonts
        self.audio = audio
        self.glitch = glitch
        self.transitions = transitions
        self.scenes = scenes
        self.characters = characters
        
        self.state = GameState()
        self.dialogue = DialogueEngine(audio, fonts)
        
        self.current_scene = None
        self.dialogue_index = 0
        self.bg_image = None
        self.portrait_img = None
        self.waiting_for_ai = False
        
        self.show_choices = False
        self.choices = []
        self.hovered_choice = -1

    def enter(self, scene_id: str):
        self.state.visit(scene_id)
        self.state.current_scene = scene_id
        
        scene = self.scenes.get(scene_id)
        if not scene:
            print(f"[GameScene] Scene {scene_id} not found!")
            self.current_scene = None
            return
            
        self.current_scene = scene
        self.show_choices = False
        self.hovered_choice = -1
        self.dialogue_index = 0
        
        # Audio
        music = scene.get('music')
        if music:
            self.audio.play_music(music)
            self.state.current_music = music
            
        # Background
        bg_path = scene.get('background', '')
        if bg_path:
            # Check if it has extension, otherwise add .png
            if not bg_path.endswith('.png'):
                bg_path += '.png'
            self.bg_image = load_image(f"background/{bg_path}", (SCREEN_W, SCREEN_H), alpha=False)
            
        # Glitch intensity update
        if 'glitch_level' in scene:
            self.state.glitch_intensity = scene['glitch_level']
            
        self._load_current_dialogue()

    def _load_current_dialogue(self):
        dialogue_list = self.current_scene.get('dialogue', [])
        if self.dialogue_index >= len(dialogue_list):
            return
            
        d = dialogue_list[self.dialogue_index]
        
        # Effects
        if d.get('glitch_burst'):
            self.glitch.trigger_burst(0.5, 0.8)
            
        # SFX
        sfx = d.get('sfx')
        if sfx:
            self.audio.play_sfx(sfx)
            
        # Portrait
        char_id = d.get('character', '')
        if char_id and char_id in self.characters:
            char_data = self.characters[char_id]
            # Try to get portraitKey, fallback to char_id if missing
            pkey = char_data.get('portraitKey', char_id)
            if pkey:
                portrait_map = {
                    'protagonist': 'portraits/Protogonist.png',
                    'scientist': 'portraits/The_Scientist.png',
                    'mnemos': 'portraits/AI_entity.png',
                    'cipher': 'portraits/Lost_Sister_Friend.png',
                    'sister': 'portraits/Lost_Sister_Friend.png',
                    'rebel_leader': 'portraits/Lost_Sister_Friend.png',
                }
                path = portrait_map.get(pkey, f"portraits/{pkey}.png")
                self.portrait_img = load_portrait(path, PORTRAIT_H)
            else:
                self.portrait_img = None
            display_name = char_data.get('displayName', char_id.upper())
        else:
            self.portrait_img = None
            display_name = char_id.upper() if char_id != 'narrator' else ''
            
        text = d.get('text', '')
        emotion = d.get('emotion', 'neutral')
        
        # Is it MNEMOS dynamic AI generation?
        if d.get('ai_generate'):
            self.waiting_for_ai = True
            self.dialogue.start("SYSTEM", "INITIALIZING MNEMOS UPLINK...", "system")
            call_mnemos(self.state.current_scene, self.state.get_stats(), text, self._on_ai_response)
        else:
            self.dialogue.start(display_name, text, emotion)

    def _on_ai_response(self, text: str):
        self.waiting_for_ai = False
        self.dialogue.start("MNEMOS", text, "mnemos")

    def handle_click(self, pos: tuple):
        if self.waiting_for_ai:
            return
            
        if not self.dialogue.is_done:
            self.dialogue.skip()
            return
            
        if not self.show_choices:
            # Are there more dialogue lines?
            dialogue_list = self.current_scene.get('dialogue', [])
            if self.dialogue_index < len(dialogue_list) - 1:
                self.dialogue_index += 1
                self._load_current_dialogue()
                return
            
            # End of dialogue. Show choices or auto-advance
            self.choices = self.current_scene.get('choices', [])
            if self.choices:
                self.show_choices = True
                return
            else:
                # No choices, check next_scene
                next_scene = self.current_scene.get('next_scene')
                if next_scene:
                    trans = self.current_scene.get('transition_out', 'fade_black')
                    self.transitions.start(trans, 1.5, lambda: self.enter(next_scene))
                return
            
        # Handle choice click
        if self.show_choices and self.hovered_choice >= 0:
            choice = self.choices[self.hovered_choice]
            
            sfx = choice.get('sfx', 'confirm')
            self.audio.play_sfx(sfx, volume=0.7)
            
            if choice.get('glitch_trigger'):
                self.glitch.trigger_burst(0.6, 0.9)
            
            # Apply stats
            if 'stat_effects' in choice:
                self.state.apply_effects(choice['stat_effects'])
                
            self.state.record_choice(self.state.current_scene, choice.get('id', 'default'))
            
            if choice.get('is_ending'):
                self.state.reached_ending = choice.get('ending_id')
                return
                
            next_scene = choice.get('next_scene')
            if not next_scene:
                return # End of game
                
            trans = choice.get('transition_out', 'fade_black')
            self.transitions.start(trans, 1.5, lambda: self.enter(next_scene))

    def update(self, dt: float, mouse_pos: tuple):
        self.dialogue.update(dt)
        
        if self.show_choices and self.choices:
            cx = SCREEN_W // 2 - CHOICE_W // 2
            cy_start = SCREEN_H // 2 - (len(self.choices) * CHOICE_ROW_H) // 2 + CHOICE_HEADER
            
            self.hovered_choice = -1
            for i in range(len(self.choices)):
                rect = pygame.Rect(cx, cy_start + i * CHOICE_ROW_H, CHOICE_W, CHOICE_ROW_H - 10)
                if rect.collidepoint(mouse_pos):
                    self.hovered_choice = i
                    break

    def draw(self, surface: pygame.Surface):
        if self.bg_image:
            surface.blit(self.bg_image, (0, 0))
        else:
            surface.fill(VOID)
            
        if self.portrait_img:
            px = SCREEN_W - self.portrait_img.get_width() - PORTRAIT_MARGIN
            py = SCREEN_H - self.portrait_img.get_height() - 200
            surface.blit(self.portrait_img, (px, py))
            
        if self.show_choices and self.choices:
            overlay = alpha_surface((0, 0, 0), (SCREEN_W, SCREEN_H), 180)
            surface.blit(overlay, (0, 0))
            
            cx = SCREEN_W // 2 - CHOICE_W // 2
            cy_start = SCREEN_H // 2 - (len(self.choices) * CHOICE_ROW_H) // 2
            
            prompt_surf = self.fonts['subtitle'].render("MAKE YOUR CHOICE", True, CYAN)
            surface.blit(prompt_surf, (SCREEN_W//2 - prompt_surf.get_width()//2, cy_start - 30))
            
            for i, choice in enumerate(self.choices):
                y = cy_start + CHOICE_HEADER + i * CHOICE_ROW_H
                rect = pygame.Rect(cx, y, CHOICE_W, CHOICE_ROW_H - 10)
                
                is_hover = (i == self.hovered_choice)
                bg_color = (30, 35, 50, 240) if is_hover else (*PANEL_BG, 200)
                text_color = CYAN if is_hover else TEXT
                
                panel = alpha_surface(bg_color[:3], (rect.w, rect.h), bg_color[3])
                if is_hover:
                    pygame.draw.rect(panel, CYAN, panel.get_rect(), 2)
                surface.blit(panel, rect.topleft)
                
                text_surf = self.fonts['body'].render(choice.get('text', ''), True, text_color)
                surface.blit(text_surf, (cx + 20, y + (rect.h - text_surf.get_height()) // 2))

        if not self.show_choices:
            self.dialogue.draw(surface)
