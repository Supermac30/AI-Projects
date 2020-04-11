import numpy as np
from keras.models import Sequential
from keras.layers import Activation, Dense

import pygame
import sys
from random import randint, random

clock = pygame.time.Clock()
pygame.init()
pygame.font.init()
pygame.display.set_caption('Flappy Bird With An Evolving Neural Net')
screen = pygame.display.set_mode((800, 600))
font = pygame.font.SysFont('Arial', 20)

YELLOW = (255, 255, 0)
LIGHTGREEN = (0, 200, 0)
DARKGREEN = (0, 100, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)

PLAYERRAD = 13
PIPEWIDTH = 60
PIPEFREQ = 450
PIPESPEED = 1
FALLRATE = 1
JUMPTIME = 50
JUMPSPEED = 2
PIPESPACE = 190
CONFIDENCE = 0.5
NUMAIS = 50
LEARNINGRATE = 1
DISCOUNT = 0.85

class Player:
    def __init__(self, model = []):
        self.pos = [50, 300]
        self.timeSinceJump = 0
        self.points = 0
        self.alive = True

        self.model = Sequential()
        self.model.add(Dense(5, activation='relu', input_shape=(3,)))
        self.model.add(Dense(1, activation='sigmoid'))
        if model != []:
            self.model.set_weights(model)
        self.timeAlive = pygame.time.get_ticks()
             
    def draw(self, surface):
        pygame.draw.circle(surface, YELLOW, self.pos, PLAYERRAD)

    def update(self):
        if self.timeSinceJump == 0:
            self.pos[1] += FALLRATE
        else:
            self.pos[1] -= FALLRATE*JUMPSPEED
            self.timeSinceJump -= 1

    def jump(self):
        self.timeSinceJump = JUMPTIME

    def input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            self.jump()

    def collide(self, pipe):
        pipes = pipe.rect0, pipe.rect1
        if self.pos[1] + PLAYERRAD >= 600 or self.pos[1] - PLAYERRAD < 0:
            self.alive = False
            self.timeAlive = pygame.time.get_ticks() - self.timeAlive
        if self.pos[0] + PLAYERRAD >= pipes[0][0] and self.pos[0] + PLAYERRAD - PIPEWIDTH <= pipes[0][0]:
            if self.pos[1] + PLAYERRAD > pipes[0][1] or self.pos[1] - PLAYERRAD < pipes[1][1] + pipes[1][3]:
                self.alive = False
                self.timeAlive = pygame.time.get_ticks() - self.timeAlive

    def think(self, vDist):
        prediction = self.model.predict(np.array([[self.pos[1]/600, vDist/600, 0 if self.timeSinceJump == 0 else 0.1]]))
        if prediction[0][0] > CONFIDENCE:
            self.jump()

    def reproduce(self, numBabies, gen):
        babies = []
        for _ in range(numBabies):
            weights = self.model.get_weights()
            for j in range(3):
                for i in range(5):
                    weights[0][j][i] += (random()-0.5)*(LEARNINGRATE*(DISCOUNT**gen))
            for i in range(5):
                weights[2][i][0] += (random()-0.5)*(LEARNINGRATE*(DISCOUNT**gen))
            babies.append(Player(model = weights))
        return babies

class Pipe:
    def __init__(self):
        height = randint(0, 600-PIPESPACE)
        self.rect0 = pygame.rect.Rect((800, 600-height, PIPEWIDTH, height))
        self.rect1 = pygame.rect.Rect((800, 0, PIPEWIDTH, 600-height-PIPESPACE))
    def draw(self, surface):
        pygame.draw.rect(surface, DARKGREEN, self.rect0)
        pygame.draw.rect(surface, DARKGREEN, self.rect1)
    def update(self):
        self.rect0.move_ip(-PIPESPEED, 0)
        self.rect1.move_ip(-PIPESPEED, 0)


class Game:
    def __init__(self): 
        self.player = Player()
        self.ais = []
        for i in range(NUMAIS):
            self.ais.append(Player())
        self.pipes = []
        self.score = 0
        self.isOver = False
        self.state = 1
        self.timeSincePipe = 0
        self.gen = 0
        self.best = None
        
    def loop(self):
        for event in pygame.event.get():
            pass
        if self.state == 0: # User plays
            self.buildGame([self.player])
            self.managePlayer()
            
        if self.state == 1: # AI Trains
            self.buildGame(self.ais)
            self.manageBrains()

        if self.state == 2: # AI plays
            pass
        pygame.display.update()

    def manageBrains(self):
        pipeV = self.pipes[0].rect0[1]
        allDead = True
        for ai in self.ais:
            if ai.alive:
                allDead = False
                if pygame.time.get_ticks() % 2 == 0:
                    ai.think(ai.pos[1]-pipeV)
                ai.update()
                ai.draw(screen)
                ai.collide(self.pipes[0])
        if allDead:
            self.ais = self.ais[self.fittestAI()].reproduce(NUMAIS, self.gen)
            self.pipes = [Pipe()]
            self.timeSincePipe = PIPEFREQ
            self.gen += 1
            self.score = 0

    def fittestAI(self):
        fittest = [0,0]
        for i in range(len(self.ais)):
            if self.ais[i].timeAlive > fittest[0]:
                fittest = [self.ais[i].timeAlive, i]
        print(self.gen, fittest)
        self.best = self.ais[fittest[1]]
        return fittest[1]

    def managePlayer(self):
        self.player.input()
        self.player.update()
        self.player.draw(screen)
        self.player.collide(self.pipes[0])
        if not self.player.alive:
            self.isOver = True
            
    def buildGame(self, players):
        screen.fill(BLUE)

        if self.timeSincePipe == 0:
            self.pipes.append(Pipe())
            self.timeSincePipe = PIPEFREQ
        else:
            self.timeSincePipe -= 1

        fixed = []
        for pipe in self.pipes:
            pipe.draw(screen)
            pipe.update()
            if pipe.rect0[0] > -PIPEWIDTH:
                fixed.append(pipe)
            else:
                self.score += 1
        self.pipes = fixed[:]

        textSurface0 = font.render("Gen: " + str(self.gen), False, WHITE)
        textSurface1 = font.render("Score: " + str(self.score), False, WHITE)
        screen.blit(textSurface0, (400, 0))
        screen.blit(textSurface1, (300, 0))



game = Game()
while not game.isOver:
    game.loop()
