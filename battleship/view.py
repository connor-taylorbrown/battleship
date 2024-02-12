from abc import ABC, abstractmethod
from battleship.server import Game, Player, Status, can_move


class BoardView(ABC):
    def __init__(self, active: bool):
        self.active = active

    @abstractmethod
    def view_cell(self, cell: Status):
        pass
    

class PlayerBoard(BoardView):
    def view_cell(self, cell: Status):
        targeted = cell.peg
        ship = cell.ship

        if ship and targeted:
            status = 'X'
        elif ship:
            status = ship.value
        elif targeted:
            status = 'O'
        else:
            status = ''

        return {
            'background': 'square',
            'status': status,
            'target': None
        }
    

class OpponentBoard(BoardView):
    def view_cell(self, cell: Status):
        targeted = cell.peg
        occupied = cell.ship

        if targeted and occupied:
            status = 'X'
        elif targeted:
            status = 'O'
        else:
            status = ''
        
        return {
            'background': 'square',
            'status': status,
            'target': self.active and not targeted
        }
    

class View:
    def render(self, state: Game, viewer: str):
        return {
            **vars(state),
            'canMove': can_move(state, viewer),
            'boards': [self.view_board(player, viewer, state.player != i) for i, player in enumerate(state.players)]
        }

    def view_board(self, player: Player, viewer: str, active: bool):
        if player.id == viewer:
            view = PlayerBoard(active)
        else:
            view = OpponentBoard(active)
        
        board = player.board
        return [
            [
                view.view_cell(c)
                for c in row
            ]
            for row in board
        ]
    