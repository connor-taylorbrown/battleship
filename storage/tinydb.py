import queue

from tinydb import JSONStorage, TinyDB, where

from battleship.model import Game, Message, Player
from battleship.server import StateUpdater
from storage.serializer import deserialize, serialize
    

class UpdateListener:
    def __init__(self, logger):
        self.logger = logger
        self.update = queue.Queue(1)
        self.read = queue.Queue(1)
    
    def run(self):
        self.logger.info('Listening for TinyDB updates...')
        while update := self.update.get():
            [updated] = update()
            self.logger.info('Applied update for game %s', updated)
            self.read.put(updated)
            self.logger.info('Consumer has been notified')


class TinyDbUpdater(StateUpdater):
    def __init__(self, listener: UpdateListener, path: str):
        self.db = TinyDB(path)
        self.await_update = listener.update
        self.await_read = listener.read
        
    def exists(self, id: int) -> bool:
        return self.db.contains(doc_id=id)
    
    def get(self, id: int) -> Game:
        return deserialize(self.db.get(doc_id=id), Game)
    
    def insert(self, game: Game) -> int:
        return self.db.insert(serialize(game))
    
    def update(self, game: Game, update: Game) -> Game:
        self.await_update.put(lambda: self.db.update(serialize(update), where('name') == game.name))
        return self.get(self.await_read.get())