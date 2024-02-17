import queue
import jsonpickle

from tinydb import JSONStorage, TinyDB, where
from tinydb_serialization import Serializer, SerializationMiddleware

from battleship.model import Game, Message, Player
from battleship.server import StateUpdater


class PlayerSerializer(Serializer):
    OBJ_CLASS = Player

    def encode(self, obj):
        return jsonpickle.encode(obj)
    
    def decode(self, s):
        return jsonpickle.decode(s)
    

class MessageSerializer(Serializer):
    OBJ_CLASS = Message

    def encode(self, obj):
        return jsonpickle.encode(obj)
    
    def decode(self, s):
        return jsonpickle.decode(s)
    

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
        serialization = SerializationMiddleware(JSONStorage)
        serialization.register_serializer(PlayerSerializer(), 'Player')
        serialization.register_serializer(MessageSerializer(), 'Message')
        self.db = TinyDB(path, storage=serialization)
        self.await_update = listener.update
        self.await_read = listener.read
        
    def exists(self, id: int) -> bool:
        return self.db.contains(doc_id=id)
    
    def get(self, id: int) -> Game:
        return Game(**self.db.get(doc_id=id))
    
    def insert(self, game: Game) -> int:
        return self.db.insert(vars(game))
    
    def update(self, game: Game, update: dict) -> Game:
        self.await_update.put(lambda: self.db.update(update, where('name') == game.name))
        return self.get(self.await_read.get())
