from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

from models import BillOfMaterials, Ingredient, MenuItem, Order, OrderItem
from sqlalchemy import Select, and_, desc, func, select
from sqlalchemy.orm import Session


class MenuPerformanceRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_menu_performance(
        self,
        days_back: int = 365,
        category: Optional[str] = None,
        min_profit: Optional[Decimal] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Tuple[List[Any], int]:
        """
        Get menu item performance metrics with optional filters.
        Returns tuple of (results, total_count)
        """
        now = datetime.now()
        cutoff_date = now - timedelta(days=days_back)

        # 1. Subquery for recipe costs and contribution margins per item
        item_data = (
            select(
                MenuItem.item_id,
                MenuItem.item_name,
                MenuItem.category,
                MenuItem.unit_price,
                func.sum(BillOfMaterials.quantity_required * Ingredient.cost_per_unit).label(
                    "total_recipe_cost"
                ),
                (
                    MenuItem.unit_price
                    - func.sum(BillOfMaterials.quantity_required * Ingredient.cost_per_unit)
                ).label("contribution_margin"),
            )
            .join(BillOfMaterials, BillOfMaterials.item_id == MenuItem.item_id)
            .join(Ingredient, Ingredient.ingredient_id == BillOfMaterials.ingredient_id)
            .group_by(
                MenuItem.item_id,
                MenuItem.item_name,
                MenuItem.category,
                MenuItem.unit_price,
            )
            .subquery("item_data")
        )

        # 2. Subquery for item order counts within the time window
        item_count = (
            select(
                OrderItem.item_id,
                func.count(OrderItem.item_id).label("item_count"),
            )
            .join(Order, Order.order_id == OrderItem.order_id)
            .where(
                and_(
                    Order.order_timestamp > cutoff_date,
                    Order.order_timestamp < now,
                )
            )
            .group_by(OrderItem.item_id)
            .subquery("item_count")
        )

        # 3. Base statement combining subqueries
        stmt: Select = (
            select(
                item_data.c.item_id,
                item_data.c.item_name,
                item_data.c.category,
                item_data.c.unit_price,
                item_data.c.total_recipe_cost,
                item_data.c.contribution_margin,
                (item_data.c.unit_price * func.coalesce(item_count.c.item_count, 0)).label(
                    "total_revenue"
                ),
                (
                    item_data.c.contribution_margin * func.coalesce(item_count.c.item_count, 0)
                ).label("total_profit"),
            )
            .outerjoin(item_count, item_count.c.item_id == item_data.c.item_id)
        )

        # 4. Apply conditional filters
        if category:
            stmt = stmt.where(item_data.c.category == category)

        if min_profit is not None:
            stmt = stmt.where(
                (item_data.c.contribution_margin * func.coalesce(item_count.c.item_count, 0))
                >= min_profit
            )

        # 5. Get total row count efficiently using a subquery count
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_count = self.db.scalar(count_stmt) or 0

        # 6. Apply ordering and pagination, then execute via db.scalars() or db.execute()
        paginated_stmt = stmt.order_by(desc("total_profit")).limit(limit).offset(offset)
        results = list(self.db.execute(paginated_stmt).all())

        return results, total_count

    def get_performance_summary(self, days_back: int = 365) -> Dict[str, Any]:
        """Get summary statistics for menu performance"""
        results, _ = self.get_menu_performance(days_back=days_back, limit=1000)

        if not results:
            return {
                "total_items": 0,
                "total_revenue": Decimal("0"),
                "total_profit": Decimal("0"),
                "average_margin": Decimal("0"),
                "top_performing_items": [],
            }

        total_revenue = sum((r.total_revenue for r in results), Decimal("0"))
        total_profit = sum((r.total_profit for r in results), Decimal("0"))
        total_items = len(results)

        top_items = sorted(results, key=lambda x: x.total_profit, reverse=True)[:5]

        return {
            "total_items": total_items,
            "total_revenue": total_revenue,
            "total_profit": total_profit,
            "average_margin": total_profit / total_items if total_items > 0 else Decimal("0"),
            "top_performing_items": [
                {
                    "item_id": r.item_id,
                    "item_name": r.item_name,
                    "category": r.category,
                    "unit_price": r.unit_price,
                    "total_recipe_cost": r.total_recipe_cost,
                    "contribution_margin": r.contribution_margin,
                    "total_revenue": r.total_revenue,
                    "total_profit": r.total_profit,
                }
                for r in top_items
            ],
        }