from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


class HealthResponse(BaseModel):
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


app = FastAPI(title="Demand Forecasting API", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


@app.get("/api/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(status="online")


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
