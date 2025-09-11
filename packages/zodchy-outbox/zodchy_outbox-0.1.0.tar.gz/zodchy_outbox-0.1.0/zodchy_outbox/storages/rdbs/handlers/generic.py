import typing
import abc

from zodchy_alchemy.contracts import WriteConnectionContract
from zodchy_alchemy.contracts import EngineContract

from ..config import Metadata
from ..internals.schema import Schema

T = typing.TypeVar("T")


class RegistrationHandler(abc.ABC):
    def __init__(
        self, transaction: WriteConnectionContract, metadata: Metadata | None = None
    ):
        self._schema = Schema((metadata or Metadata()).schema)
        self._transaction = transaction


class ProcessingHandler(abc.ABC):
    def __init__(self, engine: EngineContract, metadata: Metadata | None = None):
        self._schema = Schema((metadata or Metadata()).schema)
        self._engine = engine
