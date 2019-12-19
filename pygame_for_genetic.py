import pygame
from random import *
import random
import math
pygame.init()
screen = pygame.display.set_mode((800,600)) # generic syntax

def distance(x1,x2,y1,y2): #p1  is the target
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

class obstacles:
    def __init__(self):
        self.boundary_lists = []
    def obstacle_create(self,left,top,width,height):
        self.boundary_lists.append(left)
        self.boundary_lists.append(top)
        self.boundary_lists.append(width)
        self.boundary_lists.append(height)
        rectangle = pygame.Rect(left,top,width,height)
        self.draw(rectangle)
        return rectangle
    def draw(self,rectangle):
        pygame.draw.rect(screen,[0,255,0],rectangle)

class ball:
    def __init__(self,target_x,target_y, target_radius):
        self.upwards_velocity = [randint(-3,0) for i in range(1000)]
        self.target_radius = target_radius
        self.goal_y = target_y
        self.goal_radius = target_radius
        self.list_i = 0
        #below makes a list of values within the radius of the target
        self.goal_x = [-i for i in range(target_radius + 1)]
        self.goal_x = self.goal_x[::-1]
        for i in range(target_radius):
            self.goal_x.append(i+1)
        self.goal_x = [i + target_x for i in self.goal_x]

        self.left_right_velocity = [randint(-7,7) for i in range(1000)] # negative left, positive right - summed
        self.x_pos = 395
        self.y_pos = 590
        self.color = [255,0,0]
        self.fitness = 0
        self.y_fitness = 0
        self.stop = False
        self.intial_position = [395,595]

    def draw(self):
        pygame.draw.circle(screen,self.color,[self.x_pos,self.y_pos],5,0)

    def move(self,i):
        if self.y_pos >= (i[1] - i[3]) and self.y_pos <= (i[1] + i[3]) and self.x_pos >= i[0] and self.x_pos <= (i[0] + i[2]):
            self.stop = True
            return
        if self.y_pos <= 5 :
            self.stop = True
            return
        elif self.list_i >= 1000 or self.stop:
            self.stop = True
            return
        else:
            self.x_pos += self.left_right_velocity[self.list_i]
            self.y_pos += self.upwards_velocity[self.list_i]
            self.list_i += 1

    def fitness_calc_y(self):
        if self.stop:
            if self.y_pos > self.goal_y + 5:
                loss = self.y_pos - (self.goal_y + 5)
            elif self.y_pos < self.goal_y - 5:
                loss = (self.goal_y - 5)  - self.y_pos
            else:
                loss = 0
            self.y_fitness = 600 - loss

    def x_make(self,target_x):
        self.goal_x = [-i for i in range(self.target_radius + 1)]
        self.goal_x = self.goal_x[::-1]
        for i in range(self.target_radius):
            self.goal_x.append(i+1)
        self.goal_x = [i + target_x for i in self.goal_x]

    def target_hit(self): #currently testing to see if it sees when it reaches the target y axis
        if self.y_pos >= self.goal_y - 5 and self.y_pos <= self.goal_y + 5:
            if self.x_pos > self.goal_x[-1]:
                loss =self.x_pos  -  self.goal_x[-1]
            elif self.x_pos < self.goal_x[0]:
                loss = self.goal_x[0] - self.x_pos
            else:
                loss = 0
            self.fitness = 800 - loss
            if self.fitness == 800:
                self.color = [0,0,255]
                self.stop = True

    def reset(self,target_y):
        self.stop  = False
        self.x_pos = self.intial_position[0]
        self.y_pos = self.intial_position[1]
        self.color = [255,0,0]
        self.goal_y = target_y
        self.list_i = 0


