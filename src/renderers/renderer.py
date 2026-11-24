"""Отрисовщик доски и шахматных фигур."""

import pygame

from src.models.board import Board
from src.models.piece import Piece


class Renderer:
    """Рисует состояние Board без изменения игровой логики."""

    LIGHT_SQUARE = (240, 217, 181)
    DARK_SQUARE = (181, 136, 99)
    SELECTED_SQUARE = (246, 246, 105)
    MOVE_SQUARE = (125, 199, 125)
    LAST_MOVE_SQUARE = (180, 210, 140)

    def __init__(self, board_size: int = 720) -> None:
        """Создаёт отрисовщик с квадратной доской заданного размера."""
        pygame.font.init()
        self.board_size = board_size
        self.square_size = board_size // Board.BOARD_SIZE
        self.piece_font = pygame.font.SysFont("Segoe UI Symbol", 54)
        self.status_font = pygame.font.SysFont("Arial", 24)

    def draw(
        self,
        surface: pygame.Surface,
        board: Board,
        selected: tuple[int, int] | None = None,
        legal_moves: list[tuple[int, int]] | None = None,
        status_message: str = "",
    ) -> None:
        """Отрисовывает доску, фигуры, подсветки и сообщение."""
        if legal_moves is None:
            legal_moves = []

        for row in range(Board.BOARD_SIZE):
            for column in range(Board.BOARD_SIZE):
                position = (row, column)
                color = (
                    self.LIGHT_SQUARE
                    if (row + column) % 2 == 0
                    else self.DARK_SQUARE
                )
                last_move = getattr(board, "last_move", None)
                if last_move is not None:
                    if position in (last_move["start"], last_move["target"]):
                        color = self.LAST_MOVE_SQUARE
                if position == selected:
                    color = self.SELECTED_SQUARE

                pygame.draw.rect(
                    surface,
                    color,
                    (
                        column * self.square_size,
                        row * self.square_size,
                        self.square_size,
                        self.square_size,
                    ),
                )

                if position in legal_moves:
                    pygame.draw.circle(
                        surface,
                        self.MOVE_SQUARE,
                        (
                            column * self.square_size + self.square_size // 2,
                            row * self.square_size + self.square_size // 2,
                        ),
                        self.square_size // 5,
                    )

                piece = board.get_piece(position)
                if piece is not None:
                    self._draw_piece(surface, piece, row, column)

        panel_y = self.board_size
        pygame.draw.rect(
            surface,
            (45, 45, 45),
            (0, panel_y, surface.get_width(), surface.get_height() - panel_y),
        )
        turn_name = "Белые" if board.current_turn == "white" else "Чёрные"
        status = f"Ход: {turn_name}"
        if board.is_in_check(board.current_turn):
            status += " — шах"
        if status_message:
            status = status_message
        text = self.status_font.render(status, True, (255, 255, 255))
        surface.blit(text, (16, panel_y + 24))
        restart = self.status_font.render("R — перезапуск", True, (220, 220, 220))
        surface.blit(restart, (self.board_size - 210, panel_y + 24))

        captured = ", ".join(
            piece.piece_type for piece in getattr(board, "captured_pieces", [])
        )
        if captured:
            captured_text = self.status_font.render(
                "Взято: " + captured,
                True,
                (220, 220, 220),
            )
            surface.blit(captured_text, (16, panel_y + 52))

        history = getattr(board, "move_history", [])
        if history:
            move_number = len(history)
            history_text = self.status_font.render(
                f"Ходов: {move_number}",
                True,
                (220, 220, 220),
            )
            surface.blit(history_text, (self.board_size - 210, panel_y + 52))

    def _draw_piece(
        self,
        surface: pygame.Surface,
        piece: Piece,
        row: int,
        column: int,
    ) -> None:
        """Отрисовывает символ фигуры в своей клетке."""
        symbols = {
            ("white", "king"): "♔",
            ("white", "queen"): "♕",
            ("white", "rook"): "♖",
            ("white", "bishop"): "♗",
            ("white", "knight"): "♘",
            ("white", "pawn"): "♙",
            ("black", "king"): "♚",
            ("black", "queen"): "♛",
            ("black", "rook"): "♜",
            ("black", "bishop"): "♝",
            ("black", "knight"): "♞",
            ("black", "pawn"): "♟",
        }
        text_color = (255, 255, 255) if piece.color == "white" else (20, 20, 20)
        label = symbols[(piece.color, piece.piece_type)]
        text = self.piece_font.render(label, True, text_color)
        text_rect = text.get_rect(
            center=(
                column * self.square_size + self.square_size // 2,
                row * self.square_size + self.square_size // 2,
            )
        )
        surface.blit(text, text_rect)
