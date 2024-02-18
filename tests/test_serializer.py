from battleship.model import Board, Ship, ShipType, Status
from storage.serializer import deserialize, serialize


def ship(offset):
    return Ship(ShipType(1), (1, 0), offset)


def serialize_ship(offset):
    return {'type': 1, 'bearing': [1, 0], 'offset': offset}


def board():
    return [[Status(ship=ship(x), peg=True) for x in range(5)] for _ in range(5)]


def serialize_board():
    return [
        {'row': [{'ship': serialize_ship(x), 'peg': True} for x in range(5)]}
        for _ in range(5)
    ]


def test_serialize():
    test_cases = [
        (None, None),
        (1, 1),
        (ShipType(1), 1),   # Serialize enum correctly
        ((1, 0), [1, 0]),   # Serialize tuple correctly
        (ship(2), serialize_ship(2)),   # Serialize class correctly
        (board(), serialize_board())    # Serialize nested list correctly
    ]

    for object, expected in test_cases:
        got = serialize(object)

        assert got == expected


def test_deserialize():
    test_cases = [
        (None, None, None),
        (1, int, 1),
        (1, ShipType, ShipType(1)),
        ([1, 0], tuple[int, int], (1, 0)),
        (serialize_ship(2), Ship, ship(2)),
        (serialize_board(), Board, board())
    ]

    for serializable, hint, expected in test_cases:
        got = deserialize(serializable, hint)

        assert got == expected
