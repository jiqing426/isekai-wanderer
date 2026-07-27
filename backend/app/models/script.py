"""Script, route, node, and character SQLAlchemy models."""

import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, JSON, Text, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class Script(Base):
    """Script (story) model."""

    __tablename__ = "scripts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    genre: Mapped[str] = mapped_column(String(50), nullable=False)
    cover_image_url: Mapped[str] = mapped_column(Text, nullable=True)
    # v4.4: convergence-point / character counters for dual-agent architecture
    total_convergence_points: Mapped[int] = mapped_column(Integer, default=3)
    characters_per_script: Mapped[int] = mapped_column(Integer, default=3)
    # CR-post-page: hot_value for sorting
    hot_value: Mapped[int] = mapped_column(Integer, default=0, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    routes: Mapped[list["Route"]] = relationship(back_populates="script")


class Route(Base):
    """Story route model."""

    __tablename__ = "routes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    script_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("scripts.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    # CR3-051: Multi-branch routing
    branch_type: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="Branch category: main, branch_a, branch_b, secret")
    branch_label: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="Human-readable branch identifier")
    branch_condition: Mapped[dict | None] = mapped_column(JSON, nullable=True, comment="Condition to enter this branch")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    script: Mapped["Script"] = relationship(back_populates="routes")
    nodes: Mapped[list["Node"]] = relationship(back_populates="route")


class Node(Base):
    """Plot node model."""

    __tablename__ = "nodes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    route_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("routes.id"), nullable=False, index=True)
    parent_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("nodes.id"), nullable=True)
    node_type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    content: Mapped[dict] = mapped_column(JSON, nullable=False)
    background: Mapped[str | None] = mapped_column(Text, nullable=True, comment="W06: Background image URL for this node")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    route: Mapped["Route"] = relationship(back_populates="nodes")
    parent: Mapped["Node"] = relationship("Node", remote_side="Node.id", foreign_keys="Node.parent_id")
    choices: Mapped[list["NodeChoice"]] = relationship(
        back_populates="node",
        foreign_keys="NodeChoice.node_id",
    )


class NodeChoice(Base):
    """Choice option model."""

    __tablename__ = "node_choices"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    node_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("nodes.id"), nullable=False, index=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    next_node_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("nodes.id"), nullable=True)
    affection_delta: Mapped[int] = mapped_column(Integer, default=0)
    # CR3-047: Hidden choice (only visible if affection >= threshold)
    required_affection: Mapped[int] = mapped_column(Integer, default=0)
    is_hidden: Mapped[bool] = mapped_column(Boolean, default=False)
    # CR3-048: Choice consequence preview (shown on hover)
    hint: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    node: Mapped["Node"] = relationship(back_populates="choices", foreign_keys=[node_id])
    next_node: Mapped["Node"] = relationship("Node", foreign_keys=[next_node_id])


class Character(Base):
    """Character model."""

    __tablename__ = "characters"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    script_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("scripts.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    dialogue_style: Mapped[str] = mapped_column(String(50), default="gentle")
    portraits: Mapped[dict | None] = mapped_column(JSON, nullable=True, comment="W06: Portrait images for different expressions")
    # W07: Character selection fields
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    birthday: Mapped[str | None] = mapped_column(String(50), nullable=True)
    likes: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    personality: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_main: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    sprites: Mapped[list["CharacterSprite"]] = relationship(back_populates="character")


class CharacterSprite(Base):
    """Character emotion sprite model."""

    __tablename__ = "character_sprites"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    character_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("characters.id"), nullable=False, index=True)
    emotion: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    image_url: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    character: Mapped["Character"] = relationship(back_populates="sprites")


class Scene(Base):
    """Scene model."""

    __tablename__ = "scenes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    script_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("scripts.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    background_url: Mapped[str] = mapped_column(Text, nullable=True)
    bgm_url: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
