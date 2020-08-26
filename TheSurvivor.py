

import pygame
from pygame.locals import *
import numpy as np
import random
import time
import math
import uuid



# initializers
pygame.mixer.pre_init()
pygame.mixer.init()
pygame.init()


# some screen related parameters
screen_width = 1263
screen_height = 440
ground_height = 109
root = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('The Survivor')


# play background score
pygame.mixer.music.load('sounds_music/bg_music.mp3')
pygame.mixer.music.play(-1)


# set the maximum number of available channels
pygame.mixer.set_num_channels(20)


# load the sound effects
wheel_sound = pygame.mixer.Sound('sounds_music/wheel.wav')
wheel_sound.set_volume(0.35)
slide_sound = pygame.mixer.Sound('sounds_music/slide.wav')
jump_sound = pygame.mixer.Sound('sounds_music/jump.wav')
click_sound = pygame.mixer.Sound('sounds_music/click.wav')
collision_sound = pygame.mixer.Sound('sounds_music/collision.wav')


# names of image files
images_list_jump = [ 'images/'+str(x)+'.png' for x in range(1,8) ]
images_list_run = [ 'images/'+str(x)+'.png' for x in range(8,16) ]
images_list_slide = [ 'images/S'+str(x)+'.png' for x in range(1,6) ]





class game :

    isMusicOn = True
    isSoundOn = True
    isPause = False
    score = 0
    lives = 5
    secsElapsed = 0
    finish = False
    screen_speed = 3
    frames_per_second = 32
    jump_manager_flag = 0
    obstacle_probability = 100
    obstacle_appear_lag = 4000
    time_of_flight_controller = 5
    time_of_slide_controller = 95
    player_speed_controller = 8
    max_attainable_speed = 10
    
    # additional information
    __max_attainable_screen_speed__ = 10.04
    __min_attainable_obstacle_appear_lag__ = 1816
    __min_attainable_time_of_flight_controller__ = 2.04
    __min_attainable_time_of_slide_controller__ = 35.43
    __min_attainable_player_speed_controller__ = 2.29
    __saturation_time__ = '05minutes06seconds'
    
    @classmethod
    def update_gallery (cls) :
        global player_run, player_slide
        player_run.clear()
        player_slide.clear()
        
        for image in images_list_run :
            player_run += [pygame.image.load(image)]*int(cls.player_speed_controller)
            
        for image in images_list_slide :
            factor = int(cls.time_of_slide_controller*3/5) if image=='images/S2.png' else int(cls.time_of_slide_controller/10)
            player_slide += [pygame.image.load(image)]*factor




# list of images while player is jumping
player_jump = list()
for image in images_list_jump :
    player_jump += [pygame.image.load(image)]*5


# list of images while player is running
player_run = list()
for image in images_list_run :
    player_run += [pygame.image.load(image)]*int(game.player_speed_controller)
 

# list of images while player is sliding
player_slide = list()
for image in images_list_slide :
    factor = int(game.time_of_slide_controller*3/5) if image=='images/S2.png' else int(game.time_of_slide_controller/10)
    player_slide += [pygame.image.load(image)]*factor
    

# spike obstacle
obstacle_spike = pygame.image.load('images/spike.png')


# list of images of wheel at different angles
grinding_wheel = [
    pygame.image.load('images/SAW0.png') ,
    pygame.image.load('images/SAW1.png') ,
    pygame.image.load('images/SAW2.png') ,
    pygame.image.load('images/SAW3.png')
]


# load the background image
bg = pygame.image.load('images/bg_modified.png')
bg_ = pygame.image.load('images/bg_modified2.png')
bgx , bgx_ = (0, screen_width)





class player :

    def __init__ (self, x_start, y_start, width, height) :
        self.x = x_start
        self.y = y_start
        self.width = width
        self.height = height
        self.walkCount = 0
        self.jump = False
        self.slide = False
        self.dead = False
        self.jumpCount = 10
        self.airTime = 0
        self.slideTime = 0
        self.reset_hitbox()
        
    def update_aft_jump (self) :
        if self.jumpCount >= -10 :
            factor = 1 if self.jumpCount > 0 else -1
            self.y -= 0.5 * factor * (self.jumpCount**2)
            self.jumpCount -= 1
            self.airTime = (self.airTime + 1) % len(player_jump)
            self.reset_hitbox()
        else :
            self.jump = False
            self.jumpCount = 10
            self.airTime = 0
            flag = 0
            self.reset_hitbox()
            
    def reset_hitbox (self) :
        self.hitbox = (self.x, self.y, self.width, self.height)





