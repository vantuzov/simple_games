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
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.restart()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.handle_click(event.pos)

    def restart(self) -> None:
        """Начинает новую шахматную партсию."""
        self.board = Board()
        self.selected = None
        self.legal_moves = []
        self.status_message = ""

    def handle_click(self, position: tuple[int, int]) -> None:
        """Обрабатывает выбор фигуры и попытку перемещения."""
        column = position[0] // self.renderer.square_size
        row = position[1] // self.renderer.square_size
        if row >= Board.BOARD_SIZE or column >= Board.BOARD_SIZE:
            return

        clicked = (row, column)
        piece = self.board.get_piece(clicked)

        if self.selected is None:
            if (
                piece is not None
                and piece.color == self.board.current_turn
            ):
                moves = self.board.get_legal_moves(clicked)
                if moves:
                    self.selected = clicked
                    self.legal_moves = moves
            return

        if clicked in self.legal_moves:
            if self.board.move(self.selected, clicked):
                self.status_message = ""
                if self.board.is_checkmate(self.board.current_turn):
                    winner = "Белые" if self.board.current_turn == "black" else "Чёрные"
                    self.status_message = f"Мат. Победили {winner}"
                elif self.board.is_stalemate(self.board.current_turn):
                    self.status_message = "Пат. Ничья"
                elif self.board.is_in_check(self.board.current_turn):
                    self.status_message = "Шах"
        elif piece is not None and piece.color == self.board.current_turn:
            moves = self.board.get_legal_moves(clicked)
            if moves:
                self.selected = clicked
                self.legal_moves = moves
                return
        else:
            self.status_message = "Недопустимый ход"

        self.selected = None
        self.legal_moves = []

    def run(self) -> None:
        """Запускает главный игровой цикл."""
        self.running = True

        while self.running:
            self.handle_events()
            self.draw_board()
            pygame.display.flip()
            self.clock.tick(self.FPS)

        pygame.quit()
