from typing import List, Optional
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import String
from maleo.database.orm.mixins import DataIdentifier, DataStatus, DataTimestamp
from maleo.types.base.integer import OptionalInteger


class MedicalRole(
    DataTimestamp,
    DataStatus,
    DataIdentifier,
):
    __tablename__ = "medical_roles"
    parent_id: Mapped[OptionalInteger] = mapped_column(
        "parent_id",
        ForeignKey("medical_roles.id", ondelete="SET NULL", onupdate="CASCADE"),
    )
    order: Mapped[OptionalInteger] = mapped_column(name="order")
    code: Mapped[str] = mapped_column(
        name="code", type_=String(20), unique=True, nullable=False
    )
    key: Mapped[str] = mapped_column(
        name="key", type_=String(255), unique=True, nullable=False
    )
    name: Mapped[str] = mapped_column(
        name="name", type_=String(255), unique=True, nullable=False
    )

    parent: Mapped[Optional["MedicalRole"]] = relationship(
        back_populates="children", lazy="select"
    )
    children: Mapped[List["MedicalRole"]] = relationship(
        back_populates="parent",
        cascade="all, delete-orphan",
        lazy="select",
        order_by="MedicalRole.order",
    )
