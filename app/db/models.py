from app.db.base import Base
from typing import List
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import DateTime, ForeignKey, Column, Table, Integer, String
from datetime import date
from app.services.schemas import OrderStatus

from datetime import datetime

class Users(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(primary_key=True)
    surname: Mapped[str] = mapped_column()
    name: Mapped[str] = mapped_column()
    password: Mapped[str] = mapped_column()
    email: Mapped[str] = mapped_column(unique=True)
    role_id: Mapped[int] = mapped_column(ForeignKey('roles.role_id', ondelete='CASCADE'))
    is_active: Mapped[bool] = mapped_column(default=True)
    
    role: Mapped["Roles"] = relationship(back_populates="users")
    orders: Mapped[List["Orders"]] = relationship(back_populates="user")

class Roles(Base):
    __tablename__ = 'roles'

    role_id: Mapped[int] = mapped_column(primary_key=True)
    role_name: Mapped[str] = mapped_column(unique=True)
    
    users: Mapped[List["Users"]] = relationship(back_populates="role")
    access_roles_rules: Mapped[List["AccessRolesRules"]] = relationship(back_populates="role")

class BusinessElements(Base):
    __tablename__ = 'business_elements'

    business_element_id: Mapped[int] = mapped_column(primary_key=True)
    business_element: Mapped[str] = mapped_column()

    access_roles_rules: Mapped[List["AccessRolesRules"]] = relationship(back_populates="business_element")

class AccessRolesRules(Base):
    __tablename__ = 'access_roles_rules'

    access_roles_rules_id: Mapped[int] = mapped_column(primary_key=True)
    role_id: Mapped[int] = mapped_column(ForeignKey('roles.role_id', ondelete='CASCADE'))
    business_element_id: Mapped[int] = mapped_column(ForeignKey('business_elements.business_element_id', ondelete='CASCADE'))
    read_permission: Mapped[bool] = mapped_column()
    read_all_permission: Mapped[bool] = mapped_column()
    create_permission: Mapped[bool] = mapped_column()
    update_permission: Mapped[bool] = mapped_column()
    update_all_permission: Mapped[bool] = mapped_column()
    delete_permission: Mapped[bool] = mapped_column()
    delete_all_permission: Mapped[bool] = mapped_column()

    role: Mapped["Roles"] = relationship(back_populates="access_roles_rules")
    business_element: Mapped["BusinessElements"] = relationship(back_populates="access_roles_rules")

class Products(Base):
    __tablename__ = 'products'

    product_id: Mapped[int] = mapped_column(primary_key=True)
    product_name: Mapped[str] = mapped_column(unique=True)
    price: Mapped[int] = mapped_column()
    amount: Mapped[int] = mapped_column()

    items: Mapped[List["OrderItem"]] = relationship(back_populates="product")

class Orders(Base):
    __tablename__ = 'orders'

    order_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.user_id', ondelete='CASCADE'))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())
    status: Mapped[str] = mapped_column(default=OrderStatus.PENDING.value)
    total_price: Mapped[int] = mapped_column()
    shipping_address: Mapped[str] = mapped_column()

    user: Mapped["Users"] = relationship(back_populates="orders")
    items: Mapped[List["OrderItem"]] = relationship(back_populates="order")

class OrderItem(Base):
    __tablename__ = 'order_items'

    orderitem_id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey('orders.order_id', ondelete='CASCADE'))
    product_id: Mapped[int] = mapped_column(ForeignKey('products.product_id', ondelete='CASCADE'))
    product_name: Mapped[str] = mapped_column(String(500))
    quantity: Mapped[int] = mapped_column()
    price_at_time: Mapped[int] = mapped_column()

    order: Mapped["Orders"] = relationship(back_populates="items")
    product: Mapped['Products'] = relationship(back_populates="items")