import enum


class TaskStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    PROCESSED = "processed"
    FAILED = "failed"
    CANCELLED = "cancelled"
