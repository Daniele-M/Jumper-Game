 # Settings

# General settings.
TITLE = "Jumpy!"
WIDTH = 480
HEIGHT = 600
FPS = 60
FONT_NAME = 'arial'
HS_FILE = 'highscore.txt'
SPRITESHEET = 'spritesheet_jumper.png'

# Enviroment properties.
GRAVITY = 0.5
BG_COLOR = (51, 153, 255) # or 'lightblue'
MAX_DISTANCE_BETWEEN_PLATFORMS = 205

# Game properties.
BOOST_POWER = 25
SHIELD_TIME = 5000
BUNNY_TIME = 4000    # Min 1500
POW_SPAWN_PCT = 10   # Default 10
MOB_FREQ = 5000
PLAYER_LAYER = 3
PLATFORM_LAYER = 1
POW_LAYER = 2
MOB_LAYER = 3
CLOUD_LAYER = 0

# Player properties.
PLAYER_ACC = 0.5
PLAYER_FRICTION = -0.12
PLAYER_JUMP = 15

#Starting platforms.
PLATFORM_LIST = [(0, HEIGHT - 60),
                 (WIDTH / 2 - 50, HEIGHT * 3 / 4),
                 (125, HEIGHT - 350),
                 (350, 200),
                 (175, 100)
                 ]
