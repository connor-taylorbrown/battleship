from battleship.model import Ship
from battleship.server import ShipType, Status, new_board, setup_board, try_add_ship


def test_try_add_ship():
    submarine = ShipType(2), 3
    cruiser = ShipType(3), 3

    def with_ship_at(board, origin, direction, ship):
        x0, y0 = origin
        vx, vy = direction
        type, length = ship
        for i in range(length):
            board[y0+vy*i][x0+vx*i] = Status(ship=Ship(type=type, bearing=direction, offset=i), peg=False)

        return board

    def board_with_submarine():
        return with_ship_at(new_board(), (5, 5), (0, 1), submarine)

    test_cases = [
        (new_board(), submarine, (5, 5), (0, 1), with_ship_at(new_board(), (5, 5), (0, 1), submarine)),
        (new_board(), submarine, (8, 0), (1, 0), new_board()),
        (new_board(), submarine, (0, 8), (0, 1), new_board()),
        (new_board(), submarine, (0, 2), (0, -1), new_board()),
        (new_board(), submarine, (2, 0), (-1, 0), new_board()),
        (board_with_submarine(), cruiser, (4, 5), (1, 0), board_with_submarine()),
        (board_with_submarine(), cruiser, (4, 5), (0, 1), with_ship_at(board_with_submarine(), (4, 5), (0, 1), cruiser))
    ]

    for board, length, origin, direction, expectedBoard in test_cases:
        gotBoard = try_add_ship(board, length, origin, direction)

        assert gotBoard == expectedBoard


def test_setup_board():
    submarine = (ShipType(2), 3)
    cruiser = (ShipType(3), 3)

    def count_spaces(board, ships):
        spaces = [cell.ship and cell.ship.type for row in board for cell in row]
        return {(ship, length): spaces.count(ship) for ship, length in ships}

    test_cases = [
        (new_board(), [submarine, cruiser], {submarine: 3, cruiser: 3})
    ]

    for board, ships, expectedCount in test_cases:
        gotBoard = setup_board(board, ships)

        assert count_spaces(gotBoard, ships) == expectedCount
