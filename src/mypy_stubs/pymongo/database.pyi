from typing import Iterable

from .collection import Collection
from . import MongoClient

class Database(object):
	client: MongoClient

	def __getitem__(self, name: str) -> Collection: ...

	def collection_names(self) -> Iterable[str]: ...

	def drop_collection(self, name: str) -> None: ...
