# Sprite classes for platform game
import pygame as pg
from pygame.sprite import Sprite
vec = pg.math.Vector2
from random import choice, randrange, uniform

from settings import *


class Spritesheet:
    #Utility class for loading and parsing spritesheets
    def __init__(self, filename):
        self.spritesheet = pg.image.load(filename).convert()

    def get_image(self, x, y, width, height):
        #Grab an image out of a larger spritesheet
        image = pg.Surface((width, height))
        image.blit(self.spritesheet, (0, 0), (x, y, width, height))
        image = pg.transform.scale(image, (width // 3, height // 3))
        return image

class Player(Sprite):
    def __init__(self, game):
        self._layer = PLAYER_LAYER
        self.groups = game.all_sprites
        super().__init__(self.groups)
        self.game = game
        self.walking = False
        self.jumping = False
        self.current_frame = 0
        self.last_update = 0
        self.load_images()
        self.image = self.standing_frames[0]
        self.rect = self.image.get_rect()
        self.rect.center = (40, HEIGHT - 100)
        self.pos = vec(40, HEIGHT - 100)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.shield_rect = self.shield_icon.get_rect()
        self.shield_rect.center = (40, HEIGHT - 100)

        self.is_shield = False
        self.shield_time = pg.time.get_ticks()
        self.jump_boost = False
        self.boost_sound = False
        self.jump_boost_time = pg.time.get_ticks()



    def load_images(self):
        self.standing_frames = [self.game.spritesheet.get_image(614, 1063, 120, 191),
            self.game.spritesheet.get_image(690, 406, 120, 201)]
        for frame in self.standing_frames:
            frame.set_colorkey('black')

        self.walk_frames_r = [self.game.spritesheet.get_image(678, 860, 120, 201),
            self.game.spritesheet.get_image(692, 1458, 120, 207)]
        for frame in self.walk_frames_r:
            frame.set_colorkey('black')

        self.walk_frames_l = []
        for frame in self.walk_frames_r:
            self.walk_frames_l.append(pg.transform.flip(frame, True, False))

        self.jump_frame = self.game.spritesheet.get_image(382, 763, 150, 181)
        self.jump_frame.set_colorkey('black')

        self.shield_icon = self.game.spritesheet.get_image(0, 1662, 211, 215)
        self.shield_icon.set_colorkey('black')


    def jump(self):
        # Jump only if standing on platforms.
        self.rect.y += 2
        hits = pg.sprite.spritecollide(self, self.game.platforms, False)
        self.rect.y -= 2
        if (hits and not self.jumping) or self.jump_boost:
            self.game.jump_sound.play()
            self.jumping = True
            self.vel.y = -PLAYER_JUMP


    def jump_cut(self):
        if self.jumping:
            if self.vel.y < -5:
                self.vel.y = -5


    def update(self):
        # Powerups check.
        self.shield()
        self.bunny()

        # Moving animation.
        self.animate()

        self.acc = vec(0, GRAVITY)
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT]:
            self.acc.x = -PLAYER_ACC
        if keys[pg.K_RIGHT]:
            self.acc.x = PLAYER_ACC

        # Apply friction.
        self.acc.x += self.vel.x * PLAYER_FRICTION
        # Equations of motion.
        self.vel += self.acc
        if abs(self.vel.x) < 0.1:
            self.vel.x = 0
        self.pos += self.vel + 0.5 * self.acc

        # Wrap around the sides of the screen.
        if self.pos.x > WIDTH + self.rect.width / 2:
            self.pos.x = 0 - self.rect.width / 2
        if self.pos.x < 0 - self.rect.width / 2:
            self.pos.x = WIDTH + self.rect.width / 2

        self.rect.midbottom = self.pos


    def animate(self):
        now = pg.time.get_ticks()
        if self.vel.x != 0:
            self.walking = True
        else:
            self.walking = False

        # Show jump animation
        if self.jumping:
            self.image = self.jump_frame

        # Show walk animation
        elif self.walking:
            if now - self.last_update > 200:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.walk_frames_l)
                bottom = self.rect.bottom
                if self.vel.x > 0:
                    self.image = self.walk_frames_r[self.current_frame]
                else:
                    self.image = self.walk_frames_l[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom

        # Show idle animation
        if not self.jumping and not self.walking:
            if now - self.last_update > 400:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.standing_frames)
                bottom = self.rect.bottom
                self.image = self.standing_frames[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom
        # Mask for pixel perfect collision
        self.mask = pg.mask.from_surface(self.image)


    def shield(self):
        if pg.time.get_ticks() - self.shield_time  > SHIELD_TIME and self.is_shield:
            self.is_shield = False
            self.game.s_down_sound.play()
        self.shield_rect.center = self.rect.center


    def bunny(self):
        if self.jump_boost:
            if pg.time.get_ticks() - self.jump_boost_time  > BUNNY_TIME - BUNNY_TIME / 3 and self.boost_sound:
               self.game.alarm.play(loops=3)
               self.boost_sound = False
            if pg.time.get_ticks() - self.jump_boost_time  > BUNNY_TIME:
                self.jump_boost = False




class Platform(Sprite):
    def __init__(self, game, x, y):
        self._layer = PLATFORM_LAYER
        self.groups = game.all_sprites, game.platforms
        super().__init__(self.groups)
        self.game = game
        images = [self.game.spritesheet.get_image(0, 288, 380, 94),
            self.game.spritesheet.get_image(213, 1662, 201, 100)
        ]
        self.image = choice(images)
        self.image.set_colorkey('black')
        self.rect  = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        if randrange(100) < POW_SPAWN_PCT:
            Pow(self.game, self)

class Pow(Sprite):
    def __init__(self, game, plat):
        self._layer = POW_LAYER
        self.groups = game.all_sprites, game.powerups
        super().__init__(self.groups)
        self.game = game
        self.plat = plat
        self.type = choice(['boost', 'shield', 'bunny'])
        if self.type == 'boost':
            self.image = self.game.spritesheet.get_image(820, 1805, 71, 70)
        elif self.type == 'shield':
            self.image = self.game.spritesheet.get_image(894, 1661, 71, 70)
        elif self.type == 'bunny':
            self.image = self.game.spritesheet.get_image(826, 1220, 71, 70)
        self.image.set_colorkey('black')
        self.rect  = self.image.get_rect()
        self.rect.centerx = self.plat.rect.centerx
        self.rect.bottom = self.plat.rect.top - 5

    def update(self):
        self.rect.bottom = self.plat.rect.top - 5
        if not self.game.platforms.has(self.plat):
            self.kill()


class Mob(Sprite):
    def __init__(self, game):
        self._layer = MOB_LAYER
        self.groups = game.all_sprites, game.mobs
        super().__init__(self.groups)
        self.game = game
        self.image_up = self.game.spritesheet.get_image(566, 510, 122, 139)
        self.image_up.set_colorkey('black')
        self.image_down = self.game.spritesheet.get_image(568, 1534, 122, 135)
        self.image_down.set_colorkey('black')
        self.image = self.image_up
        self.rect = self.image.get_rect()
        self.rect.centerx = choice([-100, WIDTH + 100])
        self.vx = randrange(1, 3)
        if self.rect.centerx > WIDTH:
            self.vx *= -1
        self.rect.y = randrange(HEIGHT / 2)
        self.vy = 0
        self.dy = 0.5

    def update(self):
        self.rect.x += self.vx
        self.vy += self.dy
        if self.vy > 3 or self.vy < -3:
            self.dy *= -1

        center = self.rect.center
        if self.dy < 0:
            self.image = self.image_up
        else:
            self.image = self.image_down
        self.rect = self.image.get_rect()
        # Mask for pixel perfect collision
        self.mask = pg.mask.from_surface(self.image)
        self.rect.center = center
        self.rect.y += self.vy

        if self.rect.left > WIDTH + 100 or self.rect.right < -100:
            self.kill()


class Cloud(Sprite):
    def __init__(self, game):
        self._layer = CLOUD_LAYER
        self.groups = game.all_sprites, game.clouds
        super().__init__(self.groups)
        self.game = game
        self.image = choice(self.game.cloud_images)
        self.image.set_colorkey('black')
        self.rect = self.image.get_rect()
        scale = randrange(50, 101) / 100
        self.image = pg.transform.scale(self.image, (int(self.rect.width * scale),
            int(self.rect.height * scale)))
        self.rect.x = randrange(WIDTH - self.rect.width)
        self.rect.y = randrange(-500, -50)
        self.x = float(self.rect.x)
        self.vx = uniform(0.5, 1)
        self.speedy = randrange(2, 4)


    def update(self):
        self.x += self.vx
        self.rect.x = self.x

        if self.rect.left > WIDTH:
            self.rect.right = -50

        if self.rect.top > HEIGHT * 2:
            self.kill()
