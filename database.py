import os
from sqlalchemy import create_engine, Column, String, Text, DateTime, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import uuid

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_PATH = os.path.join(BASE_DIR, "scribeai.db")
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Category(Base):
    __tablename__ = "categories"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    parent_id = Column(String(36), ForeignKey("categories.id"), nullable=True)
    color = Column(String(20), default="#6366f1")
    user_id = Column(String(64), index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    children = relationship("Category", backref="parent", remote_side=[id])
    contents = relationship("Content", back_populates="category")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "parent_id": self.parent_id,
            "color": self.color,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class Relation(Base):
    __tablename__ = "relations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source_id = Column(String(36), ForeignKey("contents.id"), nullable=False)
    target_id = Column(String(36), ForeignKey("contents.id"), nullable=False)
    relation_type = Column(String(50), default="related")
    note = Column(Text)
    user_id = Column(String(64), index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    source = relationship("Content", foreign_keys=[source_id])
    target = relationship("Content", foreign_keys=[target_id])

    def to_dict(self):
        return {
            "id": self.id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relation_type": self.relation_type,
            "note": self.note,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class Content(Base):
    __tablename__ = "contents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    url = Column(Text, nullable=False)
    title = Column(Text)
    content = Column(Text)
    summary = Column(Text)
    main_content = Column(Text)
    key_points = Column(JSON, default=list)
    notes = Column(JSON, default=list)
    value = Column(Text)
    tags = Column(JSON, default=list)
    user_id = Column(String(64), index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 新增字段
    category_id = Column(String(36), ForeignKey("categories.id"), nullable=True)
    file_path = Column(Text, nullable=True)
    file_type = Column(String(20), default="url")  # url, pdf, docx, txt
    entities = Column(JSON, default=dict)  # AI提取的实体

    category = relationship("Category", back_populates="contents")
    outgoing_relations = relationship("Relation", foreign_keys=[Relation.source_id], back_populates="source")
    incoming_relations = relationship("Relation", foreign_keys=[Relation.target_id], back_populates="target")

    def to_dict(self):
        return {
            "id": self.id,
            "url": self.url,
            "title": self.title,
            "content": self.content,
            "summary": self.summary,
            "main_content": self.main_content,
            "key_points": self.key_points or [],
            "notes": self.notes or [],
            "value": self.value,
            "tags": self.tags or [],
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "category_id": self.category_id,
            "file_path": self.file_path,
            "file_type": self.file_type,
            "entities": self.entities or {}
        }


def init_db():
    Base.metadata.create_all(bind=engine)
    os.makedirs(UPLOAD_DIR, exist_ok=True)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
