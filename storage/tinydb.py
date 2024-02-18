import queue

from tinydb import TinyDB
from tinydb.table import Document

from battleship.model import Game
from battleship.server import StateUpdater
from storage.serializer import deserialize, serialize
    

class UpdateListener:
    def __init__(self, logger):
        self.logger = logger
        self.update = queue.Queue(1)
    
    def run(self):
        self.logger.info('Listening for TinyDB updates...')
        while update := self.update.get():
            [updated] = update()
            self.logger.info('Applied update for game %s', updated)


class TinyDbUpdater(StateUpdater):
    def __init__(self, listener: UpdateListener, path: str):
        self.db = TinyDB(path)
        self.await_update = listener.update
        
    def exists(self, id: str) -> bool:
        return self.db.contains(doc_id=int(id))
    
    def get(self, id: str) -> Game:
        return deserialize(self.db.get(doc_id=int(id)), Game)
    
    def insert(self, game: Game) -> str:
        id = self.db.insert(serialize(game))
        return str(id)
    
    def update(self, game: Game, id: str) -> Game:
        self.await_update.put(lambda: self.db.upsert(Document(serialize(game), doc_id=int(id))))
        return game
