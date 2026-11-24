"""Класс приложения шахмат."""

import pygame


class App:
    """Управляет окном Pygame и главным игровым циклом."""

    WINDOW_SIZE = 800
    BOARD_SIZE = 8
    FPS = 60
    LIGHT_SQUARE = (240, 217, 181)
    DARK_SQUARE = (181, 136, 99)

    def __init__(self) -> None:
        """Инициализирует Pygame и создаёт игровое окно."""
        pygame.init()
        self.screen = pygame.display.set_mode(
            (self.WINDOW_SIZE, self.WINDOW_SIZE)
        )
        pygame.display.set_caption("Шахматы")
        self.clock = pygame.time.Clock()
        self.running = False

    def draw_board(self) -> None:
        """Отрисовывает пустую шахматную доску."""
        square_size = self.WINDOW_SIZE // self.BOARD_SIZE

        for row in range(self.BOARD_SIZE):
            for column in range(self.BOARD_SIZE):
                color = (
                    self.LIGHT_SQUARE
                    if (row + column) % 2 == 0
                    else self.DARK_SQUARE
                )
                pygame.draw.rect(
                    self.screen,
                    color,
                    (
                        column * square_size,
                        row * square_size,
                        square_size,
                        square_size,
                    ),
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

