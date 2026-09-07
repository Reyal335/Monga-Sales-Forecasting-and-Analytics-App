from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class MenuPerformanceBase(BaseModel):
    item_id: int
    item_name: str
    category: str
    unit_price: Decimal
    total_recipe_cost: Decimal
    contribution_margin: Decimal
    total_revenue: Decimal
    total_profit: Decimal


class MenuPerformanceResponse(MenuPerformanceBase):
    # Modernized Pydantic v2 configuration replaces nested `class Config:`
    model_config = ConfigDict(from_attributes=True)


class PerformanceFilters(BaseModel):
    days_back: int = Field(default=365, ge=1, le=1095, description="Number of days to look back")
    category: Optional[str] = Field(default=None, description="Filter by category")
    min_profit: Optional[Decimal] = Field(default=None, description="Minimum profit filter")
    limit: int = Field(default=100, ge=1, le=1000, description="Number of results to return")
    offset: int = Field(default=0, ge=0, description="Offset for pagination")


class PerformanceSummary(BaseModel):
    total_items: int
    total_revenue: Decimal
    total_profit: Decimal
    average_margin: Decimal
    top_performing_items: List[MenuPerformanceResponse]