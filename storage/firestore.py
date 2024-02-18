from battleship.model import Game
from battleship.server import StateUpdater
import firebase_admin
from firebase_admin import firestore

from storage.serializer import deserialize, serialize


class FirestoreUpdater(StateUpdater):
    def __init__(self):
        _ = firebase_admin.initialize_app()
        self.db = firestore.client()
        self.collection = 'battleship'

    def exists(self, id: str) -> bool:
        ref = self.db.collection(self.collection).document(id)
        doc = ref.get()
        return doc.exists

    def get(self, id: str) -> Game:
        ref = self.db.collection(self.collection).document(id)
        doc = ref.get()
        return deserialize(doc.to_dict(), Game)

    def insert(self, game: Game) -> str:
        ref = self.db.collection(self.collection).document()
        ref.set(serialize(game))
        return ref.id

    def update(self, game: Game, id: str) -> Game:
        ref = self.db.collection(self.collection).document(id)
        ref.set(serialize(game))
        return game
