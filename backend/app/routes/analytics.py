from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session, Anno
from typing import List, Optional, Annotated, Dict
from decimal import Decimal
from datetime import datetime


from ..database.database import get_db
from ..services.menu_analytics import MenuPerformanceService
from ..schemas.menu_analytics import MenuPerformanceBase, PerformanceFilters, PerformanceSummary

router = APIRouter(prefix="api/v1/analytics", tags=["analytics"])

db_session = Annotated[Session, Depends(get_db)]

@router.get("/", tags=["analytics"], response_model=Dict[str, any])
async def get_menu_performance(
    filters: Annotated[PerformanceFilters, Query()],
    db: db_session
):
    try:
        service = MenuPerformanceService(db)
        results, total_count = service.get_performance(filters)
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(err),
        ) from err
    except Exception as err:
        # Avoid catching all exceptions silently; log or re-raise properly
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching menu analytics.",
        ) from err

