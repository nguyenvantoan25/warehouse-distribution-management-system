from app.core.commands import execute
from app.modules.dispatch.projections import task_dto
from . import service


def run(db, user, task_id, key, action, cmd, operation, own=False):
    task = service.scoped_task(db, user, task_id, own)
    before = task_dto(db, task).model_dump()

    def apply():
        operation(task)
        db.flush()
        return task_dto(db, task).model_dump()

    return execute(db, user.id, key, action, task_id, cmd.model_dump(), before, apply)
