from typing import Annotated

from dishka.integrations.fastapi import DishkaRoute
from dishka.integrations.fastapi import FromDishka as Depends
from fastapi import APIRouter
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(route_class=DishkaRoute)


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/readiness")
async def readiness(db_session: Annotated[AsyncSession, Depends()]) -> dict[str, str]:
    try:
        await db_session.execute(text("SELECT 1"))
    except Exception as e:
        return {"status": "error", "message": str(e)}
    return {"status": "ok"}
