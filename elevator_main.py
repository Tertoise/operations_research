# Dependencies
import pygame as pg
import numpy as np
import time
from statistics import mean
from random import randint
from my_math import PoissonProcessGenerator
import os

# Constants
FLOOR_W = 50
FLOOR_H = 64
# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (90, 90, 90)
LIGHTPURP = (200, 200, 230)
GREEN = (0, 230, 0)
ORANGE = (235, 70, 180)


sprite = pg.image.load(f'{os.path.abspath(os.getcwd())}/sprites/0.png')


# Elevator Class
class Elevator:
    instances = []
    selected_floor_highlighted = 1
    current_floor = 1

    def __init__(self, img, floorVar, liftsVar):
        self.__class__.instances.append(self)
        self.img = img
        self.floorVar = floorVar
        self.shaft = self.__class__.instances.index(self)
        self.x = FLOOR_W * (self.shaft + 2)
        self.y = FLOOR_H * floorVar
        self.ismoving = 0
        self.currentFloor = 1
        self.dest = 1
        self.speed = 10
        self.commands = []

    @classmethod
    def draw_doors(cls, screen):
        for instance in cls.instances:
            screen.blit(instance.img, (instance.x, instance.y))

    def add_command(self, floor):
        direction = -1 if floor < self.currentFloor else 1
        self.commands.append((direction, floor))

    def generate_commands(self, people_on_floors, current_floor):
        floors_order = calculate_lifts_order(people_on_floors, current_floor)
        for floor in floors_order:
            self.add_command(floor)

    @classmethod
    def motion(cls, gridSys, people_on_floors):
        for elevator in cls.instances:
            if elevator.commands:
                direction, target_floor = elevator.commands[0]

                if elevator.currentFloor == cls.selected_floor_highlighted:
                    cls.selected_floor_highlighted = elevator.commands[0][1]

                if elevator.currentFloor == target_floor:
                    current_floor = elevator.currentFloor
                    elevator.ismoving = 0
                    pg.time.wait(750)
                    elevator.commands.pop(0)
                    if elevator.currentFloor == 1:
                        elevator.generate_commands(people_on_floors, elevator.currentFloor)
                    people_on_floors[target_floor] = 0
                    print(elevator.commands)

                if elevator.ismoving == 0 and elevator.commands:
                    next_direction, next_target_floor = elevator.commands[0]
                    elevator.ismoving = 1 if next_target_floor > elevator.currentFloor else -1

                if elevator.ismoving != 0:

                    passing_floor = gridSys.y - int(elevator.y / FLOOR_H)

                    if elevator.ismoving == -1:
                        passing_floor += 1

                    if 1 <= passing_floor <= 12 and people_on_floors[passing_floor] > 0 and elevator.ismoving == -1:
                        pg.time.wait(500)
                        people_on_floors[passing_floor] = 0

                    # current_floor = passing_floor
                    elevator.y -= elevator.speed * elevator.ismoving

                    if (
                            (elevator.ismoving == 1 and elevator.y <= FLOOR_H * (gridSys.y - target_floor + 1)) or
                            (elevator.ismoving == -1 and elevator.y >= FLOOR_H * (gridSys.y - target_floor + 1))
                    ):
                        elevator.y = FLOOR_H * (gridSys.y - target_floor + 1)
                        elevator.currentFloor = target_floor
                        elevator.ismoving = 0

                if not elevator.commands:
                    elevator.ismoving = 0


class ShaftGrid:
    def __init__(self, floorVar, liftsVar):
        self.x = liftsVar
        self.y = floorVar
        self.LiftsGrid = []
        for i in range(liftsVar + 1):
            nextShaft = []
            for n in range(floorVar):
                nextShaft.append(pg.Rect(FLOOR_W * (i + 1), FLOOR_H * (n + 1), FLOOR_W, FLOOR_H))
            self.LiftsGrid.append(nextShaft)


