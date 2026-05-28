"""
MEMORABLE — Global constants.
Colors, dimensions, timing.
"""

# ── Screen ──────────────────────────────────────────────────────
SCREEN_W = 1280
SCREEN_H = 720
FPS      = 60

# ── Palette ─────────────────────────────────────────────────────
VOID      = (10,  10,  15)
ABYSS     = (13,  27,  62)
DEEP      = (8,   8,   20)
CYAN      = (0,   245, 228)
CYAN_DIM  = (0,   180, 168)
VIOLET    = (155, 93,  229)
RED_GLOW  = (255, 51,  102)
WHITE     = (255, 255, 255)
TEXT      = (232, 232, 236)
TEXT_DIM  = (138, 138, 154)
MUTED     = (74,  74,  90)
PANEL_BG  = (10,  12,  30)

# ── Dialogue box layout ──────────────────────────────────────────
DLGBOX_X  = 20
DLGBOX_Y  = SCREEN_H - 215
DLGBOX_W  = SCREEN_W - 40
DLGBOX_H  = 200

DLGTXT_X  = DLGBOX_X + 60
DLGTXT_Y  = DLGBOX_Y + 52
DLGTXT_W  = DLGBOX_W - 120

SPEAKER_X = DLGBOX_X + 60
SPEAKER_Y = DLGBOX_Y + 16

# ── Portrait dimensions ──────────────────────────────────────────
PORTRAIT_H     = 480
PORTRAIT_MARGIN = 10

# ── Choice panel ─────────────────────────────────────────────────
CHOICE_W       = 740
CHOICE_ROW_H   = 78
CHOICE_HEADER  = 52

# ── Audio defaults ───────────────────────────────────────────────
MUSIC_VOL = 0.55
SFX_VOL   = 0.80
FADE_MS   = 1800

# ── Glitch defaults ──────────────────────────────────────────────
BASE_GLITCH = 0.05
