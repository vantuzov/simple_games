"""Класс приложения шахмат."""

import pygame

from src.models.board import Board
from src.renderers.renderer import Renderer


class App:
    """Управляет окном Pygame и главным игровым циклом."""

    BOARD_SIZE_PIXELS = 720
    WINDOW_HEIGHT = 800
    WINDOW_WIDTH = 800
    BOARD_SIZE = 8
    FPS = 60
    LIGHT_SQUARE = (240, 217, 181)
    DARK_SQUARE = (181, 136, 99)

    def __init__(self) -> None:
        """Инициализирует Pygame и создаёт игровое окно."""
        pygame.init()
        self.screen = pygame.display.set_mode(
            (self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
        )
        pygame.display.set_caption("Шахматы")
        self.clock = pygame.time.Clock()
        self.running = False
        self.board = Board()
        self.renderer = Renderer(self.BOARD_SIZE_PIXELS)
        self.selected: tuple[int, int] | None = None
        self.legal_moves: list[tuple[int, int]] = []
        self.status_message = ""

    def draw_board(self) -> None:
        """Отрисовывает доску с начальной расстановкой фигур."""
        self.renderer.draw(
            self.screen,
            self.board,
            self.selected,
            self.legal_moves,
            self.status_message,
        )

    def handle_events(self) -> None:
        """Обрабатывает события окна Pygame."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def run(self) -> None:
        """Запускает главный игровой цикл."""
        self.running = True

        while self.running:
            self.handle_events()
            self.draw_board()
            pygame.display.flip()
            self.clock.tick(self.FPS)

        pygame.quit()
