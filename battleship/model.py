
from dataclasses import dataclass
from enum import Enum


class ShipType(int, Enum):
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


@dataclass
class Game:
    player: int
    players: list[Player]
    name: str