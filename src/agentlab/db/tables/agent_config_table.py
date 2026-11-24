"""The `agent_configs` table."""

import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from agentlab.db.base import Base
from agentlab.db.column_types import CreatedAt, JsonObject, UuidPrimaryKey


class AgentConfigTable(Base):
    """An immutable agent configuration, identified by its content hash."""

    __tablename__ = "agent_configs"

    id: Mapped[UuidPrimaryKey]
    name: Mapped[str] = mapped_column(String(200))
    adapter: Mapped[str] = mapped_column(String(50))
    settings: Mapped[JsonObject]
    prompt_version_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("prompt_versions.id", ondelete="RESTRICT"), index=True
    )
    content_hash: Mapped[str] = mapped_column(String(64), unique=True)
    created_at: Mapped[CreatedAt]
