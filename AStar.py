from typing import Literal
from math import sqrt
import random

def _round(x: float):
    return int(x + 0.5)

class AStarSolver:
    def __init__(self, maze: dict[tuple[int, int], bool], start: tuple[int, int], end: tuple[int, int], mode: Literal['manhattan', 'diagonal', 'euclidean', 'dijkstra']):
        self.maze = maze

        self.start = start
        self.end = end

        self.open: dict[tuple[int, int], tuple[int, int]] = {self.start: self.start}
        self.closed: dict[tuple[int, int], tuple[int, int]] = dict()
        self.path = []

        self.done1 = False
        self.done2 = False

        self.cost_orthogonal = 10
        self.cost_diagonal = 14

        self.mode: Literal['manhattan', 'diagonal', 'euclidean', 'dijkstra'] = mode

    def set_mode(self, mode: Literal['manhattan', 'diagonal', 'euclidean', 'dijkstra']):
        self.mode = mode

    def update_maze(self, maze: dict[tuple[int, int], bool]):
        self.maze = maze

    def update_start(self, start: tuple[int, int]):
        self.start = start
        self.open = {self.start: self.start}

    def reset(self):
        self.open = {self.start: self.start}
        self.closed.clear()
        self.path.clear()
        self.done1 = False
        self.done2 = False

    def get_path(self, coords: tuple[int, int]):
        if (next_coords := self.closed[coords]) != coords:
            self.path.append(coords)
            self.get_path(next_coords)

        else:
            self.path.append(coords)

        self.done2 = True

    def get_neighbors(self, coords: tuple[int, int], diagonals: bool):
        neighbor_offsets = (
            (-1, -1), (0, -1), (1, -1),
            (1, 0), (1, 1), (0, 1),
            (-1, 1), (-1, 0)
        ) if diagonals else (
            (0, -1), (1, 0), (0, 1), (-1, 0)
        )

        for dx, dy in neighbor_offsets:
            neighbor_pos = (coords[0] + dx, coords[1] + dy)

            # Skip if the neighbor is opened or closed already
            if neighbor_pos in self.closed:
                continue

            # Re-parent the node if the g cost is lower than before
            elif neighbor_pos in self.open:
                if self.get_g(neighbor_pos) > self.get_g(coords) + (self.cost_diagonal if self.is_diagonal(coords, neighbor_pos) else self.cost_orthogonal):
                    self.open[neighbor_pos] = coords

            # Yield the neighbor's pos if it is in the maze and not a wall
            elif neighbor_pos in self.maze and self.maze[neighbor_pos] == False:
                yield (neighbor_pos, coords)

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
        if current_coords in self.open: next_coords = self.open[current_coords]
        else:                           next_coords = self.closed[current_coords]

        while current_coords != next_coords:
            next_coords = current_coords

            if current_coords in self.open:
                current_coords = self.open[current_coords]

            else:
                current_coords = self.closed[current_coords]

            cost += self.cost_diagonal if self.is_diagonal(current_coords, next_coords) else self.cost_orthogonal

        return cost

    def choose_next_tile(self, diagonals: bool):
        if self.end in self.closed:
            self.done1 = True
            return

        min_f = float('inf')
        min_h = float('inf')
        min_coords_f: list[tuple[int, int]] = []
        coords_h: list[tuple[int, int]] = []

        _f = []
        for coords in self.open:
            g = _round(self.get_g(coords))
            h = _round(self.get_h(self.mode, coords))
            f = g + h
            _f.append(f)

            if f < min_f:
                min_f = f
                min_coords_f = [coords]

                if h < min_h:
                    min_h = h
                    coords_h = [coords]

                elif h == min_h:
                    coords_h.append(coords)

            elif f == min_f:
                min_coords_f.append(coords)

                if h < min_h:
                    min_h = h
                    coords_h = [coords]

                elif h == min_h:
                    coords_h.append(coords)

        if len(min_coords_f) == 1:
            self.closed.update({min_coords_f[0]: self.open.pop(min_coords_f[0])})
            self.open.update(self.get_neighbors(min_coords_f[0], diagonals))

        else:
            coords = random.choice(coords_h)
            self.closed.update({coords: self.open.pop(coords)})
            self.open.update(self.get_neighbors(coords, diagonals))
