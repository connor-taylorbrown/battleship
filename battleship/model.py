
from dataclasses import dataclass
from enum import Enum


class ShipType(Enum):
    DESTROYER = 1
    SUBMARINE = 2
    CRUISER = 3
    BATTLESHIP = 4
    CARRIER = 5


Vector = tuple[int, int]

@dataclass
class Ship:
    type: ShipType
    bearing: Vector
    offset: int


@dataclass
class Status:
    ship: Ship
    peg: bool


Board = list[list[Status]]


@dataclass
class Player:
    id: str
    board: Board
    sunk: list[ShipType]


@dataclass
class Result(Enum):
    MISS = 1
    HIT = 2
    SINK = 3


@dataclass
class Message:
    result: Result
    ship: ShipType = None


@dataclass
class Game:
    player: int
    players: list[Player]
    finished: bool = False
    message: Message = None
