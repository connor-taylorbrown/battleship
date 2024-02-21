from abc import ABC, abstractmethod
from dataclasses import dataclass
from battleship.model import Message, Result, Ship
from battleship.server import Game, Player, Status, can_move, has_won, player


class BoardView(ABC):
    def __init__(self, style: dict):
        self.style = style

    @abstractmethod
    def view_cell(self, cell: Status):
        pass

    def peg_tile(self, targeted: bool, occupied: bool):
        if targeted and occupied:
            return self.style['PEG_HIT']
        elif targeted:
            return self.style['PEG_MISS']
        else:
            return self.style['PEG_NONE']

    def ship_tile(self, ship: Ship):
        name = ship.type.name.lower()
        classes = [f'cell-{name}-{ship.offset}']
        if ship.bearing == (0, 1):
            classes.append(self.style['SHIP_UP'])
        elif ship.bearing == (0, -1):
            classes.append(self.style['SHIP_DOWN'])
        elif ship.bearing == (-1, 0):
            classes.append(self.style['SHIP_LEFT'])
        
        return ' '.join(classes)
    

class PlayerBoard(BoardView):
    def view_cell(self, cell: Status):
        targeted = cell.peg
        ship = cell.ship

        return {
            'background': self.ship_tile(ship) if ship else self.style['EMPTY'],
            'status': self.peg_tile(targeted, ship),
            'target': None
        }
    

class OpponentBoard(BoardView):
    def __init__(self, style: dict, active: bool):
        super().__init__(style)
        self.active = active

    def view_cell(self, cell: Status):
        targeted = cell.peg
        occupied = cell.ship
        
        return {
            'background': self.style['EMPTY'],
            'status': self.peg_tile(targeted, occupied),
            'target': self.active and not targeted
        }
    

def message(message: Message):
    if not message:
        return None
    elif message.result is Result.SINK:
        return f'{message.ship.name.title()} sunk!'
    elif message.result is Result.HIT:
        return 'Hit!'
    elif message.result is Result.MISS:
        return 'Miss!'
    

def viewer_won(state: Game, viewer: str):
    players = [player for player in state.players if player.id == viewer]
    if players:
        [player] = players
        return has_won(player)
    
    return False


def prompt(state: Game, viewer: str):
    if viewer_won(state, viewer):
        return 'You win!'
    elif state.finished:
        return 'Game over'
    elif can_move(state, viewer):
        return 'Your move'
    else:
        return f'{player(state).name.title()} to move'
    

@dataclass
class PlayerView:
    board: list[list[dict]]
    sunk: list[str]
    

class View:
    def __init__(self, style: dict):
        self.style = style

    def render(self, state: Game, viewer: str):
        return {
            **vars(state),
            'message': message(state.message),
            'prompt': prompt(state, viewer),
            'players': [self.view_board(state, player, viewer, i) for i, player in enumerate(state.players)]
        }

    def view_board(self, state: Game, player: Player, viewer: str, i: int):
        active = state.player != i and not state.finished
        if player.id == viewer:
            view = PlayerBoard(self.style)
        else:
            view = OpponentBoard(self.style, active)
        
        board = player.board
        return PlayerView(
            sunk=[self.style['PEG_HIT'] for _ in player.sunk],
            board=[
                [
                    view.view_cell(c)
                    for c in row
                ]
                for row in board
            ])
    