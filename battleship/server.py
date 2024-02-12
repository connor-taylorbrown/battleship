from abc import ABC, abstractmethod
import random
import uuid

from battleship.model import Board, Game, Player, Ship, Status


class StateUpdater(ABC):
    @abstractmethod
    def exists(self, id: int) -> bool:
        pass
    
    @abstractmethod
    def get(self, id: int) -> Game:
        pass
    
    @abstractmethod
    def insert(self, game: Game) -> int:
        pass

    @abstractmethod
    def update(self, game: Game, update: dict) -> Game:
        pass


def new_board() -> Board:
    width = 10
    height = 10
    return Board([[Status(ship=None, peg=False) for _ in range(width)] for _ in range(height)])


Vector = tuple[int, int]
def generate_position(board: Board) -> Vector:
    row = random.randint(0, len(board) - 1)
    col = random.randint(0, len(board[0]) - 1)
    return col, row


def generate_direction() -> Vector:
    direction = random.randint(0, 3)
    total, odd = 2 * (direction >> 1) - 1, direction & 1
    return total if not odd else 0, total if odd else 0


ShipPrototype = tuple[Ship, int]


def try_add_ship(board: Board, ship: ShipPrototype, position: Vector, direction: Vector) -> Board:
    type, length = ship
    x0, y0 = position
    vx, vy = direction
    if not (0 <= y0+length*vy < len(board)):
        return board
    
    if not (0 <= x0+length*vx < len(board[0])):
        return board

    new_board = list(map(list, board))
    for i in range(length):
        row = new_board[y0+i*vy]
        x = x0+i*vx
        if row[x].ship is not None:
            return board
        
        row[x] = Status(ship=type, peg=False)

    return new_board


class InitializationException(Exception):
    pass


def setup_board(board: Board, ships: list[ShipPrototype]):
    def add_ship(board, ship):
        for _ in range(100):
            # This function is random and not guaranteed to succeed. Limit iterations
            position = generate_position(board)
            direction = generate_direction()
            new_board = try_add_ship(board, ship, position, direction)
            if new_board != board:
                return new_board
        
        raise InitializationException('Could not initialize board as requested')
    
    new_board = board
    for ship in ships:
        new_board = add_ship(new_board, ship)
    
    return new_board


def create_board():
    ships = [
        (Ship.DESTROYER, 5),
        (Ship.SUBMARINE, 4),
        (Ship.CRUISER, 3),
        (Ship.BATTLESHIP, 3),
        (Ship.CARRIER, 2),
    ]
    return setup_board(new_board(), ships)


def next_player(state: Game) -> int:
    players = len(state.players)
    return (state.player + 1) % players


def is_started(state: Game) -> bool:
    return len(state.players) == 2


def can_move(state: Game, viewer: str) -> bool:
    return viewer == state.players[state.player].id


class GameServer:
    def __init__(self, games: StateUpdater, logger):
        self.games = games
        self.logger = logger

    def log(func):
        def inner(self: 'GameServer', *args, **kwargs):
            logger = self.logger
            result = func(self, *args, **kwargs)
            logger.debug('Called method %s (args %s kwargs %s), got result %s', func.__name__, args, kwargs, result)

            return result
        
        return inner

    def insert_state(func):
        def inner(self: 'GameServer', *args, **kwargs):
            game = func(self, *args, **kwargs)
            return self.games.insert(game)
        
        return inner
    
    def update_state(func):
        def inner(self: 'GameServer', game: Game, *args, **kwargs):
            update = func(self, game, *args, **kwargs)
            if update:
                return self.games.update(game, update)
            else:
                return game
        
        return inner
    
    @log
    def exists(self, game: int) -> bool:
        return self.games.exists(game)
    
    @log
    def get(self, game: int) -> Game:
        return self.games.get(game)

    @insert_state
    @log
    def new_game(self) -> Game:
        return Game(player=0, players=[], name=str(uuid.uuid4()))
    
    @update_state
    @log
    def join(self, state: Game, player: str) -> Game:
        players = state.players
        if len(players) < 2 and player not in [p.id for p in players]:
            return {
                'players': players + [Player(id=player, board=create_board())]
            }
    
    @update_state
    @log
    def target(self, state: Game, board: int, position: Vector) -> Game:
        players = state.players
        board = players[board].board
        x, y = position
        board[y][x].peg = True
        return {
            'player': next_player(state),
            'players': players
        }
