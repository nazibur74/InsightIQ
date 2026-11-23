
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Text,
    JSON,
    BigInteger
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)

    filename = Column(String(255), nullable=False)
    stored_filename = Column(String(255), nullable=False, unique=True)
    file_path = Column(String(500), nullable=False)

    file_type = Column(String(20), nullable=False)
    file_size = Column(BigInteger, nullable=False)

    row_count = Column(Integer, nullable=True)
    column_count = Column(Integer, nullable=True)

    uploaded_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    analyses = relationship(
        "Analysis",
        back_populates="dataset",
        cascade="all, delete-orphan"
    )


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)

    dataset_id = Column(
        Integer,
        ForeignKey("datasets.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    profile = Column(JSON, nullable=True)
    quality = Column(JSON, nullable=True)
    diagnostics = Column(JSON, nullable=True)
    analytics = Column(JSON, nullable=True)
    anomalies = Column(JSON, nullable=True)
    forecast = Column(JSON, nullable=True)

    ai_insights = Column(Text, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    dataset = relationship(
        "Dataset",
        back_populates="analyses"
    )

    reports = relationship(
        "Report",
        back_populates="analysis",
        cascade="all, delete-orphan"
    )


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)

    analysis_id = Column(
        Integer,
        ForeignKey("analyses.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    analysis = relationship(
        "Analysis",
        back_populates="reports"
    )
