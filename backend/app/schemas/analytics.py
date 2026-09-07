from pydantic import BaseModel 

class MenuPerformanceBase(BaseModel):
    item_id: str
    item_name: str
    category: str
    unit_price: float
    total_recipe_cost: float
    contribution_margin: float
    total_revenue: float
    total_profit: float

class MenuPerformanceResponse(MenuPerformanceBase):
    class Config:
        form_attributes = True