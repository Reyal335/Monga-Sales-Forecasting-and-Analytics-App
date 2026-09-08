from sqlalchemy.orm import Session
from typing import List, Dict, Any
from decimal import Decimal
from ..repository.MenuRepository import MenuPerformanceRepository
from ..schemas.menu_analytics import MenuPerformanceResponse, PerformanceFilters, PerformanceSummary

class MenuPerformanceService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = MenuPerformanceRepository(db)

    def get_performance(
        self,
        filters: PerformanceFilters
    ) -> Dict[str, Any]:

        results, item_count = self.repository.get_menu_performance(
            days_back=filters.days_back,
            category=filters.category,
            min_profit=filters.min_profit,
            offset=filters.offset,
            limit=filters.limit
        )

        performance_results = [
            MenuPerformanceResponse.model_validate(r) for r in results
        ]

        return {
            'items': performance_results,
            'total_count': item_count,
            'filters': filters.model_dump()
        }

    def get_performance_summary(self, days_back = 365) -> PerformanceSummary:
        summary = self.get_performance_summary(days_back)
        return PerformanceSummary(**summary)