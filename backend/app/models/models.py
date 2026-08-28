from datetime import datetime
from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, SmallInteger, String, Text, UniqueConstraint, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Store(Base):
    __tablename__ = "stores"

    store_id: Mapped[str] = mapped_column(String(10), primary_key=True)
    store_name: Mapped[str] = mapped_column(String(100), nullable=False)

    orders: Mapped[list["Order"]] = relationship(back_populates="store")


class MenuItem(Base):
    __tablename__ = "menu_items"

    item_id: Mapped[str] = mapped_column(String(10), primary_key=True)
    item_name: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    order_items: Mapped[list["OrderItem"]] = relationship(back_populates="item")
    bill_of_materials: Mapped[list["BillOfMaterials"]] = relationship(
        back_populates="item", cascade="all, delete-orphan"
    )


class Order(Base):
    __tablename__ = "orders"

    order_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    store_id: Mapped[str | None] = mapped_column(ForeignKey("stores.store_id"))
    order_timestamp: Mapped[datetime] = mapped_column(nullable=False)

    store: Mapped[Store | None] = relationship(back_populates="orders")
    order_items: Mapped[list["OrderItem"]] = relationship(back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"

    order_item_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[int | None] = mapped_column(ForeignKey("orders.order_id"))
    item_id: Mapped[str | None] = mapped_column(ForeignKey("menu_items.item_id"))
    quantity: Mapped[int] = mapped_column(nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    order: Mapped[Order | None] = relationship(back_populates="order_items")
    item: Mapped[MenuItem | None] = relationship(back_populates="order_items")


class Ingredient(Base):
    __tablename__ = "ingredients"

    ingredient_id: Mapped[str] = mapped_column(String(10), primary_key=True)
    ingredient_name: Mapped[str] = mapped_column(String(100), nullable=False)
    unit_of_measure: Mapped[str] = mapped_column(String(20), nullable=False)
    cost_per_unit: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)

    bill_of_materials: Mapped[list["BillOfMaterials"]] = relationship(
        back_populates="ingredient"
    )


class BillOfMaterials(Base):
    __tablename__ = "bill_of_materials"
    __table_args__ = (UniqueConstraint("item_id", "ingredient_id", name="uq_item_ingredient"),)

    bom_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    item_id: Mapped[str | None] = mapped_column(
        ForeignKey("menu_items.item_id", ondelete="CASCADE")
    )
    ingredient_id: Mapped[str | None] = mapped_column(
        ForeignKey("ingredients.ingredient_id", ondelete="RESTRICT")
    )
    quantity_required: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)

    item: Mapped[MenuItem | None] = relationship(back_populates="bill_of_materials")
    ingredient: Mapped[Ingredient | None] = relationship(back_populates="bill_of_materials")


class Role(Base):
    __tablename__ = "roles"

    role_id: Mapped[int] = mapped_column(SmallInteger, primary_key=True, autoincrement=True)
    role_name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())
