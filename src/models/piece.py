"""Модель шахматной фигуры."""


class Piece:
    """Описывает фигуру и её текущее состояние."""

    def __init__(self, color: str, piece_type: str) -> None:
        """Создаёт фигуру указанного цвета и типа."""
        if color not in ("white", "black"):
            raise ValueError("Цвет фигуры должен быть 'white' или 'black'")

        if piece_type not in ("pawn", "knight", "bishop", "rook", "queen", "king"):
            raise ValueError("Неизвестный тип шахматной фигуры")

        self.color = color
        self.piece_type = piece_type
        self.has_moved = False
