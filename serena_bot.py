from multiprocessing import Queue
from collections import defaultdict
from collections import deque
from random import choice
from board import Entity, neighbors
import numpy as np
import numpy.typing as npt


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
    
    def map_maker(self, goals: list, vision: set[tuple[tuple[int, int], Entity]]):
        fmap = defaultdict(lambda: float('inf')) # tuple of coordinates, value: distance from closest food
        frontier = deque() # list of coordinates
        for goal in goals:
            fmap[goal] = 0
            frontier.append(goal)

        while len(frontier) > 0:
            coord = frontier.popleft()

            for neighbor in valid_neighbors(*coord, self.walls):
                if neighbor in self.walls:
                    continue
                else:
                    temp_dist = fmap[coord] + 1
                    if temp_dist < fmap[neighbor]:
                        fmap[neighbor] = temp_dist
                        frontier.append(neighbor)
        return fmap
    
    
    def assign_ants(self, vision: set[tuple[tuple[int, int], Entity]], fmap: defaultdict):
        ants = {coord for coord, kind in vision if kind == Entity.FRIENDLY_ANT}
        food = [coord for coord, kind in vision if kind == Entity.FOOD]
        pairs = {} # food, ant

        used_ants = set()

        for f in food:
            frontier = [f]
            visited = set()
            while len(frontier) > 0:
                cell = frontier.pop(0)
                if cell in ants and cell not in used_ants:
                    pairs[f] = cell
                    used_ants.add(cell)
                    break
                valid = [
                    v
                    for v in valid_neighbors(*cell, self.walls)
                ]
                for neighbor in valid:
                    if neighbor in visited:
                        continue
                    if fmap[neighbor] == fmap[cell] + 1:
                        frontier.append(neighbor)
                    visited.add(neighbor)

        return pairs


    def next_step(self, pair: tuple[int, int], fmap: defaultdict):
        valid = [
                    v
                    for v in valid_neighbors(*pair[0], self.walls) #tuple is ant, food
                ]
        best_value = float('inf')
        next_step = pair[0]
        for v in valid:
            if fmap[v] < next_step:
                best_value = fmap[v]
                next_step = v

        return next_step

    def move_ants(
        self,
        vision: set[tuple[tuple[int, int], Entity]],
        stored_food: int,
        move_queue: Queue,
    ):
        ants = [coord for coord, kind in vision if kind == Entity.FRIENDLY_ANT]
        foods = [coord for coord, kind in vision if kind == Entity.FOOD]
        fmap = self.map_maker(foods, vision)
        food_pairings = self.assign_ants(vision, fmap)
        for food, ant in food_pairings.items():
            move_queue.put((self.next_step((ant, food), fmap)))

        # if len(ants) > len(foods)