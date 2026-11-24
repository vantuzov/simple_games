"""Тесты базовой шахматной модели."""

import unittest

from src.models.board import Board
from src.models.piece import Piece


class BoardTests(unittest.TestCase):
    """Проверяет начальную расстановку и основные ходы."""

    def test_initial_position_has_32_pieces(self) -> None:
        board = Board()
        pieces = [
            piece
            for row in board.grid
            for piece in row
            if piece is not None
        ]
        self.assertEqual(len(pieces), 32)

    def test_white_pawn_can_move_forward_two_squares(self) -> None:
        board = Board()
        moves = board.get_pseudo_moves((6, 4))
        self.assertIn((5, 4), moves)
        self.assertIn((4, 4), moves)

    def test_white_pawn_cannot_jump_over_piece(self) -> None:
        board = Board()
        board.grid[5][4] = board.grid[6][4]
        board.grid[6][4] = None
        board.grid[4][4] = board.grid[1][0]
        board.grid[1][0] = None

        moves = board.get_pseudo_moves((5, 4))
        self.assertNotIn((3, 4), moves)

    def test_move_changes_turn(self) -> None:
        board = Board()
        self.assertTrue(board.move((6, 4), (4, 4)))
        self.assertEqual(board.current_turn, "black")

    def test_piece_cannot_capture_king(self) -> None:
        board = Board()
        board.grid = [
            [None for _ in range(8)]
            for _ in range(8)
        ]
        board.grid[7][4] = board.grid[0][4] = None

        white_king = Piece("white", "king")
        black_rook = Piece("black", "rook")
        board.grid[7][4] = white_king
        board.grid[7][0] = black_rook
        board.current_turn = "black"

        self.assertNotIn((7, 4), board.get_legal_moves((7, 0)))

    def test_check_detection_by_rook(self) -> None:
        board = Board()
        board.grid = [
            [None for _ in range(8)]
            for _ in range(8)
        ]
        board.grid[7][4] = Piece("white", "king")
        board.grid[7][0] = Piece("black", "rook")

        self.assertTrue(board.is_in_check("white"))

    def test_pawn_move_changes_piece_position(self) -> None:
        board = Board()

        self.assertTrue(board.move((6, 4), (4, 4)))
        self.assertIsNone(board.grid[6][4])
        self.assertEqual(board.grid[4][4].piece_type, "pawn")

    def test_king_cannot_move_into_check(self) -> None:
        board = Board()
        board.grid = [[None for _ in range(8)] for _ in range(8)]
        board.grid[7][4] = Piece("white", "king")
        board.grid[6][5] = Piece("black", "rook")

        self.assertNotIn((7, 5), board.get_legal_moves((7, 4)))

    def test_another_piece_can_block_check(self) -> None:
        board = Board()
        board.grid = [[None for _ in range(8)] for _ in range(8)]
        board.grid[7][4] = Piece("white", "king")
        board.grid[7][0] = Piece("black", "rook")
        board.grid[7][2] = Piece("white", "rook")
        board.current_turn = "white"

        self.assertIn((7, 1), board.get_legal_moves((7, 2)))

    def test_position_with_legal_move_is_not_mate(self) -> None:
        board = Board()
        board.grid = [[None for _ in range(8)] for _ in range(8)]
        board.grid[7][4] = Piece("white", "king")
        board.grid[7][0] = Piece("black", "rook")

        self.assertGreater(len(board.get_all_legal_moves("white")), 0)


if __name__ == "__main__":
    unittest.main()
