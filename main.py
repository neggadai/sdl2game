import pygame
import random

pygame.init()


SCREEN_W, SCREEN_H = 900, 700
SCREEN = pygame.display.set_mode((SCREEN_W, SCREEN_H))
CLOCK = pygame.time.Clock()
FPS = 60

TILE = 32
MAP_TILES_X = 50
MAP_TILES_Y = 50

PLAYER_SPEED = 3.2
ENEMY_SPEED  = 1.42
ITEM_PICK_DIST = 40

# ----------------- ЗАГРУЗКА РЕСУРСОВ -----------------
def load_image(path):
    return pygame.image.load(path).convert_alpha()

def slice_sheet(img, cell_w, cell_h, scale=1.0):
    frames = []
    sw, sh = img.get_size()
    for y in range(0, sh, cell_h):
        for x in range(0, sw, cell_w):
            if x + cell_w > sw or y + cell_h > sh:
                continue
            frame = img.subsurface((x, y, cell_w, cell_h))
            if scale != 1.0:
                frame = pygame.transform.scale(frame, (int(cell_w*scale), int(cell_h*scale)))
            frames.append(frame)
    return frames

# ----------------- ФАЙЛЫ -----------------
PLAYER_IDLE_PATH   = "C:/profile/scripts/Game/assets/player_idle.png"
PLAYER_RUN_PATH    = "C:/profile/scripts/Game/assets/player_run.png"
PLAYER_ATTACK_PATH = "C:/profile/scripts/Game/assets/player_attack.png"
PLAYER_DEATH_PATH  = "C:/profile/scripts/Game/assets/player_death.png"
WOLF_SPRITESHEET   = "C:/profile/scripts/Game/assets/wolf_spritesheet.png"
TILESET_IMAGE      = "C:/profile/scripts/Game/assets/tileset.png"
#BOSS_SPRITESHEET = ""

# ----------------- ПРЕДМЕТЫ -----------------
def process_item_image(img, target_size):
    rect = img.get_bounding_rect()
    cropped = img.subsurface(rect).copy()
    scaled = pygame.transform.scale(cropped, (target_size, target_size))
    return scaled

ITEM_IMAGES = {
    "sword": process_item_image(load_image("C:/profile/scripts/Game/assets/sword.png"), TILE),
    "shield": process_item_image(load_image("C:/profile/scripts/Game/assets/shield.png"), TILE),
    "potion": process_item_image(load_image("C:/profile/scripts/Game/assets/potion.png"), TILE)
}


