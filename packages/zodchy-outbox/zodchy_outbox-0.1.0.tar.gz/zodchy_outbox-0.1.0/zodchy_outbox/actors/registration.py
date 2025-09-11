from .. import contracts


async def message_registration_writer(
    data: contracts.messages.OutboxMessageCreated,
    message_creation_handler: contracts.storage.MessageCreationHandlerContract,
) -> None:
    await message_creation_handler(
        dict(
            id=data.id,
            name=data.name,
            payload=data.payload,
        )
    )


async def task_registration_writer(
    data: contracts.messages.OutboxTaskCreated,
    tasks_creation_handler: contracts.storage.TasksCreationHandlerContract,
) -> None:
    handler = data.handler
    handler_id = (
        type(handler).__name__.replace("Outbox", "").replace("Handler", "").lower()
    )
    handler_settings = handler.settings
    await tasks_creation_handler(
        dict(
            id=data.id,
            message_id=data.message_id,
            status=contracts.enums.TaskStatus.SCHEDULED.value,
            scheduled_at=data.scheduled_at,
            handler_id=handler_id,
            handler_settings=handler_settings,
            task_settings=data.settings,
        )
    )
