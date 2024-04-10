from typing import Literal
from math import sqrt
import random

def _round(x: float):
    return int(x + 0.5)

class Node:
    def __init__(self, parent: tuple[int, int]):
        self.parent = parent
        self.g = float('inf')
        self.h = float('inf')

class AStarSolver:
    def __init__(
            self,
            maze: dict[tuple[int, int], bool],
            start: tuple[int, int],
            end: tuple[int, int],
            mode: Literal['manhattan', 'diagonal', 'euclidean', 'dijkstra'],
            diagonals: bool
        ):

        self.maze = maze

        self.start = start
        self.end = end

        self.open: dict[tuple[int, int], Node] = {self.start: Node(parent=self.start)}
        self.closed: dict[tuple[int, int], Node] = dict()
        self.path = []

        self.no_path = False
        self.done1 = False
        self.done2 = False

        self.cost_orthogonal = 10
        self.cost_diagonal = 14

        self.diagonals = diagonals

        self.mode: Literal['manhattan', 'diagonal', 'euclidean', 'dijkstra'] = mode

    def set_mode(self, mode: Literal['manhattan', 'diagonal', 'euclidean', 'dijkstra']):
        self.mode = mode

    def update_maze(self, maze: dict[tuple[int, int], bool]):
        self.maze = maze

    def update_start(self, start: tuple[int, int]):
        self.start = start
        self.open = {self.start: Node(parent=self.start)}

    def reset(self):
        self.open = {self.start: Node(parent=self.start)}
        self.closed.clear()
        self.path.clear()
        self.no_path = False
        self.done1 = False
        self.done2 = False

    def get_path(self, coords: tuple[int, int]):
        if (next_coords := self.closed[coords].parent) != coords:
            self.path.append(coords)
            self.get_path(next_coords)

        else:
            self.path.append(coords)

        self.done2 = True

    def update_neighbors(self, coords: tuple[int, int]):
        neighbor_offsets = (
            (-1, -1), (0, -1), (1, -1),
            (1, 0), (1, 1), (0, 1),
            (-1, 1), (-1, 0)
        ) if self.diagonals else (
            (0, -1), (1, 0), (0, 1), (-1, 0)
        )

        for dx, dy in neighbor_offsets:
            neighbor_pos = (coords[0] + dx, coords[1] + dy)

            # Skip if the neighbor is closed
            if neighbor_pos in self.closed:
                continue

            # Re-parent the node if the g cost is lower than before
            elif neighbor_pos in self.open:
                neighbor_node = self.open[neighbor_pos]
                if neighbor_node.g > (new_g := self.closed[coords].g + (self.cost_diagonal if self.is_diagonal(coords, neighbor_pos) else self.cost_orthogonal)):
                    neighbor_node.parent = coords
                    neighbor_node.g = new_g

            # Update the open list if the new node is simply undiscovered and not a wall
            elif neighbor_pos in self.maze and self.maze[neighbor_pos] == False:
                self.open.update({neighbor_pos: Node(parent=coords)})
                self.open[neighbor_pos].h = self.get_h(self.mode, neighbor_pos)

    def is_diagonal(self, _from: tuple[int, int], _to: tuple[int, int]):
        return (_to[0] - _from[0] != 0) and (_to[1] - _from[1] != 0)

    def get_h(self, mode: Literal['manhattan', 'diagonal', 'euclidean', 'dijkstra'], coords: tuple[int, int]) -> float:
        match mode:
            case 'manhattan':
                return (abs(coords[0] - self.end[0]) + abs(coords[1] - self.end[1])) * self.cost_orthogonal

            case 'diagonal':
                dx = abs(coords[0] - self.end[0])
                dy = abs(coords[1] - self.end[1])
                return self.cost_orthogonal * (dx + dy) + (self.cost_diagonal - 2 * self.cost_orthogonal) * min(dx, dy)

            case 'euclidean':
                return sqrt((self.end[0] - coords[0])**2 + (self.end[1] - coords[1])**2) * self.cost_orthogonal

            case 'dijkstra':
                return 0

    def get_g(self, coords: tuple[int, int]) -> float:
        cost = 0

        current_coords = coords
        if current_coords in self.open: next_coords = self.open[current_coords].parent
        else:                           next_coords = self.closed[current_coords].parent

        while current_coords != next_coords:
            next_coords = current_coords

            if current_coords in self.open:
                current_coords = self.open[current_coords].parent

            else:
                current_coords = self.closed[current_coords].parent

            cost += self.cost_diagonal if self.is_diagonal(current_coords, next_coords) else self.cost_orthogonal

        return cost

    def choose_next_tile(self):
        if not self.open:
            self.no_path = True
            return

        elif self.end in self.closed:
            self.done1 = True
            return

        min_f = float('inf')
        min_f_coords = (0, 0)

        min_h = float('inf')
        min_h_coords: list[tuple[int, int]] = []

        for coords, node in self.open.items():
            if node.g == float('inf'): node.g = self.get_g(coords)
            if node.h == float('inf'): node.h = self.get_h(self.mode, coords)

            f = node.g + node.h

            if f < min_f:
                min_f = f
                min_f_coords = coords

                min_h = node.h
                min_h_coords = [coords]

            elif f == min_f:
                if node.h < min_h:
                    min_h = node.h
                    min_h_coords = [coords]

                elif node.h == min_h:
                    min_h_coords.append(coords)

        if len(min_h_coords) > 1:
            current = random.choice(min_h_coords)
        else:
            current = min_f_coords

        self.closed.update({current: self.open.pop(current)})
        self.update_neighbors(current)