class Camera:
    def __init__(self, w, h):
        self.x = 0
        self.y = 0
        self.w = w
        self.h = h

    def update(self, target_rect):
        self.x = int(target_rect.centerx - SCREEN_W/2)
        self.y = int(target_rect.centery - SCREEN_H/2)
        self.x = max(0, min(self.x, MAP_TILES_X*TILE - SCREEN_W))
        self.y = max(0, min(self.y, MAP_TILES_Y*TILE - SCREEN_H))

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.PLAYER_FRAME_W = 96
        self.PLAYER_FRAME_H = 96
        self.SCALE = TILE / self.PLAYER_FRAME_W * 3

        self.anim_idle   = slice_sheet(load_image(PLAYER_IDLE_PATH),   self.PLAYER_FRAME_W, self.PLAYER_FRAME_H, self.SCALE)
        self.anim_run    = slice_sheet(load_image(PLAYER_RUN_PATH),    self.PLAYER_FRAME_W, self.PLAYER_FRAME_H, self.SCALE)
        self.anim_attack = slice_sheet(load_image(PLAYER_ATTACK_PATH), self.PLAYER_FRAME_W, self.PLAYER_FRAME_H, self.SCALE)
        self.anim_death  = slice_sheet(load_image(PLAYER_DEATH_PATH),  self.PLAYER_FRAME_W, self.PLAYER_FRAME_H, self.SCALE)

        self.kills = 0
        self.level = 1
        self.exp = 0
        self.exp_to_next = 100

        self.pos = pygame.Vector2(x, y)
        self.start_pos = pygame.Vector2(x, y)
        self.speed = PLAYER_SPEED
        self.health = 100
        self.max_health = 100
        self.inventory = []
        self.weapon = "none"

        self.attacking = False
        self.attack_cooldown = 0
        self.attack_damage = 15
        self.dead = False

        self.state = "idle"
        self.frame = 0
        self.animation_speed = 0.18

        self.direction = "right"
        self.attack_rect = pygame.Rect(0,0,40, self.PLAYER_FRAME_H)  

        self.image = self.anim_idle[0]
        self.rect = self.image.get_rect(center=(x, y))

    def update(self, dt, collision_check):
        if self.health <= 0 and not self.dead:
            self.dead = True
            self.frame = 0
            self.state = "death"

        if self.dead:
            self.animate()
            if self.frame >= len(self.anim_death)-1:
                self.dead = False
                self.health = self.max_health
                self.pos = self.start_pos.copy()
                self.state = "idle"
                self.frame = 0
            self.rect.center = self.pos
            return

        keys = pygame.key.get_pressed()
        dx = dy = 0
        if not self.attacking:
            if keys[pygame.K_w]: dy -= 1
            if keys[pygame.K_s]: dy += 1
            if keys[pygame.K_a]: dx -= 1
            if keys[pygame.K_d]: dx += 1

        if dx < 0: self.direction = "left"
        elif dx > 0: self.direction = "right"

        moving = (dx != 0 or dy != 0)
        self.state = "run" if moving else "idle"
        if self.attacking: self.state = "attack"

        vec = pygame.Vector2(dx, dy).normalize() if moving else pygame.Vector2(0, 0)
        new_pos = self.pos + vec * self.speed * dt

        if not collision_check(new_pos.x, self.pos.y, self.rect.width, self.rect.height):
            self.pos.x = new_pos.x
        if not collision_check(self.pos.x, new_pos.y, self.rect.width, self.rect.height):
            self.pos.y = new_pos.y

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        self.animate()

        if self.direction == "left":
            self.image = pygame.transform.flip(self.image, True, False)

        self.rect.center = self.pos


    def gain_exp(self, amount):
        self.exp += amount

        while self.exp >= self.exp_to_next:
            self.exp -= self.exp_to_next
            self.level += 1
            self.exp_to_next = int(self.exp_to_next * 1.4)

            self.max_health += 10
            self.health = self.max_health
            self.attack_damage += 2

    def start_attack(self):
        if self.attacking or self.attack_cooldown > 0 or self.weapon != "sword":
            return
        self.attacking = True
        self.state = "attack"
        self.frame = 0
        self.attack_cooldown = 20

        if self.direction == "right":
            self.attack_rect.topleft = (self.rect.right, self.rect.top)
        else:
            self.attack_rect.topright = (self.rect.left, self.rect.top)

        for w in wolves:
            if self.attack_rect.colliderect(w.rect):
                w.health -= self.attack_damage
                if w.health <= 0:
                    w.kill()
                    self.kills += 1
                    self.gain_exp(35)

    def animate(self):
        if self.state == "idle":
            frames = self.anim_idle
        elif self.state == "run":
            frames = self.anim_run
        elif self.state == "attack":
            frames = self.anim_attack
        elif self.state == "death":
            frames = self.anim_death

        self.frame += self.animation_speed

        if self.state == "attack" and self.frame >= len(frames):
            self.attacking = False
            self.state = "idle"
            self.frame = 0
        elif self.state == "death" and self.frame >= len(frames):
            self.frame = len(frames)-1
        elif self.frame >= len(frames):
            self.frame = 0

        self.image = frames[int(self.frame)]

class Wolf(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.WOLF_FRAME_W = 79
        self.WOLF_FRAME_H = 69
        self.SCALE = TILE / self.WOLF_FRAME_W * 3
        sheet = load_image(WOLF_SPRITESHEET)
        self.frames = slice_sheet(sheet, self.WOLF_FRAME_W, self.WOLF_FRAME_H, self.SCALE)
        self.frame_idx = 0.0
        self.anim_speed = 0.15

        self.pos = pygame.Vector2(x, y)
        self.speed = ENEMY_SPEED
        self.health = 30
        self.target = None
        self.alert_distance = 200
        self.attack_distance = 36
        self.attack_cd = 0

        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=(x, y))

    def update(self, dt, collision_check):
        if self.target:
            dirv = self.target.pos - self.pos
            dist = dirv.length()
            if dist < self.attack_distance:
                if self.attack_cd <= 0:
                    self.target.health -= 5
                    self.attack_cd = 35
                else:
                    self.attack_cd -= 1
            elif dist < self.alert_distance:
                dirv = dirv.normalize()
                np = self.pos + dirv * self.speed * dt
                
                if not collision_check(np.x, np.y, self.rect.width, self.rect.height):
                    self.pos = np
                self.animate()
        else:
            self.animate()
        self.rect.center = self.pos

    def animate(self):
        self.frame_idx += self.anim_speed
        if self.frame_idx >= len(self.frames):
            self.frame_idx = 0
        self.image = self.frames[int(self.frame_idx)]

map_data = [[random.randint(0, 3) for _ in range(MAP_TILES_X)] for __ in range(MAP_TILES_Y)]  # случайные тайлы

# ----------------- КОЛЛИЗИИ -----------------

def tile_is_block(x, y):
    if x<0 or y<0 or x>=MAP_TILES_X or y>=MAP_TILES_Y:
        return False
    return map_data[y][x] != 0

