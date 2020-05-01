import pygame as pg
from pygame.math import Vector2
from pygame import mixer

pg.init()
font = pg.font.SysFont('Times new roman', 32)

mixer.music.load("background.mp3")
mixer.music.play(-1)

class Player(pg.sprite.Sprite):
    
    def __init__(self, pos, imagecur, left, right, up, down, fire, all_sprites, bullets, enemy_bullets, scorecoor):
        super().__init__()
        self.image = imagecur
        self.scorecoor = scorecoor
        self.rect = self.image.get_rect(topleft=pos)
        self.vel = Vector2(0, 0)
        self.pos = Vector2(self.rect.topleft)
        self.dt = 0.03
        self.angle = 0
        self.key_left = left
        self.key_right = right
        self.key_up = up
        self.key_down = down
        self.key_fire = fire

        # Store the groups as attributes, so that you can add bullets
        # and use them for the collision detection in the update method.
        
        self.all_sprites = all_sprites
        self.bullets = bullets
        self.enemy_bullets = enemy_bullets
        self.fire_direction = Vector2(350, 0)
        self.health = 3
    
    def update(self, dt):
        self.dt = dt
        self.pos += self.vel
        if self.pos.x <= 0:
            self.pos.x = 800
        if self.pos.x > 800:
            self.pos.x = 800 - self.pos.x + self.dt
        if self.pos.y <= 0:
            self.pos.y = 600
        if self.pos.y > 600:
            self.pos.y = 600 - self.pos.y + self.dt
        self.rect.center = self.pos
        
        # Check if enemy bullets collide with the player, reduce
        # health and kill self if health is <= 0.
        
        collided_bullets = pg.sprite.spritecollide(self, self.enemy_bullets, True)
        for bullet in collided_bullets:
            self.health -= 1
            if self.health <= 0:
                explosionSound = mixer.Sound("explosion.wav")
                explosionSound.play()
                self.kill()
    
    def printscore(self, screen):
        if self.health > 0:
            hp = font.render('H P:' + str(self.health), True, (255, 123, 100))
            screen.blit(hp, (self.scorecoor, self.scorecoor))
        else:
            text = font.render('L  O  S  E  R', True, (255, 123, 100))
            screen.blit(text, self.scorecoor)
    
    def handle_event(self, event):
        if event.type == pg.KEYDOWN:
 
            if event.key == self.key_left:
                self.image = pg.transform.rotate(self.image, 90 - self.angle)
                self.angle = 90
                self.vel.x = -90 * self.dt
                self.vel.y = 0
                self.fire_direction = Vector2(-350, 0)
 
            elif event.key == self.key_right:
                self.image = pg.transform.rotate(self.image, 270 - self.angle)
                self.angle = 270
                self.vel.x = 90 * self.dt
                self.vel.y = 0
                self.fire_direction = Vector2(350, 0)
 
            elif event.key == self.key_up:
                self.image = pg.transform.rotate(self.image, 0 - self.angle)
                self.angle = 0
                self.vel.y = -90 * self.dt
                self.vel.x = 0
                self.fire_direction = Vector2(0, -350)
 
            elif event.key == self.key_down:
                self.image = pg.transform.rotate(self.image, 180 - self.angle)
                self.angle = 180
                self.vel.y = 90 * self.dt
                self.vel.x = 0
                self.fire_direction = Vector2(0, 350)
 
            elif event.key == self.key_fire:  # Add a bullet to the groups.
                bullet = Bullet(self.rect.center, self.fire_direction, self.angle)
                bulletSound = mixer.Sound("fire.wav")
                bulletSound.play()
                self.bullets.add(bullet)
                self.all_sprites.add(bullet)

        elif event.type == pg.KEYUP:
            if event.key == self.key_left and self.vel.x < 0:
                self.vel.x = 0
            elif event.key == self.key_right and self.vel.x > 0:
                self.vel.x = 0
            elif event.key == self.key_up and self.vel.y < 0:
                self.vel.y = 0
            elif event.key == self.key_down and self.vel.y > 0:
                self.vel.y = 0

class Bullet(pg.sprite.Sprite):
    def __init__(self, pos, velocity, angle):
        super().__init__()
        self.image = pg.Surface((7, 7))
        self.image.fill(pg.Color('black'))
        # self.image.fill(pg.Color('aquamarine1'))
        self.rect = self.image.get_rect(center=pos)
        self.pos = pos
        self.flytime = 100
        self.fly = 0
        self.vel = velocity

    def update(self, dt):
        if self.fly >= 40:
            self.kill()
            self.rect.center = self.pos
        else:
            self.pos += self.vel * dt
            if self.pos.x <= 0:
                self.pos.x = 800
            if self.pos.x > 800:
                self.pos.x = 800 - self.pos.x + dt
            if self.pos.y <= 0:
                self.pos.y = 600
            if self.pos.y > 600:
                self.pos.y = 600 - self.pos.y + dt
            self.rect.center = self.pos
            self.fly += 1

class Game:
    def __init__(self):
        self.fps = 30
        self.done = False
        self.clock = pg.time.Clock()
        self.screen = pg.display.set_mode((800, 600))
        self.bg_color = pg.Color('white')
        # Sprite groups that contain the players and bullets.
        self.all_sprites = pg.sprite.Group()
        self.bullets1 = pg.sprite.Group()  # Will contain bullets of player1.
        self.bullets2 = pg.sprite.Group()  # Will contain bullets of player2.
        player1 = Player(
            (100, 300), pg.image.load("tank1.png"),
            pg.K_a, pg.K_d, pg.K_w, pg.K_s, pg.K_f,
            self.all_sprites, self.bullets1, self.bullets2, (10,10))  # Pass the groups.
        player2 = Player(
            (300, 400), pg.image.load("tank2.png"),
            pg.K_LEFT, pg.K_RIGHT, pg.K_UP, pg.K_DOWN, pg.K_SPACE,
            self.all_sprites, self.bullets2, self.bullets1, (600,10))  # Pass the groups.
        self.all_sprites.add(player1, player2)
        self.players = pg.sprite.Group(player1, player2)
 
    def run(self):
        while not self.done:
            self.dt = self.clock.tick(self.fps) / 1000
            self.handle_events()
            self.run_logic()
            self.draw()
  
    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.done = True
            for player in self.players:
                player.handle_event(event)
  
    def run_logic(self):
        self.all_sprites.update(self.dt)
  
    def draw(self):
        self.screen.fill(self.bg_color)
        self.all_sprites.draw(self.screen)
        for player in self.players:
            player.printscore(self.screen)
        pg.display.flip()

if __name__ == '__main__':
    pg.init()
    Game().run()
    pg.quit()
