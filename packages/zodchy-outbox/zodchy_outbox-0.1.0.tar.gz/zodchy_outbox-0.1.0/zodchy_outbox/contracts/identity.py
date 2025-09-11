import typing

T = typing.TypeVar("T")


class OutboxIdentifiersProviderContract(typing.Protocol[T]):
    async def task_id(self) -> T: ...
    async def message_id(self) -> T: ...
