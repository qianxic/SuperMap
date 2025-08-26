from typing import Any, Dict

from app.application.dto.gis_dto import BufferRequest, ShortestPathRequest, AccessibilityRequest
from app.domains.gis.services import BufferService, RoutingService, IsochroneService, GeometryProjector
from app.infrastructure.database.postgres.repositories import AnalysisResultRepository
from app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends


class AnalysisUseCase:
    def __init__(self, buffer_srv: BufferService, route_srv: RoutingService, iso_srv: IsochroneService,
                 projector: GeometryProjector, repo: AnalysisResultRepository):
        self.buffer_srv = buffer_srv
        self.route_srv = route_srv
        self.iso_srv = iso_srv
        self.projector = projector
        self.repo = repo

    async def run_buffer(self, req: BufferRequest) -> Dict[str, Any]:
        fc_result = self.buffer_srv.buffer_geojson(req.input, req.distance_m, req.cap_style, req.dissolve)
        record_id = await self.repo.save_buffer_result(req, fc_result)
        # 注入 record_id
        if fc_result.get("features"):
            for f in fc_result["features"]:
                props = f.setdefault("properties", {})
                props["record_id"] = record_id
        return fc_result

    async def run_shortest_path(self, req: ShortestPathRequest) -> Dict[str, Any]:
        feat_result = self.route_srv.shortest_path(req.start.model_dump(), req.end.model_dump(), req.profile, req.weight)
        record_id = await self.repo.save_route_result(req, feat_result)
        feat_result.setdefault("properties", {})["record_id"] = record_id
        return feat_result

    async def run_accessibility(self, req: AccessibilityRequest) -> Dict[str, Any]:
        fc_result = self.iso_srv.isochrones(req.origin.model_dump(), req.mode, req.cutoff_min, req.bands)
        record_id = await self.repo.save_accessibility_result(req, fc_result)
        summary = fc_result.setdefault("summary", {})
        summary["record_id"] = record_id
        return fc_result


def get_analysis_use_case(
    db: AsyncSession = Depends(get_db),
) -> AnalysisUseCase:
    # 以最小骨架实例化服务与仓储；后续可接入依赖注入容器
    buffer_srv = BufferService()
    route_srv = RoutingService()
    iso_srv = IsochroneService()
    projector = GeometryProjector()
    repo = AnalysisResultRepository(db)
    return AnalysisUseCase(buffer_srv, route_srv, iso_srv, projector, repo)


