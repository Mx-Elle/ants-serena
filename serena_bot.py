from multiprocessing import Queue
from collections import defaultdict
from collections import deque
from random import choice
from board import Entity, neighbors
import numpy as np
import numpy.typing as npt

AntMove = tuple[tuple[int, int], tuple[int, int]]

def valid_neighbors(
    row: int, col: int, walls: npt.NDArray[np.int_]
) -> list[tuple[int, int]]:
    return [n for n in neighbors((row, col), walls.shape) if not walls[n]]

def manhattan_dist(a: tuple, b: tuple) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

class SerenaBot:

    def __init__(
        self,
        walls: npt.NDArray[np.int_],
        harvest_radius: int,
        vision_radius: int,
        battle_radius: int,
        max_turns: int,
        time_per_turn: float,
    ) -> None:
        self.walls = walls
        self.collect_radius = harvest_radius
        self.vision_radius = vision_radius
        self.battle_radius = battle_radius
        self.max_turns = max_turns
        self.time_per_turn = time_per_turn
        # self.warrior_ants = 0
        # self.food_ants = 0
        # self.exploration_ants = 0

    @property
    def name(self):
        return "serena"
    
    # def find_enemy_hills(self, vision: set[tuple[tuple[int, int], Entity]]) -> list:
    #     enemy_hills = {}
    #     my_hills = {coord for coord, kind in vision if kind == Entity.FRIENDLY_HILL}
    #     for hill in my_hills:
    #         self.walls #0s and 1s
    
    def map_maker(self, goals: list):
        fmap = defaultdict(lambda: float('inf')) # tuple of coordinates, value: distance from closest food
        frontier = deque() # list of coordinates
        for goal in goals:
            fmap[goal] = 0
            frontier.append(goal)

        while len(frontier) > 0:
            coord = frontier.popleft()

            for neighbor in valid_neighbors(*coord, self.walls):
                # if neighbor in self.walls:
                #     continue
                temp_dist = fmap[coord] + 1
                if temp_dist < fmap[neighbor]:
                    fmap[neighbor] = temp_dist
                    frontier.append(neighbor)
        return fmap

    def enough_guards(self, num_ants: int, ants: list, hills: list):
        #strat: 20 min ants are guards, guarding radius = 6
        guards = 0
        guarding_radius = 6
        if num_ants >= 30:
            for ant in ants:
                for hill in hills:
                    if manhattan_dist(ant, hill) <= guarding_radius:
                        guards += 1
            
            if guards < 20:
                return guards
        return -1


    def next_choice(self, ant: tuple[int, int], fmap: defaultdict, claimed_destinations: list):
        valid = [
                v
                for v in valid_neighbors(*ant, self.walls)
                if v not in claimed_destinations
            ]
        # if not valid:
        #     claimed_destinations.add(ant)
        best_value = float('inf')
        next_step = None
        for v in valid:
            if fmap[v] < best_value:
                best_value = fmap[v]
                next_step = v

        return next_step
    
    def find_all_cells(self):
        r, c = self.walls.shape
        all_cells = []
        for row in range(r):
            for col in range(c):
                if self.walls[row, col] == 0:
                    all_cells.append((row, col))

        return all_cells
    

    def final_map(self, explore_map: defaultdict, food_map: defaultdict):
        dijkstra = defaultdict(lambda: float('0'))
        for cell in self.find_all_cells():
            dijkstra[cell] = explore_map[cell] + food_map[cell]
        return dijkstra


    def move_ants(
        self,
        vision: set[tuple[tuple[int, int], Entity]],
        stored_food: int,
    ) -> set[AntMove]:
        my_hills = [coord for coord, kind in vision if kind == Entity.FRIENDLY_HILL]
        claimed_destinations = my_hills
        my_ants = [coord for coord, kind in vision if kind == Entity.FRIENDLY_ANT]
        foods = [coord for coord, kind in vision if kind == Entity.FOOD]
        out = set()

        foodmap = self.map_maker(foods)
        unexplored = []
        for cell in self.find_all_cells():
            if cell not in vision:
                unexplored.append(cell)
        explore_map = self.map_maker(unexplored)

        # if self.enough_guards(len(my_ants), my_ants, my_hills) != -1:
        #     ...

        dijkstra = self.final_map(explore_map, foodmap)
        for ant in my_ants:
            step = self.next_choice(ant, dijkstra, claimed_destinations)
            if step not in claimed_destinations:
                claimed_destinations.append(step)
                out.add((ant, step))
        # print(f'moves: {out}')
        return out

        # if len(ants) > len(foods)


    # def assign_ants(self, vision: set[tuple[tuple[int, int], Entity]], fmap: defaultdict):
    #     ants = {coord for coord, kind in vision if kind == Entity.FRIENDLY_ANT}
    #     foods = [coord for coord, kind in vision if kind == Entity.FOOD]
    #     pairs = {} # food, ant

    #     # claimed_food = set()

    #     # for food in foods:
    #     #     if food not in claimed_food:
                

    #     # for f in food:
    #     #     frontier = [f]
    #     #     visited = set()
    #     #     while len(frontier) > 0:
    #     #         cell = frontier.pop(0)
    #     #         if cell in ants and cell not in used_ants:
    #     #             pairs[f] = cell
    #     #             used_ants.add(cell)
    #     #             break
    #     #         valid = [
    #     #             v
    #     #             for v in valid_neighbors(*cell, self.walls)
    #     #         ]
    #     #         for neighbor in valid:
    #     #             if neighbor in visited:
    #     #                 continue
    #     #             if fmap[neighbor] == fmap[cell] + 1:
    #     #                 frontier.append(neighbor)
    #     #             visited.add(neighbor)

    #     # return pairs