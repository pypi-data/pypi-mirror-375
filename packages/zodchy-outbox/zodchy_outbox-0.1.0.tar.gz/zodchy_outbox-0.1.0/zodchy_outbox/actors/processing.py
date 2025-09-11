import collections.abc
from ..contracts.messages import GetOutboxTasks, OutboxTaskForProcessingReceived
from ..contracts.storage import TasksForStatusHandlerContract
from ..contracts.enums import TaskStatus


async def tasks_ready_for_dispatch_reader(
    query: GetOutboxTasks,
    handler: TasksForStatusHandlerContract,
) -> collections.abc.AsyncIterable[OutboxTaskForProcessingReceived]:
    for task in await handler(
        query=query,
        assure_status=TaskStatus.IN_PROGRESS.value,
    ):
        yield OutboxTaskForProcessingReceived(
            id=task["id"],
            message_name=task["message_name"],
            message_payload=task["message_payload"],
            scheduled_at=task["scheduled_at"],
            handler_id=task["handler_id"],
            handler_settings=task["handler_settings"],
        )
