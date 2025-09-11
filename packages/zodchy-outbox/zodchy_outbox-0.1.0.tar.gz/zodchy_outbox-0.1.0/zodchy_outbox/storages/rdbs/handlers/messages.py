import typing
import sqlalchemy

from .generic import RegistrationHandler
from ....contracts.storage import MessageCreationModel
from ....contracts.types import MessageId

T = typing.TypeVar("T")


class MessageCreationHandler(RegistrationHandler):
    async def __call__(self, message: MessageCreationModel) -> MessageId:
        await self._transaction.execute(
            sqlalchemy.insert(self._schema.messages).values(
                id=message["id"],
                name=message["name"],
                payload=message["payload"],
            )
        )
        return message["id"]
