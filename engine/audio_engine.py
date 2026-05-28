"""
MEMORABLE — Audio Engine
Pygame mixer wrapper for music, SFX, and crossfading.
"""

import os
import pygame
from constants import MUSIC_VOL, SFX_VOL

class AudioEngine:
    def __init__(self):
        self.enabled = True
        try:
            pygame.mixer.init()
            pygame.mixer.set_num_channels(8)
            # Channel 0 reserved for SFX like typing
            # Channel 1 reserved for suspense/glitch bursts
        except Exception as e:
            print(f"[AudioEngine] Mixer init failed: {e}")
            self.enabled = False

        self.current_music = None
        
        self.tracks = {
            'ambient_cyberpunk': 'music/ambient_cyberpunk.mp3',
            'emotional_piano':   'music/emotional_piano.mp3',
            'tension_soundtrack': 'music/tension_soundtrack.mp3',
            'final_choice_music': 'music/final_choice_music.mp3',
        }
        
        self.sfx = {
            'click':    'sounds/click_sound.mp3',
            'confirm':  'sounds/decision_confirm_sound.wav',
            'glitch':   'sounds/glitch_sound.wav',
            'suspense': 'sounds/suspense_hit.wav',
            'typing':   'sounds/typing_sound2.wav',
        }
        
        self._sfx_cache = {}

    def _load_sfx(self, key: str):
        if key in self._sfx_cache:
            return self._sfx_cache[key]
        path = self.sfx.get(key)
        if not path or not os.path.exists(path):
            return None
        try:
            sound = pygame.mixer.Sound(path)
            self._sfx_cache[key] = sound
            return sound
        except Exception as e:
            self._sfx_cache[key] = None
            return None

    def play_music(self, key: str, fade_ms: int = 1500, loop: bool = True):
        if not self.enabled or key == self.current_music:
            return
        path = self.tracks.get(key)
        if not path or not os.path.exists(path):
            print(f"[AudioEngine] Missing music track: {key} at {path}")
            return
            
        try:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.fadeout(fade_ms)
                # We can't block here easily without freezing the game, 
                # so we just load and play. Pygame mixer queueing handles it gracefully.
            
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(MUSIC_VOL)
            loops = -1 if loop else 0
            pygame.mixer.music.play(loops=loops, fade_ms=fade_ms)
            self.current_music = key
        except Exception as e:
            print(f"[AudioEngine] Play music failed: {e}")

    def play_sfx(self, key: str, volume: float = 1.0, channel: int = -1, loops: int = 0):
        if not self.enabled:
            return
        sound = self._load_sfx(key)
        if sound:
            sound.set_volume(SFX_VOL * volume)
            if channel >= 0:
                pygame.mixer.Channel(channel).play(sound, loops=loops)
            else:
                sound.play(loops=loops)
                
    def stop_channel(self, channel: int):
        if not self.enabled:
            return
        pygame.mixer.Channel(channel).stop()

    def pause_channel(self, channel: int):
        if not self.enabled:
            return
        pygame.mixer.Channel(channel).pause()

    def unpause_channel(self, channel: int):
        if not self.enabled:
            return
        pygame.mixer.Channel(channel).unpause()

    def set_glitch_degradation(self, intensity: float):
        if not self.enabled:
            return
        # Lower music volume slightly based on glitch intensity
        vol = MUSIC_VOL * (1.0 - (intensity * 0.4))
        pygame.mixer.music.set_volume(max(0.0, vol))

    def fade_out_all(self, fade_ms: int = 2000):
        if not self.enabled:
            return
        pygame.mixer.music.fadeout(fade_ms)
        self.current_music = None
