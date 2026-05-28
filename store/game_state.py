"""
MEMORABLE — GameState
Global mutable state. Hidden moral stats never shown to player directly.
"""

from constants import BASE_GLITCH


class GameState:
    """Single instance shared across all engines and screens."""

    def __init__(self):
        self.reset()

    def reset(self):
        # ── Hidden moral stats (0–5) ─────────────────────────────
        self.empathy      = 0   # compassion vs pragmatism
        self.resistance   = 0   # rebellion vs compliance
        self.mnemos_trust = 0   # belief in AI's good intent
        self.curiosity    = 0   # depth of truth-seeking
        self.trust_cipher = 0   # faith in human rebels

        # ── Scene tracking ───────────────────────────────────────
        self.current_scene  = 'scene_apartment_wake'
        self.visited        = set()
        self.choices_made   = {}   # "scene_id:choice_id" → choice_id
        self.chapter        = 1

        # ── Atmosphere ──────────────────────────────────────────
        self.glitch_intensity = BASE_GLITCH
        self.current_music    = None

        # ── Meta ────────────────────────────────────────────────
        self.ending    = None
        self.reached_ending = None
        self.play_time = 0.0     # cumulative seconds

    # ── Stat helpers ─────────────────────────────────────────────

    def apply_effects(self, effects: dict):
        """Apply a dict of {stat_name: delta} from a scene choice."""
        for stat, delta in effects.items():
            if hasattr(self, stat):
                old = getattr(self, stat)
                setattr(self, stat, max(0, min(5, old + delta)))

    def get_stats(self) -> dict:
        return {
            'empathy':      self.empathy,
            'resistance':   self.resistance,
            'mnemos_trust': self.mnemos_trust,
            'curiosity':    self.curiosity,
            'trust_cipher': self.trust_cipher,
        }

    def record_choice(self, scene_id: str, choice_id: str):
        key = f"{scene_id}:{choice_id}"
        self.choices_made[key] = choice_id

    def visit(self, scene_id: str):
        self.visited.add(scene_id)

    def tick(self, dt: float):
        self.play_time += dt
