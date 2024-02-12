
from dataclasses import dataclass
from enum import Enum


class Ship(int, Enum):
    DESTROYER = 1
    SUBMARINE = 2
    CRUISER = 3
    BATTLESHIP = 4
    CARRIER = 5


@dataclass
class Status:
    ship: Ship | None
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