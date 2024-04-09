import pygame, json
from typing import Literal

from AStar import AStarSolver

class Visualizer:
    def __init__(
            self,
            fps: int,
            maze_sizeX: int,
            maze_sizeY: int,
            tileSize: int,
            start: tuple[int, int],
            end: tuple[int, int],
            mode: Literal['manhattan', 'diagonal', 'euclidian', 'dijkstra'],
            outlineWidth: int = 3,
            debug: bool = False
        ):

        pygame.init()
        pygame.display.set_caption('A* Visualizer')
        pygame.display.set_icon(pygame.image.load('A Star.png'))
        self.fps = fps
        self.frame_count = 0

        # Setup
        self.tileSize = tileSize
        self.outlineWidth = outlineWidth

        self.maze_sizeX = maze_sizeX
        self.maze_sizeY = maze_sizeY

        self.screen = pygame.display.set_mode((self.maze_sizeX * self.tileSize, self.maze_sizeY * self.tileSize))

        self.mode: Literal['manhattan', 'diagonal', 'euclidian', 'dijkstra'] = mode

        # Maze init
        self.maze: dict[tuple[int, int], bool] = {(x, y): False for y in range(self.maze_sizeY) for x in range(self.maze_sizeX)}
        self.solver = AStarSolver(self.maze, start, end, self.mode)

        # Pressed keys
        self.keys = {
            'left_mouse_held': False,
            'right_mouse_held': False
        }

        self.debug = debug
        if self.debug:
            self.font = pygame.font.SysFont(None, 32)

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

        start = False

        while True:
            clock.tick(self.fps)

            self.frame_count += 1

            mx, my = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

                if event.type == pygame.KEYDOWN:
                    if (event.key == pygame.K_q and pygame.key.get_mods() & pygame.KMOD_CTRL) or event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        return

                    if event.key == pygame.K_SPACE:
                        start = True

                    if event.key == pygame.K_BACKSPACE:
                        self.solver.reset()
                        start = False

                    if event.key == pygame.K_s:
                        self.save_maze()

                    if event.key == pygame.K_o:
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

            if self.keys['left_mouse_held']:
                mouse_tile_clicked = (mx // self.tileSize, my // self.tileSize)
                self.maze[mouse_tile_clicked] = True
            elif self.keys['right_mouse_held']:
                mouse_tile_clicked = (mx // self.tileSize, my // self.tileSize)
                self.maze[mouse_tile_clicked] = False

            self.screen.fill((255, 255, 255))

            self.draw_maze()

            if start and self.frame_count % 5 == 0:
                if not self.solver.done1:
                    self.solver.choose_next_tile(diagonals = True)

                elif not self.solver.done2:
                    self.solver.get_path(self.solver.end)

            if self.debug:
                for coords in self.solver.open | self.solver.closed:
                    g, h = self.solver.get_g(coords), self.solver.get_h(self.mode, coords)
                    self.screen.blit(self.font.render(
                        str(round(g + h)),
                        True, (255, 0, 255)
                        ), (coords[0] * self.tileSize + 20, coords[1] * self.tileSize + 5)
                    )

                    self.screen.blit(self.font.render(
                        str(round(g)),
                        True, (255, 0, 255)
                        ), (coords[0] * self.tileSize + 20, coords[1] * self.tileSize + 30)
                    )

                    self.screen.blit(self.font.render(
                        str(round(h)),
                        True, (255, 0, 255)
                        ), (coords[0] * self.tileSize + 20, coords[1] * self.tileSize + 55)
                    )

            pygame.display.update()

if __name__ == '__main__':
    Visualizer(
        fps          = 60,
        maze_sizeX   = 20,
        maze_sizeY   = 20,
        tileSize     = 45,
        start        = (1, 1),
        end          = (19, 19),
        mode         = 'dijkstra',
        outlineWidth = 2,
        debug        = False
    ).run()
