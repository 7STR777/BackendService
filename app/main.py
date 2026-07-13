from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.services.auth import auth_router
from app.services.profile import profile_router
from app.services.products import product_router
from app.services.orders import order_router
from app.services.adminpanel import adminpanel_router
import uvicorn
from app.db.database import AsyncORM, StaticData

@asynccontextmanager
async def lifespan(app: FastAPI):
    await AsyncORM.init_db()
    await StaticData.add_roles()
    await StaticData.add_business_elements()
    await StaticData.add_users()
    await StaticData.add_products()
    await StaticData.add_orders()
    await StaticData.add_order_items()
    await StaticData.add_access_roles_rules()
    print("Тестовые данные занесены в БД")
    yield
    print("Exit")

app = FastAPI(lifespan=lifespan)

app.include_router(
    router=auth_router,
    prefix="/auth",
    tags=['auth']
)

app.include_router(
    router=profile_router,
    prefix="/profile",
    tags=["profile"]
)

app.include_router(
    router=product_router,
    tags=['products']
)

app.include_router(
    router=order_router,
    tags=['orders']
)

app.include_router(
    router=adminpanel_router,
    prefix="/adminpanel",
    tags=["adminpanel"]
)

@app.get("/addtestdata", tags=['database'])
async def add_test_data():
    """Endpoint для ручного добавления тестовых данных"""
    await AsyncORM.init_db()
    await StaticData.add_roles()
    await StaticData.add_business_elements()
    await StaticData.add_users()
    await StaticData.add_products()
    await StaticData.add_orders()
    await StaticData.add_order_items()
    await StaticData.add_access_roles_rules()
    return {"message": "БД обновлена"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)