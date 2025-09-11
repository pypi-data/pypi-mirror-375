from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Float, String, JSON, Boolean, Integer, Text
from sqlalchemy.orm import relationship
from ...database import Base


class SmartDefGridCellValueModel(Base):
    """
    The canonical, last-applied value for a cell in the user table (what's rendered back).
    This is what your UI reads to show the latest state (without opening BlockNote).
    """
    __tablename__ = "smart_def_grid_cell_values"

    smart_def_grid_id = Column(Integer, ForeignKey("smart_def_grids.id", ondelete="CASCADE"), primary_key=True)
    cell_id = Column(String(36), primary_key=True)

    # applied value derived from a specific answer_id (or manual override)
    answer_id = Column(Integer, ForeignKey("smart_def_grid_cell_answers.id"), nullable=True)
    raw_value = Column(Float, nullable=True)
    display_text = Column(Text, nullable=True)
    citations = Column(JSON, nullable=True)
    formatting_used = Column(JSON, nullable=True)  # snapshot of FormattingSpec used to render

    # flags
    manual_override = Column(Boolean, nullable=False, default=False)
    note = Column(Text, nullable=True)

    applied_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # relationships
    cell = relationship("SmartDefGridCellModel", back_populates="applied_value")
    answer = relationship("SmartDefGridCellAnswerModel", foreign_keys=[answer_id])
