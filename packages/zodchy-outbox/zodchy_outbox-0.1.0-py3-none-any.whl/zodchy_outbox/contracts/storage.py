from dataclasses import dataclass
import typing
import datetime
from zodchy.codex.cqea import Query
from .types import TaskId, MessageId


class LogCreationModel(typing.TypedDict):
    task_id: TaskId
    status: str


class MessageCreationModel(typing.TypedDict):
    id: MessageId
    name: str
    payload: dict


class TaskCreationModel(typing.TypedDict):
    id: TaskId
    message_id: MessageId
    status: str
    scheduled_at: datetime.datetime
    handler_id: str
    handler_settings: dict | None = None
    task_settings: dict | None = None


class TaskUpdatingModel(typing.TypedDict):
    id: TaskId
    status: str
    scheduled_at: datetime.datetime | None = None


class TaskForStatusModel(typing.TypedDict):
    id: TaskId
    handler_id: str
    scheduled_at: datetime.datetime
    handler_settings: dict
    task_settings: dict
    message_name: str
    message_payload: dict


class MessageCreationHandlerContract(typing.Protocol):
    async def __call__(self, message: MessageCreationModel) -> None: ...


class TasksCreationHandlerContract(typing.Protocol):
    async def __call__(self, *tasks: TaskCreationModel) -> None: ...


class TasksUpdatingHandlerContract(typing.Protocol):
    async def __call__(self, *tasks: TaskUpdatingModel) -> None: ...


class TasksForStatusHandlerContract(typing.Protocol):
    async def __call__(
        self,  
        query: Query,
        assure_status: str
    ) -> list[TaskForStatusModel]: ...


class LogsCreationHandlerContract(typing.Protocol):
    async def __call__(self, *logs: LogCreationModel) -> None: ...