# HUD
def draw_hud(screen, gridSys, people_on_floors):
    font = pg.font.Font('freesansbold.ttf', 15)

    for shaft in gridSys.LiftsGrid:
        for floor in shaft:
            pg.draw.rect(screen, LIGHTPURP, floor, 1)

    for floor in range(1, gridSys.y + 1):
        renderFloorNum = font.render(str(floor), True, WHITE)
        screen.blit(renderFloorNum, (FLOOR_W + (FLOOR_W / 2.5), FLOOR_H * (gridSys.y - floor + 1) + FLOOR_H / 2.5))

        people_count = people_on_floors[floor]
        if people_count > 0:
            number_text = str(people_count)
            renderPeopleCount = font.render(number_text, True, (255, 0, 0))

            number_rect = renderPeopleCount.get_rect(
                center=(FLOOR_W * (gridSys.x + 2) + FLOOR_W / 2, FLOOR_H * (gridSys.y - floor + 1) + FLOOR_H / 2))
            screen.blit(renderPeopleCount, number_rect)

        if floor == Elevator.selected_floor_highlighted:
            pg.draw.rect(screen, (0, 0, 255), (FLOOR_W, FLOOR_H * (gridSys.y - floor + 1), FLOOR_W, FLOOR_H), 0)


def calculate_lifts_order(people_on_floors, current_floor):
    all_zero_values = all(value == 0 for value in people_on_floors.values())
    if all_zero_values:
        return [1]

    floor = []
    people = []
    for k, v in people_on_floors.items():
        floor.append(k)
        people.append(v)
    temp = 0
    koef = []
    for i in range(len(floor)):
        if i > 0:
            temp += people[i]
        if floor[i] == current_floor:
            koef.append(0)
        else:
            koef.append(temp/(abs(floor[i] - current_floor)+(floor[i]-1)))

    if people_on_floors[1] > 0 and current_floor == 1:
        temp = 0
        koef = []
        rand_floor = randint(2, 12)
        for i in range(len(floor)):
            if i > 0:
                temp += people[i]
            if floor[i] == rand_floor:
                koef.append(0)
            else:
                koef.append(temp/(abs(floor[i] - rand_floor)+(floor[i]-1)+(rand_floor-1)))
        # print(max(koef)+people_on_floors[1]/rand_floor)
        if floor[koef.index(max(koef))] > 1:
            efficiency.append(max(koef)+people_on_floors[1]/(rand_floor-1))
            return [rand_floor, floor[koef.index(max(koef))], 1]
        else:
            efficiency.append(people_on_floors[1]/((rand_floor-1)*2))
            return [rand_floor, 1]

    efficiency.append(max(koef))
    return [floor[koef.index(max(koef))], 1]


def run_game(floorVar, liftsVar):
    pg.init()
    SCREEN_W = FLOOR_W * (liftsVar + 3)
    SCREEN_H = FLOOR_H * (floorVar + 2)
    screen = pg.display.set_mode((SCREEN_W, SCREEN_H))
    gridSys = ShaftGrid(floorVar, liftsVar)
    people_generator = PoissonProcessGenerator(intensity=0.1, time_step=0.1, value_range=np.arange(0, 13))
    people_on_floors = {floor: 0 for floor in range(1, gridSys.y + 1)}

    e = Elevator(sprite, floorVar, liftsVar)
    e.generate_commands(people_on_floors, 1)
    clock = pg.time.Clock()
    last_update_time_people = 0
    global running
    global efficiency
    efficiency = []
    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    running = False
                    print("Safe Quit")
                if event.key == pg.K_SPACE:
                    running = False
                    print(f"Efficiency - {mean(efficiency)}(people/floor)")
        try:
            screen.fill(GRAY)
            current_time = time.time()

            if current_time - last_update_time_people >= 5:
                for floor in range(1, gridSys.y + 1):
                    people_on_floors[floor] += people_generator.generate_next_value()
                people_on_floors[1] = sum(people_on_floors.values())
                last_update_time_people = current_time

            draw_hud(screen, gridSys, people_on_floors)
            Elevator.draw_doors(screen)
            Elevator.motion(gridSys, people_on_floors)
            pg.display.update()
            clock.tick(60)

        except pg.error:
            return


if __name__ == '__main__':
    run_game(12, 1)
