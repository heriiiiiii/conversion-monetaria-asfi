from __future__ import annotations

from app.config import settings


def get_repository():
    engine = settings.db_engine.lower()

    if engine == "mysql":
        from app.repository.mysql_repository import AsfiRepository
        return AsfiRepository()

    from app.repository.sqlite_repository import AsfiRepository
    return AsfiRepository()