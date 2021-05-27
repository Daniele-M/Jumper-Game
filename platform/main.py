# Tutorial by KidsCanCode
# Platform game
# Art : Credit "Kenney.nl" or "www.kenney.nl"
# Happy tune by syncopika
# Yippee by Snabisch

import pygame as pg
import random
import os
from time import sleep

from settings import *
from sprites import *
from os import path

class Game:
    def __init__(self):
        """Initialize game window, etc."""
        pg.init()
        pg.mixer.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.running = True
        self.font_name = pg.font.match_font(FONT_NAME)
        self.load_data()


    def load_data(self):
        # Load high score
        self.dir = path.dirname(__file__)
        file = path.join(self.dir, HS_FILE)
        img_dir = path.join(self.dir, 'img')

        if not path.exists(file):
            with open(file, 'w'): pass
        with open(file, "r") as f:
            try:
                self.highscore = int(f.read())
            except:
                self.highscore = 0
        # Load spritesheet image
        self.spritesheet = Spritesheet(path.join(img_dir, SPRITESHEET))
        # Cloud images
        self.cloud_images = []
        for i in range(1, 4):
            self.cloud_images.append(pg.image.load(path.join(img_dir, f'cloud{i}.png')).convert())
        # Load sounds
        self.snd_dir = path.join(self.dir, 'snd')
        self.jump_sound = pg.mixer.Sound(path.join(self.snd_dir, 'jump_sound1.wav'))
        self.boost_sound = pg.mixer.Sound(path.join(self.snd_dir, 'Boost1.ogg'))
        self.s_up_sound = pg.mixer.Sound(path.join(self.snd_dir, 'shieldUp.ogg'))
        self.s_down_sound = pg.mixer.Sound(path.join(self.snd_dir, 'shieldDown.ogg'))
        self.jump_boost_sound = pg.mixer.Sound(path.join(self.snd_dir, 'bunny_sound.ogg'))
        self.alarm = pg.mixer.Sound(path.join(self.snd_dir, 'alarm_sound.wav'))


    def new(self):
        """Start a new game."""
        self.score = 0
        self.scroll = 0
        self.last_height = 0
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.platforms = pg.sprite.Group()
        self.powerups = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.clouds = pg.sprite.Group()
        self.player = Player(self)
        for plat in PLATFORM_LIST:
            Platform(self, *plat)
        self.mob_timer = 0
        pg.mixer.music.load(path.join(self.snd_dir, 'Happy Tune.ogg'))
        for i in range(8):
            c = Cloud(self)
            c.rect.y += 500

        self.run()


    def run(self):
        """Game loop."""
        pg.mixer.music.play(loops=-1)
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()
        pg.mixer.music.fadeout(500)


    def update(self):
        """Game loop - Update."""
        self.all_sprites.update()

        # Spawn a mob
        now = pg.time.get_ticks()
        if now - self.mob_timer > MOB_FREQ + random.choice([-1000, -500, 0, 500, 1000]):
            self.mob_timer = now
            Mob(self)
        # Mob collision
        mob_hits = pg.sprite.spritecollide(self.player, self.mobs, False, pg.sprite.collide_mask)
        if mob_hits:
            if self.player.is_shield == True:
                for mob in mob_hits:
                    mob.kill()
            else:
                for mob in mob_hits:
                    if mob.rect.right < 10 or mob.rect.left > WIDTH - 10:
                        pass
                    else:
                        self.playing = False

        # Check if player hits a platform only if falling
        if self.player.vel.y > 0:
            hits = pg.sprite.spritecollide(self.player, self.platforms, False)
            if hits:
                lowest = hits[0]
                for hit in hits:
                    if hit.rect.bottom > lowest.rect.centery:
                        lowest = hit
                if self.player.pos.x < lowest.rect.right + 10 and \
                    self.player.pos.x > lowest.rect.left - 10:
                    if self.player.pos.y < lowest.rect.bottom:
                        self.player.pos.y = lowest.rect.top + 1
                        self.player.vel.y = 0
                        self.player.jumping = False

        # If player reaches top 1/4 of screen
        if self.player.rect.top <= HEIGHT / 4:
            if random.randrange(100) < 10:
                Cloud(self)
            self.scroll += max(abs(self.player.vel.y), 2)
            self.player.pos.y += max(abs(self.player.vel.y), 2)
            for cloud in self.clouds:
                cloud.rect.y += max(abs(self.player.vel.y / cloud.speedy), 2)
            for mob in self.mobs:
                mob.rect.y += max(abs(self.player.vel.y), 2)
            for plat in self.platforms:
                plat.rect.y += max(abs(self.player.vel.y), 2)
                if plat.rect.top >= HEIGHT:
                    plat.kill()
                    self.score += 10

        # If player hits a powerup
        pow_hits = pg.sprite.spritecollide(self.player, self.powerups, True)
        for pow in pow_hits:
            if pow.type == 'boost':
                self.boost_sound.play()
                self.player.vel.y = - BOOST_POWER
                self.player.jumping = False
            if pow.type == 'shield':
                self.player.shield_time = pg.time.get_ticks()
                self.player.is_shield = True
                self.s_up_sound.play()
            if pow.type == 'bunny':
                self.player.jump_boost_time = pg.time.get_ticks()
                self.player.jump_boost = True
                self.player.boost_sound = True
                self.jump_boost_sound.play()


        # Die
        if self.player.rect.bottom > HEIGHT:
            for sprite in self.all_sprites:
                sprite.rect.y -= max(self.player.vel.y, 10)
                if sprite.rect.bottom < 10:
                    sprite.kill()
        if len(self.platforms) == 0:
            self.playing = False

        self.spawn_platforms()


    def events(self):
        """Game loop - Events."""
        for event in pg.event.get():
            if event.type == pg.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_UP:
                    self.player.jump()
            if event.type == pg.KEYUP:
                if event.key == pg.K_UP:
                    self.player.jump_cut()


    def draw(self):
        """Game loop - Draw."""
        self.screen.fill(BG_COLOR)
        self.all_sprites.draw(self.screen)
        if self.player.is_shield == True:
            self.screen.blit(self.player.shield_icon, self.player.shield_rect)
        self.draw_text(str(self.score), 22, 'white', WIDTH / 2, 15)
        pg.display.flip()


    def show_start_screen(self):
        """Game splash/start screen."""
        pg.mixer.music.set_volume(0.5)
        pg.mixer.music.load(path.join(self.snd_dir, 'Yippee.ogg'))
        pg.mixer.music.play(loops=-1)


        self.screen.fill(BG_COLOR)
        self.draw_text(TITLE, 48, 'white', WIDTH / 2, HEIGHT / 4)
        self.draw_text("Arrows to move, arrow up to jump",
            22, 'white', WIDTH / 2, HEIGHT / 2)
        self.draw_text("Press a key to play", 22, 'white', WIDTH / 2, HEIGHT * 3 / 4)
        self.draw_text("High score : " + str(self.highscore), 22, 'white', WIDTH / 2, 15)
        pg.display.flip()
        self.wait_for_key()

        pg.mixer.music.fadeout(500)
        sleep(0.5)
        pg.mixer.music.set_volume(1.0)


    def show_go_screen(self):
        """Game over."""
        if not self.running:
            return
        self.screen.fill(BG_COLOR)
        self.draw_text("GAME OVER", 48, 'white', WIDTH / 2, HEIGHT / 4)
        self.draw_text("Score: " + str(self.score),
            22, 'white', WIDTH / 2, HEIGHT / 2)
        self.draw_text("Press a key to play again", 22, 'white', WIDTH / 2, HEIGHT * 3 / 4)
        if self.score > self.highscore:
            self.highscore = self.score
            self.draw_text("New Highscore!", 22, 'white', WIDTH / 2, HEIGHT / 2 + 40)
            with open(path.join(self.dir, HS_FILE), 'w') as f:
                f.write(str(self.score))
        else:
            self.draw_text("Highscore: " + str(self.highscore), 22, 'white', WIDTH / 2, HEIGHT / 2 + 40)

        pg.display.flip()
        self.wait_for_key()


    def draw_text(self, text, size, color, x, y):
        font = pg.font.Font(self.font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)


    def wait_for_key(self):
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.running = False
                if event.type == pg.KEYUP:
                    waiting = False


    def spawn_platforms(self):
        # Spawn new platforms
        i = 0
        while len(self.platforms) < 6:
            width = random.randrange(50, 150)
            height =  random.randrange(-75, -30)
            while self.last_height + self.scroll - height > MAX_DISTANCE_BETWEEN_PLATFORMS:
                if i > 100:
                    height = 0
                    break
                height = random.randrange(-75, -30)
                i += 1
            Platform(self, random.randrange(0, WIDTH - width), height)
            self.last_height = height
            self.scroll = 0



g = Game()
g.show_start_screen()
while g.running:
    g.new()
    g.show_go_screen()


os.sys.exit(0)
