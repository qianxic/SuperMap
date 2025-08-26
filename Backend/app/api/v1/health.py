"""
健康检查接口
"""
from fastapi import APIRouter


router = APIRouter(tags=["系统健康"])


@router.get("/health")
async def health_check() -> dict:
    return {"status": "ok"}


