import contextlib

from .client import GameClient, TaskMetadata

with contextlib.suppress(ImportError):
    from . import db
