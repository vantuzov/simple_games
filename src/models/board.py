"""Модель шахматной доски и хода фигур."""

from src.models.piece import Piece

Position = tuple[int, int]


class Board:
    """Хранит расположение фигур и выполняет шахматные ходы."""

    BOARD_SIZE = 8

    def __init__(self) -> None:
        """Создаёт доску с начальной расстановкой фигур."""
        self.grid: list[list[Piece | None]] = [
            [None for _ in range(self.BOARD_SIZE)]
            for _ in range(self.BOARD_SIZE)
        ]
        self.current_turn = "white"
        self.last_move: dict[str, Position] | None = None
        self.move_history: list[dict[str, object]] = []
        self.captured_pieces: list[Piece] = []
        self.en_passant_target: Position | None = None
        self.promotion_pending: Position | None = None
        self.setup_initial_position()

    def is_inside(self, row: int, column: int) -> bool:
        """Проверяет, находится ли клетка внутри доски."""
        return 0 <= row < self.BOARD_SIZE and 0 <= column < self.BOARD_SIZE

    def get_piece(self, position: Position) -> Piece | None:
        """Возвращает фигуру на указанной позиции."""
        row, column = position
        if not self.is_inside(row, column):
            return None
        return self.grid[row][column]

    def setup_initial_position(self) -> None:
        """Расставляет фигуры в начальную шахматную позицию."""
        back_rank = (
            "rook",
            "knight",
            "bishop",
            "queen",
            "king",
            "bishop",
            "knight",
            "rook",
        )

        for column, piece_type in enumerate(back_rank):
            self.grid[0][column] = Piece("black", piece_type)
            self.grid[1][column] = Piece("black", "pawn")
            self.grid[6][column] = Piece("white", "pawn")
            self.grid[7][column] = Piece("white", piece_type)

    def get_pseudo_moves(self, position: Position) -> list[Position]:
        """Возвращает геометрически возможные ходы фигуры."""
        row, column = position
        piece = self.get_piece(position)
        if piece is None:
            return []

        if piece.piece_type == "pawn":
            return self._pawn_moves(row, column, piece)
        if piece.piece_type == "knight":
            return self._knight_moves(row, column, piece)
        if piece.piece_type == "bishop":
            return self._sliding_moves(
                row,
                column,
                piece,
                ((-1, -1), (-1, 1), (1, -1), (1, 1)),
            )
        if piece.piece_type == "rook":
            return self._sliding_moves(
                row,
                column,
                piece,
                ((-1, 0), (1, 0), (0, -1), (0, 1)),
            )
        if piece.piece_type == "queen":
            return self._sliding_moves(
                row,
                column,
                piece,
                (
                    (-1, -1),
                    (-1, 1),
                    (1, -1),
                    (1, 1),
                    (-1, 0),
                    (1, 0),
                    (0, -1),
                    (0, 1),
                ),
            )
        if piece.piece_type == "king":
            moves = []
            for row_delta in (-1, 0, 1):
                for column_delta in (-1, 0, 1):
                    if row_delta == 0 and column_delta == 0:
                        continue
                    target = (row + row_delta, column + column_delta)
                    if self._can_move_to(target, piece):
                        moves.append(target)
            for target in self._castling_moves(row, column, piece):
                moves.append(target)
            return moves
        return []

    def get_legal_moves(self, position: Position) -> list[Position]:
        """Возвращает ходы, после которых король не остаётся под шахом."""
        piece = self.get_piece(position)
        if piece is None or piece.color != self.current_turn:
            return []

        legal_moves = []
        for target in self.get_pseudo_moves(position):
            target_piece = self.grid[target[0]][target[1]]
            if (
                target_piece is not None
                and target_piece.piece_type == "king"
            ):
                continue

            captured = self.grid[target[0]][target[1]]
            moving_piece = self.grid[position[0]][position[1]]
            ep_capture = None
            if (
                moving_piece is not None
                and moving_piece.piece_type == "pawn"
                and target == self.en_passant_target
                and target_piece is None
            ):
                ep_row = position[0]
                ep_capture = self.grid[ep_row][target[1]]
                self.grid[ep_row][target[1]] = None
            self.grid[target[0]][target[1]] = moving_piece
            self.grid[position[0]][position[1]] = None

            is_castling = (
                moving_piece is not None
                and moving_piece.piece_type == "king"
                and abs(target[1] - position[1]) == 2
            )
            rook = None
            rook_start = None
            rook_target = None
            if is_castling:
                rook_column = 7 if target[1] == 6 else 0
                rook_target_column = 5 if target[1] == 6 else 3
                rook = self.grid[position[0]][rook_column]
                rook_start = (position[0], rook_column)
                rook_target = (position[0], rook_target_column)
                self.grid[position[0]][rook_column] = None
                self.grid[rook_target[0]][rook_target[1]] = rook

            if not self.is_in_check(piece.color):
                legal_moves.append(target)

            if is_castling:
                self.grid[rook_start[0]][rook_start[1]] = rook
                self.grid[rook_target[0]][rook_target[1]] = None
            if ep_capture is not None:
                self.grid[position[0]][target[1]] = ep_capture
            self.grid[position[0]][position[1]] = moving_piece
            self.grid[target[0]][target[1]] = captured
        return legal_moves

    def move(self, start: Position, target: Position) -> bool:
        """Выполняет разрешённый ход и переключает очередь."""
        if target not in self.get_legal_moves(start):
            return False

        piece = self.grid[start[0]][start[1]]
        captured = self.grid[target[0]][target[1]]
        ep_pawn = None
        if (
            piece is not None
            and piece.piece_type == "pawn"
            and target == self.en_passant_target
            and captured is None
        ):
            ep_pawn = self.grid[start[0]][target[1]]
            captured = ep_pawn
            self.grid[start[0]][target[1]] = None
        if captured is not None:
            self.captured_pieces.append(captured)
        self.grid[target[0]][target[1]] = piece
        self.grid[start[0]][start[1]] = None
        if piece is not None:
            piece.has_moved = True

        if (
            piece is not None
            and piece.piece_type == "king"
            and abs(target[1] - start[1]) == 2
        ):
            rook_column = 7 if target[1] == 6 else 0
            rook_target_column = 5 if target[1] == 6 else 3
            rook = self.grid[start[0]][rook_column]
            self.grid[start[0]][rook_column] = None
            self.grid[start[0]][rook_target_column] = rook
            if rook is not None:
                rook.has_moved = True

        self.en_passant_target = None
        if (
            piece is not None
            and piece.piece_type == "pawn"
            and abs(target[0] - start[0]) == 2
        ):
            middle_row = (target[0] + start[0]) // 2
            self.en_passant_target = (middle_row, target[1])

        if (
            piece is not None
            and piece.piece_type == "pawn"
            and target[0] in (0, 7)
        ):
            self.promotion_pending = target

        self.move_history.append(
            {
                "start": start,
                "target": target,
                "piece": piece,
                "captured": captured,
            }
        )
        self.last_move = {"start": start, "target": target}

        self.current_turn = "black" if self.current_turn == "white" else "white"
        return True

    def get_all_legal_moves(self, color: str) -> list[Position]:
        """Возвращает все легальные ходы для указанного цвета."""
        original_turn = self.current_turn
        self.current_turn = color
        moves = []
        for row in range(self.BOARD_SIZE):
            for column in range(self.BOARD_SIZE):
                piece = self.grid[row][column]
                if piece is not None and piece.color == color:
                    for target in self.get_legal_moves((row, column)):
                        moves.append(target)
        self.current_turn = original_turn
        return moves

    def is_checkmate(self, color: str) -> bool:
        """Проверяет, объявлен ли мат указанному королю."""
        return self.is_in_check(color) and not self.get_all_legal_moves(color)

    def is_stalemate(self, color: str) -> bool:
        """Проверяет, возник ли пат для указанного цвета."""
        return not self.is_in_check(color) and not self.get_all_legal_moves(color)

    def find_king(self, color: str) -> Position | None:
        """Находит позицию короля указанного цвета."""
        for row in range(self.BOARD_SIZE):
            for column in range(self.BOARD_SIZE):
                piece = self.grid[row][column]
                if (
                    piece is not None
                    and piece.color == color
                    and piece.piece_type == "king"
                ):
                    return row, column
        return None

    def is_square_attacked(
        self,
        position: Position,
        attacker_color: str,
    ) -> bool:
        """Проверяет, атакуется ли клетка фигурами указанного цвета."""
        row, column = position
        pawn_direction = -1 if attacker_color == "white" else 1

        for column_delta in (-1, 1):
            pawn_row = row - pawn_direction
            pawn_column = column - column_delta
            if not self.is_inside(pawn_row, pawn_column):
                continue
            piece = self.grid[pawn_row][pawn_column]
            if (
                piece is not None
                and piece.color == attacker_color
                and piece.piece_type == "pawn"
            ):
                return True

        knight_offsets = (
            (-2, -1),
            (-2, 1),
            (-1, -2),
            (-1, 2),
            (1, -2),
            (1, 2),
            (2, -1),
            (2, 1),
        )
        for row_delta, column_delta in knight_offsets:
            target = (row + row_delta, column + column_delta)
            if self.is_inside(*target):
                piece = self.get_piece(target)
                if (
                    piece is not None
                    and piece.color == attacker_color
                    and piece.piece_type == "knight"
                ):
                    return True

        for row_delta, column_delta in (
            (-1, -1),
            (-1, 1),
            (1, -1),
            (1, 1),
        ):
            if self._attacker_found(
                position,
                attacker_color,
                row_delta,
                column_delta,
                ("bishop", "queen"),
            ):
                return True

        for row_delta, column_delta in (
            (-1, 0),
            (1, 0),
            (0, -1),
            (0, 1),
        ):
            if self._attacker_found(
                position,
                attacker_color,
                row_delta,
                column_delta,
                ("rook", "queen"),
            ):
                return True

        for row_delta in (-1, 0, 1):
            for column_delta in (-1, 0, 1):
                if row_delta == 0 and column_delta == 0:
                    continue
                target = (row + row_delta, column + column_delta)
                if self.is_inside(*target):
                    piece = self.get_piece(target)
                    if (
                        piece is not None
                        and piece.color == attacker_color
                        and piece.piece_type == "king"
                    ):
                        return True
        return False

    def is_in_check(self, color: str) -> bool:
        """Проверяет, находится ли король указанного цвета под шахом."""
        king_position = self.find_king(color)
        if king_position is None:
            return False
        opponent = "black" if color == "white" else "white"
        return self.is_square_attacked(king_position, opponent)

    def _pawn_moves(
        self,
        row: int,
        column: int,
        piece: Piece,
    ) -> list[Position]:
        """Возвращает ходы пешки."""
        moves = []
        direction = -1 if piece.color == "white" else 1
        start_row = 6 if piece.color == "white" else 1

        forward = (row + direction, column)
        if self.is_inside(*forward) and self.get_piece(forward) is None:
            moves.append(forward)
            double_forward = (row + 2 * direction, column)
            if row == start_row and self.get_piece(double_forward) is None:
                moves.append(double_forward)

        for column_delta in (-1, 1):
            target = (row + direction, column + column_delta)
            target_piece = self.get_piece(target)
            if (
                self.is_inside(*target)
                and target_piece is not None
                and target_piece.color != piece.color
            ):
                moves.append(target)
            if (
                self.is_inside(*target)
                and target_piece is None
                and (target[0], target[1]) == self.en_passant_target
            ):
                adjacent = self.get_piece((row, target[1]))
                if (
                    adjacent is not None
                    and adjacent.color != piece.color
                    and adjacent.piece_type == "pawn"
                ):
                    moves.append(target)
        return moves

    def _castling_moves(
        self,
        row: int,
        column: int,
        king: Piece,
    ) -> list[Position]:
        """Возвращает доступные ходы для рокировки."""
        moves = []
        if king.has_moved or self.is_in_check(king.color):
            return moves

        for rook_column, target_column, between in (
            (7, 6, (5, 6)),
            (0, 2, (1, 2, 3)),
        ):
            rook = self.grid[row][rook_column]
            if (
                rook is None
                or rook.piece_type != "rook"
                or rook.color != king.color
                or rook.has_moved
            ):
                continue
            if any(self.grid[row][cell] is not None for cell in between):
                continue

            king_path = (
                (row, column),
                (row, column + 1),
                (row, target_column),
            )
            if target_column == 2:
                king_path = (
                    (row, column),
                    (row, column - 1),
                    (row, target_column),
                )
            opponent = "black" if king.color == "white" else "white"
            if any(
                self.is_square_attacked(square, opponent)
                for square in king_path
            ):
                continue
            moves.append((row, target_column))
        return moves

    def promote_pawn(self, piece_type: str) -> bool:
        """Превращает пешку в выбранную фигуру."""
        if (
            self.promotion_pending is None
            or piece_type not in ("queen", "rook", "bishop", "knight")
        ):
            return False
        row, column = self.promotion_pending
        pawn = self.grid[row][column]
        if pawn is None or pawn.piece_type != "pawn":
            return False
        pawn.piece_type = piece_type
        self.promotion_pending = None
        return True

    def _knight_moves(
        self,
        row: int,
        column: int,
        piece: Piece,
    ) -> list[Position]:
        """Возвращает ходы коня."""
        moves = []
        offsets = (
            (-2, -1),
            (-2, 1),
            (-1, -2),
            (-1, 2),
            (1, -2),
            (1, 2),
            (2, -1),
            (2, 1),
        )
        for row_delta, column_delta in offsets:
            target = (row + row_delta, column + column_delta)
            if self._can_move_to(target, piece):
                moves.append(target)
        return moves

    def _sliding_moves(
        self,
        row: int,
        column: int,
        piece: Piece,
        directions: tuple[tuple[int, int], ...],
    ) -> list[Position]:
        """Возвращает ходы фигур, перемещающихся по прямой."""
        moves = []
        for row_delta, column_delta in directions:
            target_row = row + row_delta
            target_column = column + column_delta

            while self.is_inside(target_row, target_column):
                target = (target_row, target_column)
                target_piece = self.get_piece(target)
                if target_piece is None:
                    moves.append(target)
                else:
                    if target_piece.color != piece.color:
                        moves.append(target)
                    break

                target_row += row_delta
                target_column += column_delta
        return moves

    def _can_move_to(self, target: Position, piece: Piece) -> bool:
        """Проверяет свободную или вражескую цель для фигуры."""
        if not self.is_inside(*target):
            return False
        target_piece = self.get_piece(target)
        return target_piece is None or target_piece.color != piece.color

    def _attacker_found(
        self,
        position: Position,
        attacker_color: str,
        row_delta: int,
        column_delta: int,
        attacker_types: tuple[str, str],
    ) -> bool:
        """Ищет дальнобойную фигуру в заданном направлении."""
        row, column = position
        target_row = row + row_delta
        target_column = column + column_delta

        while self.is_inside(target_row, target_column):
            piece = self.grid[target_row][target_column]
            if piece is not None:
                return (
                    piece.color == attacker_color
                    and piece.piece_type in attacker_types
                )
            target_row += row_delta
            target_column += column_delta
        return False