def collision_result() :
    global soldier, spikes, wheels
    channel_collision.play(collision_sound)
    time.sleep(0.5)
    spikes.clear()
    wheels.clear()
    soldier.jump = soldier.slide = False
    soldier.x, soldier.y = (screen_width/3, screen_height-136)
    game.jump_manager_flag = 0
    soldier.walkCount = 0
    soldier.jumpCount = 10
    soldier.airTime = 0
    soldier.slideTime = 0
    game.lives -= 1
    if game.lives == 0 :
        finish_game()
    




def finish_game () :
   
    game.finish = True
    pygame.mixer.music.stop()
    pygame.mixer.music.load('sounds_music/finishGame.mp3')
    pygame.mixer.music.play(-1)
    if not game.isMusicOn : pygame.mixer.music.pause()
    
    clicked_btn = ''
    
    while game.finish :
    
    
        for each_button in buttons :
            each_button.update_status()
            
        root.blit(bg, (0,0))
        
        for each_button in buttons :
            root.blit(each_button.buttonImage, (each_button.x, each_button.y))
        
        custom_font = pygame.font.Font('freesansbold.ttf', 50)
        text = 'GAME OVER'
        
        root.blit(player_run[0], (soldier.x, soldier.y))
        
        display_score_lives()
        
        text_surface = custom_font.render(text, True, (255, 69, 0))
        text_rect = text_surface.get_rect()
        text_rect.center = (screen_width/2, screen_height/2)
        root.blit(text_surface, text_rect)
        pygame.display.update()
        
        
        for event in pygame.event.get() :
        
            if event.type == pygame.QUIT :
                game.finish = False
                
            if event.type == pygame.MOUSEBUTTONUP :
            
                for eachButton in buttons :
                    if eachButton.hover :
                        clicked_btn = eachButton
                        click_sound.play()
                        if not clicked_btn.type == 'pause' : clicked_btn.action()
                        break
                
                if clicked_btn.type == 'restart' :
                    pygame.mixer.music.stop()
                    time.sleep(1)
                    pygame.mixer.music.load('sounds_music/bg_music.mp3')
                    pygame.mixer.music.play(-1)
                    game.finish = False
                    return
                    
                if clicked_btn.type == 'close' :
                    game.finish = False
                    break
                
    if clicked_btn.type == 'close' : return
    
    pygame.quit()
  
    



class spike :

    def __init__ (self, x_start, y_start, width, height) :
        self.x = x_start
        self.y = y_start
        self.width = width
        self.height = height
        self.id = uuid.uuid4()
        self.reset_hitbox()
        
    def reset_hitbox(self) :
        self.hitbox = [
                        (self.x, self.y), 
                        (self.x+self.width, self.y), 
                        (self.x+self.width, self.y+285), 
                        (self.x+self.width-18, self.y+self.height-3), 
                        (self.x+18, self.y+self.height-3), 
                        (self.x, self.y+285)
                       ]
                       
    def check_collision (self) :
        if soldier.hitbox[0]+soldier.hitbox[2] > self.hitbox[0][0] and soldier.hitbox[0] < self.hitbox[1][0] :
            if soldier.hitbox[1] < self.hitbox[2][1] :
                collision_result()
                return
                
        if soldier.hitbox[0]+soldier.hitbox[2] > self.hitbox[4][0] and soldier.hitbox[0] < self.hitbox[3][0] :
            if soldier.hitbox[1] < self.hitbox[3][1] and soldier.hitbox[1] > self.hitbox[2][1] :
                collision_result()
                return





class wheel :

    def __init__ (self, x_start, y_start, width, height) :
        self.x = x_start
        self.y = y_start
        self.width = width
        self.height = height
        self.rotationCount = 0
        self.stop = False # when the man dies
        self.id = uuid.uuid4()
        self.reset_hitbox()
        
    def reset_hitbox(self) :
        self.hitbox = {'center' : (self.x+55, self.y+53), 'radius' : 53}
        
    def check_collision (self) :
        global soldier, spikes, wheels, channel_collision
        if math.hypot(soldier.hitbox[0]+soldier.hitbox[2]-self.hitbox['center'][0], soldier.hitbox[1]-self.hitbox['center'][1]) <= self.hitbox['radius'] :
            collision_result()
            return
        elif math.hypot(soldier.hitbox[0]+soldier.hitbox[2]-self.hitbox['center'][0], soldier.hitbox[1]+soldier.hitbox[3]-self.hitbox['center'][1]) <= self.hitbox['radius'] :
            collision_result()
            return
        elif math.hypot(soldier.hitbox[0]-self.hitbox['center'][0], soldier.hitbox[1]+soldier.hitbox[3]-self.hitbox['center'][1]) <= self.hitbox['radius'] :
            collision_result()
            return



 

