from sqlalchemy import (
    Integer,
    String,
    Text,
    DateTime,
    Enum,
    ForeignKey,
    func,
    Index,
    TypeDecorator,
)
from datetime import datetime, timezone
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column, Session
from typing import List
from .schemas import MetadataSource, MetadataType, FolderType


class RawBase(DeclarativeBase):
    pass


class Base(RawBase):
    __abstract__ = True
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )


class LibraryModel(Base):
    __tablename__ = "libraries"
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    folders: Mapped[List["FolderModel"]] = relationship(
        "FolderModel",
        back_populates="library",
        lazy="joined",
        primaryjoin="and_(LibraryModel.id==FolderModel.library_id, FolderModel.type=='DEFAULT')",
    )
    plugins: Mapped[List["PluginModel"]] = relationship(
        "PluginModel", secondary="library_plugins", lazy="joined"
    )


class FolderModel(Base):
    __tablename__ = "folders"
    path: Mapped[str] = mapped_column(String, nullable=False)
    library_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("libraries.id"), nullable=False
    )
    library: Mapped["LibraryModel"] = relationship(
        "LibraryModel", back_populates="folders"
    )
    entities: Mapped[List["EntityModel"]] = relationship(
        "EntityModel", back_populates="folder"
    )
    type: Mapped[FolderType] = mapped_column(Enum(FolderType), nullable=False)
    last_modified_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=False)


class EntityPluginStatusModel(RawBase):
    __tablename__ = "entity_plugin_status"

    entity_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("entities.id", ondelete="CASCADE"), primary_key=True
    )
    plugin_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("plugins.id", ondelete="CASCADE"), primary_key=True
    )
    processed_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    __table_args__ = (
        Index("idx_entity_plugin_entity_id", "entity_id"),
        Index("idx_entity_plugin_plugin_id", "plugin_id"),
    )


# Custom DateTime type to ensure UTC time storage
class UTCDateTime(TypeDecorator):
    impl = DateTime
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            if value.tzinfo is None:
                value = value.replace(tzinfo=timezone.utc)
            return value.astimezone(timezone.utc)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            return value.replace(tzinfo=timezone.utc)
        return value


class EntityModel(Base):
    __tablename__ = "entities"
    filepath: Mapped[str] = mapped_column(String, nullable=False)
    filename: Mapped[str] = mapped_column(String, nullable=False)
    size: Mapped[int] = mapped_column(Integer, nullable=False)
    file_created_at: Mapped[datetime] = mapped_column(UTCDateTime, nullable=False)
    file_last_modified_at: Mapped[datetime] = mapped_column(UTCDateTime, nullable=False)
    file_type: Mapped[str] = mapped_column(String, nullable=False)
    file_type_group: Mapped[str] = mapped_column(String, nullable=False)
    last_scan_at: Mapped[datetime | None] = mapped_column(
        UTCDateTime, server_default=func.now(), onupdate=func.now(), nullable=True
    )
    library_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("libraries.id"), nullable=False
    )
    folder_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("folders.id"), nullable=False
    )
    folder: Mapped["FolderModel"] = relationship(
        "FolderModel", back_populates="entities", lazy="select"
    )
    metadata_entries: Mapped[List["EntityMetadataModel"]] = relationship(
        "EntityMetadataModel", lazy="select", cascade="all, delete-orphan"
    )
    tags: Mapped[List["TagModel"]] = relationship(
        "TagModel",
        secondary="entity_tags",
        lazy="select",
        cascade="all, delete",
        overlaps="entities",
    )
    plugin_status: Mapped[List["EntityPluginStatusModel"]] = relationship(
        "EntityPluginStatusModel", cascade="all, delete-orphan", lazy="select"
    )

    # 添加索引
    __table_args__ = (
        Index("idx_filepath", "filepath"),
        Index("idx_filename", "filename"),
        Index("idx_file_type", "file_type"),
        Index("idx_library_id", "library_id"),
        Index("idx_folder_id", "folder_id"),
        Index("idx_file_type_group", "file_type_group"),
        Index("idx_file_created_at", "file_created_at"),
    )

    @classmethod
    def update_last_scan_at(cls, session: Session, entity: "EntityModel"):
        entity.last_scan_at = func.now()
        session.add(entity)

    @property
    def tag_names(self) -> List[str]:
        return [tag.name for tag in self.tags]


class TagModel(Base):
    __tablename__ = "tags"
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    color: Mapped[str | None] = mapped_column(String, nullable=True)
    # source: Mapped[str | None] = mapped_column(String, nullable=True)


class EntityTagModel(Base):
    __tablename__ = "entity_tags"
    entity_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("entities.id", ondelete="CASCADE"), nullable=False
    )
    tag_id: Mapped[int] = mapped_column(Integer, ForeignKey("tags.id"), nullable=False)
    source: Mapped[MetadataSource] = mapped_column(Enum(MetadataSource), nullable=False)

    __table_args__ = (
        Index("idx_entity_tag_entity_id", "entity_id"),
        Index("idx_entity_tag_tag_id", "tag_id"),
    )


class EntityMetadataModel(Base):
    __tablename__ = "metadata_entries"
    entity_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("entities.id"), nullable=False
    )
    key: Mapped[str] = mapped_column(String, nullable=False)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    source_type: Mapped[MetadataSource] = mapped_column(
        Enum(MetadataSource), nullable=False
    )
    source: Mapped[str | None] = mapped_column(String, nullable=True)
    data_type: Mapped[MetadataType] = mapped_column(Enum(MetadataType), nullable=False)
    entity = relationship("EntityModel", back_populates="metadata_entries")

    __table_args__ = (
        Index("idx_metadata_entity_id", "entity_id"),
        Index("idx_metadata_key", "key"),
    )


class PluginModel(Base):
    __tablename__ = "plugins"
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    webhook_url: Mapped[str] = mapped_column(String, nullable=False)


class LibraryPluginModel(Base):
    __tablename__ = "library_plugins"
    library_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("libraries.id"), nullable=False
    )
    plugin_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("plugins.id"), nullable=False
    )
