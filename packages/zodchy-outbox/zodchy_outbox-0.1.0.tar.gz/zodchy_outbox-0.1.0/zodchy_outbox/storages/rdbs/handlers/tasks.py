import abc
import typing
import sqlalchemy
from zodchy.codex.cqea import Query
from zodchy_alchemy import QueryAssembler
from zodchy_alchemy.adapters.cqea import QueryAdapter

from ....contracts.storage import (
    TaskCreationModel,
    TaskUpdatingModel,
)
from ....contracts.types import TaskId
from .generic import RegistrationHandler, ProcessingHandler


class Log(typing.TypedDict):
    task_id: TaskId
    status: str


class TasksOperation(RegistrationHandler, abc.ABC):
    async def _save_logs(self, *logs: Log):
        await self._transaction.execute(
            sqlalchemy.insert(self._schema.logs).values(logs)
        )


class TasksCreationHandler(TasksOperation):
    async def __call__(self, *tasks: TaskCreationModel):
        _tasks = []
        _logs = []
        for task in tasks:
            _tasks.append(
                dict(
                    id=task["id"],
                    message_id=task["message_id"],
                    handler_id=task["handler_id"],
                    status=task["status"],
                    scheduled_at=task["scheduled_at"],
                    handler_settings=task["handler_settings"] if task["handler_settings"] is not None else sqlalchemy.null(),
                    task_settings=task["task_settings"] if task["task_settings"] is not None else sqlalchemy.null(),
                )
            )
            _logs.append(
                dict(
                    task_id=task["id"],
                    status=task["status"],
                )
            )
        await self._transaction.execute(
            sqlalchemy.insert(self._schema.tasks).values(_tasks)
        )
        await self._save_logs(*_logs)


class TasksUpdatingHandler(TasksOperation):
    async def __call__(self, *tasks: TaskUpdatingModel):
        statuses = set()
        scheduled_ats = set()
        for task in tasks:
            statuses.add(task["status"])
            if "scheduled_at" in task:
                scheduled_ats.add(task["scheduled_at"])

        data = tasks
        if len(statuses) == 1:
            data = dict(
                status=statuses.pop(),
                scheduled_at=scheduled_ats.pop() if len(scheduled_ats) > 0 else None,
            )

        if type(data) is dict:
            await self._write_one(data, [task["id"] for task in tasks])
        elif type(data) is list:
            await self._write_many(data)

    async def _write_one(self, data: dict, ids: list[TaskId]):
        await self._transaction.execute(
            sqlalchemy.update(self._schema.tasks)
            .where(self._schema.tasks.c.id.in_(ids))
            .values(**{k: v for k, v in data.items() if v is not None})
        )

    async def _write_many(self, data: list[dict]):
        for row in data:
            _id = row.pop("id")
            await self._transaction.execute(
                sqlalchemy.update(self._schema.tasks)
                .where(self._schema.tasks.c.id == _id)
                .values(row)
            )


class ReadTasksForStatusHandler(ProcessingHandler):
    async def __call__(self, query: Query, assure_status: str):
        async with self._engine.connect() as connection:
            sql_query = (
                sqlalchemy.select(
                    self._schema.tasks.c.id,
                    self._schema.tasks.c.scheduled_at,
                    self._schema.tasks.c.handler_id,
                    self._schema.tasks.c.handler_settings,
                    self._schema.tasks.c.task_settings,
                    self._schema.messages.c.name.label("message_name"),
                    self._schema.messages.c.payload.label("message_payload"),
                )
                .join(
                    self._schema.messages,
                    self._schema.tasks.c.message_id == self._schema.messages.c.id,
                    isouter=True,
                )
            )
            adapter = QueryAdapter(
                default_table=self._schema.tasks,
            )
            assembler = QueryAssembler(sql_query)
            sql = assembler(*adapter(query))
            stream = await connection.execute(sql)
            result = [
                dict(
                    id=row.id,
                    message_name=row.message_name,
                    message_payload=row.message_payload,
                    scheduled_at=row.scheduled_at,
                    handler_id=row.handler_id,
                    handler_settings=row.handler_settings,
                    task_settings=row.task_settings,
                )
                for row in stream
            ]
            await connection.execute(
                sqlalchemy.update(self._schema.tasks)
                .where(self._schema.tasks.c.id.in_([task["id"] for task in result]))
                .values(status=assure_status)
            )
            return result