class button :

    def __init__ (self, x, y, type, size) :
        self.x = x
        self.y = y
        self.type = type
        self.size = size
        self.normalImageName = 'images/' + type + '_normal.png'
        self.hoverImageName = 'images/' + type + '_hover.png'
        self.normal = True
        self.hover = False
        self.update_image()
        
    def update_image (self) :
        if self.type == 'pause' and game.isPause :
            if self.normal :
                self.buttonImage = pygame.transform.scale(pygame.image.load('images/play_normal.png'), self.size)
            elif self.hover :
                self.buttonImage = pygame.transform.scale(pygame.image.load('images/play_hover.png'), self.size) 
            return 
                
        if self.normal :
            self.buttonImage = pygame.transform.scale(pygame.image.load(self.normalImageName), self.size)
        elif self.hover :
            self.buttonImage = pygame.transform.scale(pygame.image.load(self.hoverImageName), self.size) 
            
    def update_status (self) :
        mouse_pos = pygame.mouse.get_pos()
        center_of_button = (self.x+self.size[0]/2, self.y+self.size[1]/2)
        distance = math.hypot(mouse_pos[0]-center_of_button[0], mouse_pos[1]-center_of_button[1])
        if distance > (self.size[1]+self.size[0])/4 :
            self.normal = True
            self.hover = False
        else :
            self.normal = False
            self.hover = True
        self.update_image()
        
    def action(self) :
        if self.type == 'music' :
            if game.isMusicOn :
                pygame.mixer.music.pause()
                game.isMusicOn = False
            else :
                pygame.mixer.music.unpause()
                game.isMusicOn = True
            return
            
        if self.type == 'pause' :
            if not game.isPause :
                game.isPause = True
            else :
                game.isPause = False
            return
            
        if self.type == 'restart' :
            global soldier, wheels, spikes, bgx, bgx_, passed_obstacle_ids
            game.isPause = False
            game.score = 0
            game.lives = 5
            game.secsElapsed = 0
            game.screen_speed = 2
            game.jump_manager_flag = 0
            game.obstacle_appear_lag = 4500
            game.time_of_flight_controller = 5
            game.time_of_slide_controller = 110
            game.player_speed_controller = 8
            soldier.x = screen_width/3
            soldier.y = screen_height-136
            soldier.jump = soldier.slide = False
            soldier.walkCount = 0
            soldier.jumpCount = 10
            soldier.airTime = 0
            soldier.slideTime = 0
            pygame.time.set_timer(obstacle_appear, game.obstacle_appear_lag)
            pygame.time.set_timer(increase_screen_speed, 3*1000)
            spikes.clear()
            wheels.clear()
            passed_obstacle_ids.clear()
            bgx , bgx_ = (0, screen_width)
            pygame.mixer.music.rewind()
            time.sleep(0.5)
            return
            
        if self.type == 'sound' :
            if game.isSoundOn :
                wheel_sound.set_volume(0)
                slide_sound.set_volume(0)
                jump_sound.set_volume(0)
                collision_sound.set_volume(0)
                click_sound.set_volume(0)
                game.isSoundOn = False
            else :
                wheel_sound.set_volume(0.35)
                slide_sound.set_volume(1)
                jump_sound.set_volume(1)
                collision_sound.set_volume(1)
                click_sound.set_volume(1)
                game.isSoundOn = True
            return
            
        if self.type == 'close' :
            global run
            run = False
            return
            




# list of all the buttons on the screen
buttons = [
    button(5, screen_height-55, 'music', (50,50)) ,
    button(60, screen_height-55, 'sound', (50,50)) ,
    button(screen_width-55, screen_height-55, 'restart', (50,50)) ,
    button(screen_width-110, screen_height-55, 'pause', (50,50)) ,
    button(screen_width-55, 5, 'close', (50,50))
]





def game_attributes_tracker () :
    print('\n\n\nseconds_elapsed', game.secsElapsed)
    print('screen_speed', game.screen_speed)
    print('time_of_flight_controller', game.time_of_flight_controller)
    print('time_of_slide_controller', game.time_of_slide_controller)
    print('player_speed_controller', game.player_speed_controller)
    print('obstacle_appear_lag', game.obstacle_appear_lag)
    return





