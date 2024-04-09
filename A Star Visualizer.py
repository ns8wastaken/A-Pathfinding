import pygame, time, json
from typing import Literal

from AStar_Solver import AStarSolver

class Visualizer:
    def __init__(
            self,
            frame_time: float,
            maze_sizeX: int,
            maze_sizeY: int,
            tileSize: int,
            start: tuple[int, int],
            end: tuple[int, int],
            mode: Literal['manhattan', 'diagonal', 'euclidean', 'dijkstra'],
            diagonals: bool,
            outlineWidth: int = 3,
            debug: bool = False
        ):

        pygame.init()
        pygame.display.set_caption('A* Visualizer')
        self.frame_time = frame_time

        # Setup
        self.tileSize = tileSize
        self.outlineWidth = outlineWidth

        self.maze_sizeX = maze_sizeX
        self.maze_sizeY = maze_sizeY

        self.diagonals = diagonals

        self.screen = pygame.display.set_mode((self.maze_sizeX * self.tileSize, self.maze_sizeY * self.tileSize))

        self.mode = 1 if mode == 'manhattan' else\
                    2 if mode == 'diagonal' else\
                    3 if mode == 'euclidean' else\
                    4

        self.modes: tuple[
            Literal['manhattan'],
            Literal['diagonal'],
            Literal['euclidean'],
            Literal['dijkstra']
        ] = ('manhattan', 'diagonal', 'euclidean', 'dijkstra')

        # Maze init
        self.maze: dict[tuple[int, int], bool] = {(x, y): False for y in range(self.maze_sizeY) for x in range(self.maze_sizeX)}
        self.solver = AStarSolver(self.maze, start, end, self.modes[self.mode])

        # Pressed keys
        self.keys = {
            'left_mouse_held': False,
            'right_mouse_held': False
        }

        # Misc
        self.mode_font = pygame.font.SysFont(None, 30)
        self.debug_font = pygame.font.SysFont(None, 20)
        self.debug = debug

    def save_maze(self):
        with open('maze.json', 'w') as f:
            json.dump({f'{key[0]};{key[1]}': val for key, val in self.maze.items()}, f)

    def load_maze(self):
        with open('maze.json', 'r') as f:
            self.maze.clear()
            for key, val in json.load(f).items():
                key = key.split(';')
                key = (int(key[0]), int(key[1]))
                self.maze[key] = val

    def draw_solver_open(self):
        for x, y in self.solver.open:
            pygame.draw.rect(self.screen, (42, 130, 196), (x * self.tileSize, y * self.tileSize, self.tileSize, self.tileSize))

    def draw_solver_closed(self):
        for x, y in self.solver.closed:
            pygame.draw.rect(self.screen, (49, 4, 107), (x * self.tileSize, y * self.tileSize, self.tileSize, self.tileSize))

    def draw_solver_path(self):
        for coords in self.solver.path:
            pygame.draw.rect(self.screen, (140, 27, 106), (coords[0] * self.tileSize, coords[1] * self.tileSize, self.tileSize, self.tileSize))

    def draw_maze(self):
        self.draw_solver_closed()
        self.draw_solver_open()
        self.draw_solver_path()

        pygame.draw.rect(self.screen, (0, 255, 0), (self.solver.start[0] * self.tileSize, self.solver.start[1] * self.tileSize, self.tileSize, self.tileSize))
        pygame.draw.rect(self.screen, (255, 0, 0), (self.solver.end[0] * self.tileSize, self.solver.end[1] * self.tileSize, self.tileSize, self.tileSize))

        for coords, is_wall in self.maze.items():
            if is_wall:
                # Draw walls
                pygame.draw.rect(self.screen, (0, 0, 0), (coords[0] * self.tileSize, coords[1] * self.tileSize, self.tileSize, self.tileSize))

            else:
                # Draw tile outlines
                pygame.draw.rect(self.screen, (0, 0, 0), (coords[0] * self.tileSize, coords[1] * self.tileSize, self.tileSize, self.tileSize), width=self.outlineWidth)

    def run(self):
        clock = pygame.time.Clock()

        _previous_time = time.time()

        start = False

        while True:
            clock.tick(0)

            dt = time.time() - _previous_time
            if dt > self.frame_time:
                _previous_time = time.time()

            mx, my = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                        pygame.quit()
                        return

                    if event.key == pygame.K_SPACE:
                        start = True

                    if event.key == pygame.K_BACKSPACE:
                        self.solver.reset()
                        start = False

                    if event.key == pygame.K_ESCAPE:
                        self.maze = {(x, y): False for y in range(self.maze_sizeY) for x in range(self.maze_sizeX)}
                        self.solver.reset()
                        self.solver.update_maze(self.maze)
                        start = False

                    if event.key == pygame.K_TAB:
                        self.mode += (-1 if pygame.key.get_mods() & pygame.KMOD_SHIFT else 1)
                        self.mode %= len(self.modes)
                        self.solver.set_mode(self.modes[self.mode])

                    if event.key == pygame.K_d:
                        self.debug = not self.debug

                    if not start:
                        if event.key == pygame.K_s and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                            self.save_maze()

                        if event.key == pygame.K_o and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                            self.load_maze()

                        if event.key == pygame.K_1:
                            tile_hover = (mx // self.tileSize, my // self.tileSize)
                            self.solver.update_start(tile_hover)

                        if event.key == pygame.K_2:
                            tile_hover = (mx // self.tileSize, my // self.tileSize)
                            self.solver.end = tile_hover

                if not start:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            self.keys['left_mouse_held'] = True

                        if event.button == 3:
                            self.keys['right_mouse_held'] = True

                    if event.type == pygame.MOUSEBUTTONUP:
                        if event.button == 1:
                            self.keys['left_mouse_held'] = False
                            self.solver.update_maze(self.maze)

                        if event.button == 3:
                            self.keys['right_mouse_held'] = False
                            self.solver.update_maze(self.maze)

                if event.type == pygame.MOUSEWHEEL and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                    self.outlineWidth += event.y

            if self.keys['left_mouse_held']:
                mouse_tile_clicked = (mx // self.tileSize, my // self.tileSize)
                self.maze[mouse_tile_clicked] = True
            elif self.keys['right_mouse_held']:
                mouse_tile_clicked = (mx // self.tileSize, my // self.tileSize)
                self.maze[mouse_tile_clicked] = False

            self.screen.fill((255, 255, 255))

            self.draw_maze()

            if start and dt > self.frame_time:
                if not self.solver.done1:
                    self.solver.choose_next_tile(diagonals = True)

                elif not self.solver.done2:
                    self.solver.get_path(self.solver.end)

            self.screen.blit(
                self.mode_font.render(
                    'Mode: ' + self.modes[self.mode].replace('_', ' ').title(),
                    True, (200, 125, 50)
                ), (2, 2)
            )

            if self.debug:
                for coords in self.solver.open | self.solver.closed:
                    g, h = self.solver.get_g(coords), self.solver.get_h(self.modes[self.mode], coords)
                    self.screen.blit(self.debug_font.render(
                        str(round(g + h)),
                        True, (255, 0, 255)
                        ), (coords[0] * self.tileSize + 20, coords[1] * self.tileSize + 5)
                    )

                    self.screen.blit(self.debug_font.render(
                        str(round(g)),
                        True, (255, 0, 255)
                        ), (coords[0] * self.tileSize + 20, coords[1] * self.tileSize + 30)
                    )

                    self.screen.blit(self.debug_font.render(
                        str(round(h)),
                        True, (255, 0, 255)
                        ), (coords[0] * self.tileSize + 20, coords[1] * self.tileSize + 55)
                    )

            pygame.display.update()

if __name__ == '__main__':
    Visualizer(
        frame_time   = 0.01,
        maze_sizeX   = 20,
        maze_sizeY   = 20,
        tileSize     = 45,
        start        = (1, 1),
        end          = (18, 18),
        mode         = 'euclidean',
        diagonals    = False,
        outlineWidth = 2,
        debug        = False
    ).run()
