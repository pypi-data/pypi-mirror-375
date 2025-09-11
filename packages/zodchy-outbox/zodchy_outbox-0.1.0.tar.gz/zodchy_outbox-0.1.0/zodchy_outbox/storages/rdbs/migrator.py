from . import migrations


class Migrator:
    def __init__(self, schema: str = "zodchy", version: str = "latest"):
        self._schema = schema
        self._version = version

    def upgrade(self) -> list[str]:
        return [migration for migration in migrations.v0.upgrade(self._schema)]

    def downgrade(self) -> list[str]:
        return [migration for migration in migrations.v0.downgrade(self._schema)]
