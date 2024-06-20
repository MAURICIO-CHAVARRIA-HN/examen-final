import pygame
import random
import button
from pygame import mixer
import moviepy.editor as mpy

# Inicialización de Pygame y del mezclador de sonido
mixer.init()
mixer.music.load('mp3/msc.mp3')
mixer.music.play(-1)  # Reproducir la música en bucle
pygame.init()

clock = pygame.time.Clock()
fps = 120

# Ventana del juego
bottom_panel = 150
screen_width = 800
screen_height = 400 + bottom_panel

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Batalla medieval')

# Variables del juego
current_fighter = 1
total_fighters = 3
action_cooldown = 0
action_wait_time = 90
attack = False
potion = False
potion_effect = 15
clicked = False
game_over = 0
state = 'menu'  # Estado inicial del juego

# Fuente del juego
font = pygame.font.SysFont('cambria', 26)

# Colores
red = (255, 0, 0)
green = (0, 255, 0)

# Carga de imágenes
background_img = pygame.image.load('img/Background/background.png').convert_alpha()
panel_img = pygame.image.load('img/Icons/panel.png').convert_alpha()
potion_img = pygame.image.load('img/Icons/potion.png').convert_alpha()
restart_img = pygame.image.load('img/Icons/restart.png').convert_alpha()
victory_img = pygame.image.load('img/Icons/victory.png').convert_alpha()
defeat_img = pygame.image.load('img/Icons/defeat.png').convert_alpha()
sword_img = pygame.image.load('img/Icons/sword.png').convert_alpha()

# Cargar la imagen de fondo del menú
menu_background_img = pygame.image.load('img/Background/menufondo.jpg').convert_alpha()

# Redimensionar la imagen de fondo del menú
menu_background_img = pygame.transform.scale(menu_background_img, (screen_width, screen_height))

# Carga de sonidos
victory_fx = pygame.mixer.Sound('mp3/victoria.mp3')  # Cargar sonido de victoria
defeat_fx = pygame.mixer.Sound('mp3/vc.mp3')  # Cargar sonido de derrota

# Funciones de dibujo
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

def draw_bg():
    screen.blit(background_img, (0, 0))

def draw_panel():
    screen.blit(panel_img, (0, screen_height - bottom_panel))
    draw_text(f'{Caballero.name} HP: {Caballero.hp}', font, red, 100, screen_height - bottom_panel + 10)
    for count, i in enumerate(Brujo_list):
        draw_text(f'{i.name} HP: {i.hp}', font, red, 550, (screen_height - bottom_panel + 10) + count * 60)

# Clase de luchador
class Fighter():
    def __init__(self, x, y, name, max_hp, strength, potions):
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        self.strength = strength
        self.start_potions = potions
        self.potions = potions
        self.alive = True
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        temp_list = []
        for i in range(8):
            img = pygame.image.load(f'img/{self.name}/Idle/{i}.png')
            img = pygame.transform.scale(img, (img.get_width() * 3, img.get_height() * 3))
            temp_list.append(img)
        self.animation_list.append(temp_list)
        temp_list = []
        for i in range(8):
            img = pygame.image.load(f'img/{self.name}/Attack/{i}.png')
            img = pygame.transform.scale(img, (img.get_width() * 3, img.get_height() * 3))
            temp_list.append(img)
        self.animation_list.append(temp_list)
        temp_list = []
        for i in range(3):
            img = pygame.image.load(f'img/{self.name}/Hurt/{i}.png')
            img = pygame.transform.scale(img, (img.get_width() * 3, img.get_height() * 3))
            temp_list.append(img)
        self.animation_list.append(temp_list)
        temp_list = []
        for i in range(10):
            img = pygame.image.load(f'img/{self.name}/Death/{i}.png')
            img = pygame.transform.scale(img, (img.get_width() * 3, img.get_height() * 3))
            temp_list.append(img)
        self.animation_list.append(temp_list)
        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):
        animation_cooldown = 100
        self.image = self.animation_list[self.action][self.frame_index]
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.idle()

    def idle(self):
        self.action = 0
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

    def attack(self, target):
        rand = random.randint(-5, 5)
        damage = self.strength + rand
        target.hp -= damage
        target.hurt()
        if target.hp < 1:
            target.hp = 0
            target.alive = False
            target.death()
        damage_text = DamageText(target.rect.centerx, target.rect.y, str(damage), red)
        damage_text_group.add(damage_text)
        self.action = 1
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

    def hurt(self):
        self.action = 2
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

    def death(self):
        self.action = 3
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

    def reset(self):
        self.alive = True
        self.potions = self.start_potions
        self.hp = self.max_hp
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()

    def draw(self):
        screen.blit(self.image, self.rect)

class HealthBar():
    def __init__(self, x, y, hp, max_hp):
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = max_hp

    def draw(self, hp):
        self.hp = hp
        ratio = self.hp / self.max_hp
        pygame.draw.rect(screen, red, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, green, (self.x, self.y, 150 * ratio, 20))

class DamageText(pygame.sprite.Sprite):
    def __init__(self, x, y, damage, colour):
        pygame.sprite.Sprite.__init__(self)
        self.image = font.render(damage, True, colour)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0

    def update(self):
        self.rect.y -= 1
        self.counter += 1
        if self.counter > 30:
            self.kill()

