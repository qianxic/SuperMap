"""
空间分析 API 端点：缓冲区 / 最优路径 / 可达性
"""
from fastapi import APIRouter, Depends
from typing import Any, Dict

from app.application.dto.gis_dto import BufferRequest, ShortestPathRequest, AccessibilityRequest
from app.application.use_cases.gis.analysis_use_case import AnalysisUseCase, get_analysis_use_case


router = APIRouter()


@router.post("/buffer")
async def buffer_endpoint(payload: BufferRequest, uc: AnalysisUseCase = Depends(get_analysis_use_case)) -> Dict[str, Any]:
    return await uc.run_buffer(payload)


@router.post("/shortest-path")
async def shortest_path_endpoint(payload: ShortestPathRequest, uc: AnalysisUseCase = Depends(get_analysis_use_case)) -> Dict[str, Any]:
    return await uc.run_shortest_path(payload)


@router.post("/accessibility")
async def accessibility_endpoint(payload: AccessibilityRequest, uc: AnalysisUseCase = Depends(get_analysis_use_case)) -> Dict[str, Any]:
    return await uc.run_accessibility(payload)