def collision_check(px, py, w, h):
    hw, hh = w/2, h/2
    corners = [
        (px-hw, py-hh),
        (px+hw, py-hh),
        (px-hw, py+hh),
        (px+hw, py+hh)
    ]
    for cx, cy in corners:
        tx = int(cx//TILE)
        ty = int(cy//TILE)
        if tile_is_block(tx, ty):
            return False
    return True
# ----------------- ИГРОК -----------------
player = Player(MAP_TILES_X*TILE//2, MAP_TILES_Y*TILE//2)
camera = Camera(MAP_TILES_X*TILE, MAP_TILES_Y*TILE)

# ----------------- ВРАГИ -----------------
wolves = pygame.sprite.Group()
for _ in range(8):
    wx = random.randint(2, MAP_TILES_X-3)*TILE + TILE//2
    wy = random.randint(2, MAP_TILES_Y-3)*TILE + TILE//2
    w = Wolf(wx, wy)
    w.target = player
    wolves.add(w)

# ----------------- ПРЕДМЕТЫ -----------------
items = []
for _ in range(5):
    for name in ["sword", "shield", "potion"]:
        ix = random.randint(2, MAP_TILES_X-3)*TILE + TILE//2
        iy = random.randint(2, MAP_TILES_Y-3)*TILE + TILE//2
        items.append({"name": name, "pos": pygame.Vector2(ix, iy)})

# ----------------- КАРТА -----------------
tileset_img = load_image(TILESET_IMAGE)
tiles = slice_sheet(tileset_img, TILE, TILE)

def draw_map(surface, cam):
    sx = max(0, cam.x//TILE)
    sy = max(0, cam.y//TILE)
    ex = min(MAP_TILES_X, (cam.x+SCREEN_W)//TILE+2)
    ey = min(MAP_TILES_Y, (cam.y+SCREEN_H)//TILE+2)
    for y in range(sy, ey):
        for x in range(sx, ex):
            tile = tiles[map_data[y][x] % len(tiles)]
            surface.blit(tile, (x*TILE - cam.x, y*TILE - cam.y))

def draw_exp_bar(surface, player):
    bar_w = 300
    bar_h = 18

    x = SCREEN_W//2 - bar_w//2
    y = 20

    pygame.draw.rect(surface, (40,40,40), (x,y,bar_w,bar_h))

    fill = (player.exp/player.exp_to_next) * bar_w
    pygame.draw.rect(surface, (0,200,0), (x,y,fill,bar_h))

    pygame.draw.rect(surface, (255,255,255), (x,y,bar_w,bar_h),2)

    txt = FONT.render(f"LVL {player.level}", True, (255,255,255))
    surface.blit(txt, (x + bar_w//2 - txt.get_width()//2, y-18))

# ----------------- ЦИКЛ -----------------
FONT = pygame.font.SysFont("Arial", 18)
running = True
while running:
    dt = CLOCK.tick(FPS) / (1000/60)

    for ev in pygame.event.get():
        if ev.type == pygame.QUIT: running = False
        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_1: player.weapon = "sword"
            if ev.key == pygame.K_2: player.weapon = "shield"
            if ev.key == pygame.K_0: player.weapon = "none"
            if ev.key == pygame.K_SPACE: player.start_attack()

    player.update(dt, collision_check)
    for w in wolves: w.update(dt, collision_check)
    camera.update(player.rect)

    for it in items[:]:
        if player.pos.distance_to(it["pos"]) < ITEM_PICK_DIST:
            player.inventory.append(it["name"])
            if it["name"] == "potion":
                player.health = min(player.max_health, player.health + 25)
            items.remove(it)

    SCREEN.fill((20,20,20))
    draw_map(SCREEN, camera)

    for it in items:
        img = ITEM_IMAGES[it["name"]]
        SCREEN.blit(img, (it["pos"].x - camera.x - img.get_width()//2,
                          it["pos"].y - camera.y - img.get_height()//2))

    for w in wolves:
        SCREEN.blit(w.image, (w.rect.left-camera.x, w.rect.top-camera.y))
    SCREEN.blit(player.image, (player.rect.left-camera.x, player.rect.top-camera.y))

    if player.attacking:
        rect = player.attack_rect.move(-camera.x, -camera.y)
        pygame.draw.rect(SCREEN, (255,0,0), rect, 2)

    SCREEN.blit(FONT.render(f"HP: {int(player.health)}", True, (255,255,255)), (10,10))
    SCREEN.blit(FONT.render(f"Weapon: {player.weapon}", True, (255,255,255)), (10,32))
    SCREEN.blit(FONT.render(f"Inv: {player.inventory}", True, (255,255,255)), (10,54))

    draw_exp_bar(SCREEN, player)
    SCREEN.blit(FONT.render(f"Kills: {player.kills}", True, (255,255,255)), (10,76))

    pygame.display.flip()

pygame.quit()