class genetic_algo:
    def __init__(self,population_size):
        self.population_size = population_size
        self.population = [ball(target_x, target_y, target_radius) for i in range(population_size)]
        self.initial_pop = True
        self.next_pop = []

    def all_stopped(self):
        stopped = []
        for i in self.population:
            if i.stop == True:
                stopped.append(True)
            else:
                stopped.append(False)
        for i in stopped:
            if i == False:
                return False
        return True

    def fitness_sort(self):
        self.population.sort(key=lambda x: distance(x.goal_x[len(x.goal_x)//2],x.x_pos, x.goal_y,x.y_pos), reverse=True)
        #self.population.sort(key=lambda y: y.y_fitness,reverse=True)
    def step_up(self):
        percentage = int((5/100) * self.population_size)
        for i in range(percentage):
            self.next_pop.append(self.population[i])

    def selection(self):
        m  = len(self.next_pop)
        while m <= self.population_size:
            competitor_a_1 = self.population[randint(0,self.population_size-1)]
            competitor_a_2 = self.population[randint(0,self.population_size-1)]
            distance_a_1 = distance(competitor_a_1.goal_x[len(competitor_a_1.goal_x)//2],competitor_a_1.x_pos,competitor_a_1.goal_y,competitor_a_1.y_pos)
            distance_a_2 = distance(competitor_a_2.goal_x[len(competitor_a_2.goal_x)//2],competitor_a_2.x_pos,competitor_a_2.goal_y,competitor_a_2.y_pos)
            parent_a = competitor_a_1 if distance_a_1 < distance_a_2 else competitor_a_2
            competitor_b_1 = self.population[randint(0,self.population_size-1)]
            competitor_b_2 = self.population[randint(0,self.population_size-1)]
            distance_b_1 = distance(competitor_b_1.goal_x[len(competitor_b_1.goal_x)//2],competitor_b_1.x_pos,competitor_b_1.goal_y,competitor_b_1.y_pos)
            distance_b_2 = distance(competitor_b_2.goal_x[len(competitor_b_2.goal_x)//2],competitor_b_2.x_pos,competitor_b_2.goal_y,competitor_b_2.y_pos)
            parent_b = competitor_b_1 if distance_b_1 < distance_b_2 else competitor_b_2
            self.mate(parent_a,parent_b)
            m += 1
        self.population = [i for i in self.next_pop]
        del self.next_pop[:]

    def mate(self,parent_a,parent_b):
            P = randint(0,len(parent_a.upwards_velocity))
            velocity_upwards = [*parent_a.upwards_velocity[0:P],*parent_b.upwards_velocity[P:]]
            velocity_sides = [*parent_a.left_right_velocity[0:P],*parent_b.left_right_velocity[P:]]
            self.next_pop.append(ball(parent_a.goal_x[len(parent_a.goal_x)//2],parent_a.goal_y,parent_a.goal_radius))
            self.next_pop[-1].upwards_velocity = velocity_upwards
            self.next_pop[-1].left_right_velocity = velocity_sides
            self.mutation()

    def mutation(self):
        new_upwards = []
        for i in range(1000):
            m = random.random()
            if m > 0.98:
                new_upwards.append(randint(-3,4))
            else:
                new_upwards.append(self.next_pop[-1].upwards_velocity[i])

        self.next_pop[-1].upwards_velocity = [i for i in new_upwards]
        new_left_right  = []

        for i in range(1000):
            m = random.random()
            if m > 0.98: #ideal = 0.98 for no obstacles
                new_left_right.append(randint(-11,11))
            else:
                new_left_right.append(self.next_pop[-1].left_right_velocity[i])
        self.next_pop[-1].left_right_velocity = [i for i in new_left_right]
    def most_hit(self):
        numberhit = 0
        for i in self.population:
            if i.color == [0,0,255]:
                numberhit += 1
        return numberhit

class target:
    def __init__(self,radius):
        self.t_x_pos = randint(0,800)
        self.t_y_pos = randint(0,600)
        self.radius = radius
    def draw(self):
        pygame.draw.circle(screen,[0,255,0],[self.t_x_pos,self.t_y_pos],self.radius,0)
    def reset(self):
        self.t_x_pos = randint(0,800)
        self.t_y_pos = randint(0,600)
        pygame.draw.circle(screen,[0,255,0],[self.t_x_pos,self.t_y_pos],self.radius,0)

#Variable declarations
store = target(5)
target_y = store.t_y_pos
target_x = store.t_x_pos
target_radius = store.radius

mem = genetic_algo(100)


for i in mem.population:
    i.draw()
running = True
press = False

obsti = obstacles()
recti = obsti.obstacle_create(400,295,400,10)
generation = 1
while running:
        for event in pygame.event.get(): # runs through all the events in pygame
            if event.type == pygame.QUIT: # capital quit
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    press = True
                if event.key == pygame.K_RIGHT:
                    store.reset()
                    for i in mem.population:
                        i.reset(store.t_y_pos)
                        i.x_make(store.t_x_pos)
                if event.key == pygame.K_UP:
                    if(mem.all_stopped()):
                        print("all stopped")

        if press:
            screen.fill([0,0,0])
            for i in mem.population:
                i.move(obsti.boundary_lists)
                i.draw()
                i.target_hit()

        if mem.all_stopped():
            print("Generation: %d"%generation)
            print("The number of populants that hit the target are: %d" %(mem.most_hit()))
            generation += 1
            mem.fitness_sort()
            mem.selection()

        store.draw()
        obsti.draw(recti)
        pygame.display.update()