def display_screen() :
    global buttons 
    
    global soldier
    root.blit(bg, (bgx, 0))
    root.blit(bg_, (bgx_, 0))
    
    for obstacle in spikes :
        root.blit(obstacle_spike, (obstacle.x, obstacle.y))
        
    for obstacle in wheels :
        root.blit(grinding_wheel[obstacle.rotationCount], (obstacle.x, obstacle.y))
    
    for each_button in buttons :
        root.blit(each_button.buttonImage, (each_button.x, each_button.y))
    
    
    if not soldier.jump and not soldier.slide :
        present_posture = player_run[soldier.walkCount % len(player_run)]
        root.blit(present_posture, (soldier.x, soldier.y))
        soldier.width, soldier.height = present_posture.get_rect().size
        soldier.reset_hitbox()
        
    elif soldier.jump :
        present_posture = player_jump[soldier.airTime]
        root.blit(present_posture, (soldier.x, soldier.y))
        soldier.width, soldier.height = present_posture.get_rect().size
        if not game.finish : soldier.reset_hitbox()
        
    else :
        present_posture = player_slide[soldier.slideTime % len(player_slide)]
        root.blit(present_posture, (soldier.x, soldier.y))
        soldier.width, soldier.height = present_posture.get_rect().size
        if not game.finish : soldier.reset_hitbox()
        soldier.y = screen_height - ground_height - soldier.height + 25
        
    
    for obstacle in spikes :
        obstacle.check_collision()
        
    for obstacle in wheels :
        obstacle.check_collision()
        
        
    display_score_lives()
    display_clock ()
        
    pygame.display.update()
    
    
    


def display_score_lives () :
    custom_font = pygame.font.Font('freesansbold.ttf', 28)
    text_score = 'SCORE : ' + str(game.score)
    
    text_surface_score = custom_font.render(text_score, True, (255, 20, 147))
    text_rect_score = text_surface_score.get_rect()
    text_rect_score.center = (5+text_rect_score.size[0]/2, 5+text_rect_score.size[1]/2)
    root.blit(text_surface_score, text_rect_score)
    
    text_lives = 'LIVES : ' + str(game.lives)
    custom_font = pygame.font.Font('freesansbold.ttf', 27)
    
    text_surface_lives = custom_font.render(text_lives, True, (255, 20, 147))
    text_rect_lives = text_surface_lives.get_rect()
    text_rect_lives.center = (5+text_rect_lives.size[0]/2, 10+text_rect_score.size[1]+text_rect_lives.size[1]/2)
    root.blit(text_surface_lives, text_rect_lives)
    
    
    


