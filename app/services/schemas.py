from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from enum import Enum
from typing import List
from datetime import datetime


class UserCreate(BaseModel):
    surname: str
    name: str
    email: str
    password: str
    repeat_password: str
    role_id: int = 1
    is_active: bool = True

class UserResponse(BaseModel):
    user_id: int
    surname: str
    name: str
    email: str
    password: str
    role_id: int
    is_active: bool

class UserForChangePassword(BaseModel):
    user_id: int
    surname: str
    name: str
    email: str
    role_id: int
    is_active: bool

class RegistrationDataResponse(BaseModel):
    surname: str
    name: str
    email: str
    password: str
    role_id: int = 1
    is_active: bool = True

class RegistrationResponse(BaseModel):
    status: str
    message: str
    data: List[RegistrationDataResponse] = Field(min_length=1)

class UserLogin(BaseModel):
    email: str
    password: str
    
class UserProfileResponse(BaseModel):
    surname: str
    name: str
    email: str
    is_active: bool
    user_id: int
    role_id: int

class ChangePassword(BaseModel):
    password: str
    new_password: str

class ChangeEmail(BaseModel):
    new_email: str

class ChangeCredentials(BaseModel):
    new_surname: Optional[str] = None
    new_name: Optional[str] = None

class DeleteUser(BaseModel):
    password: str
    repeat_password: str

class CreateProduct(BaseModel):
    product_name: str
    price: int
    amount: int

class ProductResponse(BaseModel):
    message: str
    items: List[CreateProduct] = Field(min_length=1)

class OrderStatus(str, Enum):
    PENDING = 'pending'
    PAID = 'paid'
    CANCELLED = 'cancelled'

class OrderItemCreate(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(ge=1, le=999)

class OrderCreate(BaseModel):
    shipping_address: str = Field(min_length=5, max_length=500)
    items: List[OrderItemCreate] = Field(min_length=1)

class OrderItemResponse(BaseModel):
    product_id: int
    product_name: str
    quantity: int
    price_at_time: int

class OrderResponse(BaseModel):
    order_id: int
    created_at: datetime
    status: str
    total_price: int
    shipping_address: str
    items: List[OrderItemResponse]

class UpdateFieldsOfProduct(BaseModel):
    product_name: Optional[str] = None
    price: Optional[int] = None
    amount: Optional[int] = None

class UpdateProduct(BaseModel):
    product_name: str
    amount: int
    price: int

class UpdateProductResponse(BaseModel):
    message: str
    items: List[UpdateProduct] = Field(min_length=1)

class UpdateFieldOfPermission(BaseModel):
    role_id: Optional[int]
    business_element_id: Optional[int]
    read_permission: Optional[bool] = None
    read_all_permission: Optional[bool] = None
    create_permission: Optional[bool] = None
    update_permission: Optional[bool] = None
    update_all_permission: Optional[bool] = None
    delete_permission: Optional[bool] = None
    delete_all_permission: Optional[bool] = None

class UpdateFieldOfPermissionResponse(BaseModel):
    message: str
    permissions: List[UpdateFieldOfPermission] = Field(min_length=1)