damage_text_group = pygame.sprite.Group()
Caballero = Fighter(200, 260, 'Caballero', 40, 10, 3)
Brujo1 = Fighter(550, 270, 'Brujo', 20, 6, 1)
Brujo2 = Fighter(700, 270, 'Brujo', 20, 6, 1)
Brujo_list = []
Brujo_list.append(Brujo1)
Brujo_list.append(Brujo2)
Caballero_health_bar = HealthBar(100, screen_height - bottom_panel + 40, Caballero.hp, Caballero.max_hp)
Brujo1_health_bar = HealthBar(550, screen_height - bottom_panel + 40, Brujo1.hp, Brujo1.max_hp)
Brujo2_health_bar = HealthBar(550, screen_height - bottom_panel + 100, Brujo2.hp, Brujo2.max_hp)
potion_button = button.Button(screen, 100, screen_height - bottom_panel + 70, potion_img, 64, 64)
restart_button = button.Button(screen, 330, 120, restart_img, 120, 30)

def menu_principal():
    # Dibujar la imagen de fondo del menú
    screen.blit(menu_background_img, (0, 0))
    
    # Dibujar el
    draw_text("Batalla medieval", font, (255, 255, 255), 300, 100)
    
    # Crear botones
    start_button = button.Button(screen, 330, 200, pygame.image.load('img/Icons/st.png').convert_alpha(), 120, 100)
    quit_button = button.Button(screen, 330, 300, pygame.image.load('img/Icons/salir.png').convert_alpha(), 120, 100)
    
    # Manejar los clics en los botones
    if start_button.draw():
        return 'game'
    if quit_button.draw():
        return 'quit'
    
    return 'menu'

run = True
while run:
    clock.tick(fps)

    if state == 'menu':
        state = menu_principal()
    elif state == 'game':
        draw_bg()
        draw_panel()
        Caballero_health_bar.draw(Caballero.hp)
        Brujo1_health_bar.draw(Brujo1.hp)
        Brujo2_health_bar.draw(Brujo2.hp)
        Caballero.update()
        Caballero.draw()
        for Brujo in Brujo_list:
            Brujo.update()
            Brujo.draw()
        damage_text_group.update()
        damage_text_group.draw(screen)
        attack = False
        potion = False
        target = None
        pygame.mouse.set_visible(True)
        pos = pygame.mouse.get_pos()
        for count, Brujo in enumerate(Brujo_list):
            if Brujo.rect.collidepoint(pos):
                pygame.mouse.set_visible(False)
                screen.blit(sword_img, pos)
                if clicked == True and Brujo.alive == True:
                    attack = True
                    target = Brujo_list[count]
        if potion_button.draw():
            potion = True
        draw_text(str(Caballero.potions), font, red, 150, screen_height - bottom_panel + 70)
        if game_over == 0:
            if Caballero.alive == True:
                if current_fighter == 1:
                    action_cooldown += 1
                    if action_cooldown >= action_wait_time:
                        if attack == True and target != None:
                            Caballero.attack(target)
                            current_fighter += 1
                            action_cooldown = 0
                        if potion == True:
                            if Caballero.potions > 0:
                                if Caballero.max_hp - Caballero.hp > potion_effect:
                                    heal_amount = potion_effect
                                else:
                                    heal_amount = Caballero.max_hp - Caballero.hp
                                Caballero.hp += heal_amount
                                Caballero.potions -= 1
                                damage_text = DamageText(Caballero.rect.centerx, Caballero.rect.y, str(heal_amount), green)
                                damage_text_group.add(damage_text)
                                current_fighter += 1
                                action_cooldown = 0
            else:
                game_over = -1
            for count, Brujo in enumerate(Brujo_list):
                if current_fighter == 2 + count:
                    if Brujo.alive == True:
                        action_cooldown += 1
                        if action_cooldown >= action_wait_time:
                            if (Brujo.hp / Brujo.max_hp) < 0.5 and Brujo.potions > 0:
                                if Brujo.max_hp - Brujo.hp > potion_effect:
                                    heal_amount = potion_effect
                                else:
                                    heal_amount = Brujo.max_hp -Brujo.hp
                                Brujo.hp += heal_amount
                                Brujo.potions -= 1
                                damage_text = DamageText(Brujo.rect.centerx, Brujo.rect.y, str(heal_amount), green)
                                damage_text_group.add(damage_text)
                                current_fighter += 1
                                action_cooldown = 0
                            else:
                                Brujo.attack(Caballero)
                                current_fighter += 1
                                action_cooldown = 0
                    else:
                        current_fighter += 1
            if current_fighter > total_fighters:
                current_fighter = 1
        alive_Brujos = 0
        for Brujo in Brujo_list:
            if Brujo.alive == True:
                alive_Brujos += 1
        if alive_Brujos == 0:
            game_over = 1
        if game_over != 0:
            if game_over == 1:
                mixer.music.stop()  # Detener la música de fondo
                victory_fx.play()  # Reproducir sonido de victoria
                screen.blit(victory_img, (250, 50))
            if game_over == -1:
                mixer.music.stop()  # Detener la música de fondo
                defeat_fx.play()  # Reproducir sonido de derrota
                screen.blit(defeat_img, (290, 50))
            if restart_button.draw():
                Caballero.reset()
                for Brujo in Brujo_list:
                    Brujo.reset()
                current_fighter = 1
                action_cooldown = 0
                game_over = 0
                mixer.music.play(-1)  # Reproducir la música de fondo de nuevo
    elif state == 'quit':
        run = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            clicked = True
        else:
            clicked = False

    pygame.display.update()

pygame.quit()
