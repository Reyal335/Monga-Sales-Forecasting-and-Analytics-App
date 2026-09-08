from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from app.schemas.users import User

from pydantic import BaseModel
from app.routes import chat
from app.routes import users
from app.routes import analytics
from app.database.database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Annotated

import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

class HealthResponse(BaseModel):
    status: str

class DatabaseHealth(BaseModel):
    status: str

class Prediction(BaseModel):
    date: str
    store_name: str
    item_name: str
    predicted_qty: int


class DashboardSummary(BaseModel):
    total_projected_units: int
    active_skus: int
    top_demand_location: str
    model_type: str
    recent_predictions: list[Prediction]

db_session = Annotated[Session, Depends(get_db)]

app = FastAPI(title="Demand Forecasting API", version="0.1.0")


app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

app.include_router(chat.router)
app.include_router(users.router)
app.include_router(analytics.router)

def fake_decode_token(token):
    return User(
        username=token + "fakedecoded", email="john@example.com", full_name="John Doe"
    )

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    user = fake_decode_token(token)
    return user


@app.get("/users/me")
async def read_items(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user

@app.get("/api/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(status="online")


@app.get("/api/database-health", response_model=HealthResponse)
def database_check(db: db_session) -> HealthResponse:
    if not db.is_active:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "msg": "Database session is not active.",
                "db_url": DATABASE_URL
            },
        )       

    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "msg": f"Database operational error {str(e)}",
                "db_url": DATABASE_URL
            }
        )
    
    return DatabaseHealth(status='online')


@app.get("/api/dashboard/summary", response_model=DashboardSummary)
def get_dashboard_summary() -> DashboardSummary:
    return DashboardSummary(
        total_projected_units=1420, active_skus=8, top_demand_location="SM Megamall", model_type="LightGBM regressor",
        recent_predictions=[
            Prediction(date="2026-09-04", store_name="SM Megamall", item_name="Premium Rice 5kg", predicted_qty=320),
            Prediction(date="2026-09-04", store_name="SM North EDSA", item_name="Instant Coffee 200g", predicted_qty=245),
            Prediction(date="2026-09-05", store_name="SM Megamall", item_name="Laundry Detergent 1kg", predicted_qty=180),
            Prediction(date="2026-09-05", store_name="SM Mall of Asia", item_name="Bottled Water 1L", predicted_qty=675),
        ],
    )