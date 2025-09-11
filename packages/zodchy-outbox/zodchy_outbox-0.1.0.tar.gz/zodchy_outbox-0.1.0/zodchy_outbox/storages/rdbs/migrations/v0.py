def upgrade(schema: str = "zodchy") -> list[str]:
    return [
        f"""
    -- Create events table
        CREATE TABLE {schema}.outbox_messages (
            id UUID DEFAULT gen_random_uuid() NOT NULL,
            name VARCHAR NOT NULL,
            payload JSONB NOT NULL,
            CONSTRAINT pk__outbox_messages PRIMARY KEY (id)
        );
        """,
        f"""
    -- Create tasks table
    CREATE TABLE {schema}.outbox_tasks (
        id UUID DEFAULT gen_random_uuid() NOT NULL,
        message_id UUID NOT NULL,
        handler_id VARCHAR NOT NULL,
        status VARCHAR NOT NULL,
        scheduled_at TIMESTAMP NOT NULL,
        handler_settings JSONB,
        task_settings JSONB,
        CONSTRAINT pk__outbox_tasks PRIMARY KEY (id),
        CONSTRAINT fk__outbox_tasks__message_id__outbox_messages FOREIGN KEY (message_id)
            REFERENCES {schema}.outbox_messages(id)
    );
    """,
        f"""
    -- Create index on tasks.message_id
    CREATE INDEX ix__outbox_tasks__message_id ON {schema}.outbox_tasks (message_id);
    """,
        f"""
    -- Create log table
    CREATE TABLE {schema}.outbox_logs (
        id UUID DEFAULT gen_random_uuid() NOT NULL,
        task_id UUID NOT NULL,
        status VARCHAR NOT NULL,
        payload JSONB,
        CONSTRAINT pk__outbox_logs PRIMARY KEY (id),
        CONSTRAINT fk__outbox_logs__task_id__outbox_tasks FOREIGN KEY (task_id)
            REFERENCES {schema}.outbox_tasks(id)
    );
    """,
        f"""
    -- Create index on log.task_id
    CREATE INDEX ix__outbox_logs__task_id ON {schema}.outbox_logs (task_id);
        """,
    ]


def downgrade(schema: str = "zodchy") -> list[str]:
    return [
        f"""
        -- Drop index on log.task_id
        DROP INDEX IF EXISTS {schema}.ix__outbox_logs__task_id;
        """,
        f"""
        -- Drop log table
        DROP TABLE IF EXISTS {schema}.outbox_logs;
        """,
        f"""
        -- Drop index on tasks.message_id
        DROP INDEX IF EXISTS {schema}.ix__outbox_tasks__message_id;
        """,
        f"""    
        -- Drop tasks table
        DROP TABLE IF EXISTS {schema}.outbox_tasks;
        """,
        f"""
        -- Drop events table
        DROP TABLE IF EXISTS {schema}.outbox_messages;
        """,
    ]