def display_clock () :
    minutes = int(game.secsElapsed // 60)
    seconds = int(game.secsElapsed - minutes*60)
    if minutes < 10 :   minutes = '0' + str(minutes)
    if seconds < 10 :   seconds = '0' + str(seconds)
    time_elapsed = str(minutes) + ' : ' + str(seconds)
    
    custom_font = pygame.font.Font('freesansbold.ttf', 28)
    text = 'TIME ELAPSED : ' + time_elapsed
    
    text_surface = custom_font.render(text, True, (0, 0, 205))
    text_rect = text_surface.get_rect()
    text_rect.center = (screen_width/2, screen_height-text_rect.size[1]-5)
    root.blit(text_surface, text_rect)
    
    
    
    
    
spikes = list()
wheels = list()

passed_obstacle_ids = set()

clock = pygame.time.Clock()

increase_screen_speed = USEREVENT+1
pygame.time.set_timer(increase_screen_speed, 3*1000)
obstacle_appear = USEREVENT+2
pygame.time.set_timer(obstacle_appear, game.obstacle_appear_lag)
set_time_elapsed = USEREVENT+3
pygame.time.set_timer(set_time_elapsed, 1000)

channel_activity = pygame.mixer.Channel(4)
channel_click = pygame.mixer.Channel(5)
channel_collision = pygame.mixer.Channel(3)
channel_newjump = pygame.mixer.Channel(1)

soldier = player(screen_width/3, screen_height-136, 37, 60)

run = True





while run :

    soldier.walkCount = (soldier.walkCount + 1) % len(player_run)
    
    
    for each_button in buttons :
        each_button.update_status()
    
    
    if len(wheels) > 0 : 
        wheel_sound.play(fade_ms=1000)
    else : 
        wheel_sound.fadeout(1000)
        
        
    bgx -= game.screen_speed
    bgx_ -= game.screen_speed
    
    if bgx <= -1*screen_width :
        bgx = screen_width
    if bgx_ <= -1*screen_width :
        bgx_ = screen_width
        
    
    spikes_copy = spikes.copy()
    for obstacle in spikes :
        if soldier.x > obstacle.hitbox[1][0]  :
            passed_obstacle_ids.add(obstacle.id)
        
        obstacle.x -= game.screen_speed
        obstacle.reset_hitbox()
        
        if obstacle.x <= -1*obstacle.width :
            spikes_copy.remove(obstacle)
    
    spikes = spikes_copy.copy()
    
    
    wheels_copy = wheels.copy()
    for obstacle in wheels :
    
        if soldier.x > obstacle.hitbox['center'][0]+obstacle.hitbox['radius'] :
            passed_obstacle_ids.add(obstacle.id)
    
        obstacle.x -= game.screen_speed
        obstacle.reset_hitbox()
        obstacle.rotationCount = (obstacle.rotationCount+1) % 4
    
        if obstacle.x <= -1*obstacle.width :
            wheels_copy.remove(obstacle)
    
    wheels = wheels_copy.copy()
 
    game.score = len(passed_obstacle_ids)
    
    for event in pygame.event.get() :
        if event.type == pygame.QUIT :
            run = False
            
            
        if event.type == increase_screen_speed and game.screen_speed < game.max_attainable_speed :
            game.screen_speed += 0.069
            game.time_of_flight_controller -= 0.029
            game.time_of_slide_controller -= 0.584
            game.player_speed_controller -= 0.056
            game.update_gallery()
            
            # game_attributes_tracker()
            
        
        if event.type == obstacle_appear :
            if random.uniform(0,1) <= game.obstacle_probability/100 :
                if random.randint(0,1) == 0 : # FIX IT
                    spikes.append(spike(screen_width, 0, 48, 320))
                else :
                    wheels.append(wheel(screen_width, screen_height-195, 112, 117))
            if game.screen_speed < game.max_attainable_speed :
                game.obstacle_appear_lag -= 21
                pygame.time.set_timer(obstacle_appear, game.obstacle_appear_lag)
         
         
        if event.type == set_time_elapsed :
            game.secsElapsed += 1
            
            
        if event.type == pygame.MOUSEBUTTONUP :
            for eachButton in buttons :
                if eachButton.hover :
                    click_sound.play()
                    eachButton.action()
                    break
        
        
        if event.type == pygame.KEYUP :
            if event.key == pygame.K_SPACE and not soldier.slide and not soldier.jump :
                channel_newjump.play(jump_sound)
                soldier.jump = True
            if event.key == pygame.K_DOWN and not soldier.jump and not soldier.slide :
                channel_activity.play(slide_sound)
                soldier.slide = True
    
    
    
    old_isPause = game.isPause
    
    if game.isPause :
        wheel_sound.stop()
        game.isSoundOn = False
    
    while game.isPause :
        for each_button in buttons :
            each_button.update_status()
        for event in pygame.event.get() :
            if event.type == pygame.MOUSEBUTTONUP :
                for eachButton in buttons :
                    if eachButton.hover :
                        click_sound.play()
                        if eachButton.type == 'close' :
                            run = False
                            pygame.quit()
                        if eachButton.type == 'sound' :
                            continue
                        eachButton.action()
                            
                        break
            if event.type == pygame.QUIT :
                game.isPause = False
                run = False
                break
        try : display_screen()
        except : break
    
    if old_isPause :
        pygame.time.set_timer(increase_screen_speed, 3*1000)
        pygame.time.set_timer(obstacle_appear, game.obstacle_appear_lag)
        game.isSoundOn = True
    
    
    if soldier.jump :
        if game.jump_manager_flag == 0 :
            soldier.update_aft_jump()
        game.jump_manager_flag = (game.jump_manager_flag + 1) % int(game.time_of_flight_controller)
    
    if soldier.slide :
        soldier.slideTime = (soldier.slideTime+1)
        if soldier.slideTime > int(game.time_of_slide_controller) :
            soldier.slide = False
            soldier.slideTime = 0
            soldier.y = screen_height-136
    
    
    clock.tick_busy_loop(game.frames_per_second)
    
    
    try : display_screen()
    except : break





pygame.quit()
