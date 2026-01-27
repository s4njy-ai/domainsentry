"""
Risk analysis endpoints for DomainSentry API.
"""
import uuid
from typing import Dict

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.schemas.domain import RiskAnalysisRequest, RiskAnalysisResponse
from app.services.risk_service import RiskService

router = APIRouter()


@router.post("/analyze", response_model=RiskAnalysisResponse)
async def analyze_risk(
    risk_request: RiskAnalysisRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """
    Analyze risk for a domain.
    """
    service = RiskService(db)
    return await service.analyze_domain_risk(risk_request)


@router.post("/analyze-async")
async def analyze_risk_async(
    risk_request: RiskAnalysisRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """
    Trigger asynchronous risk analysis for a domain.
    """
    service = RiskService(db)
    task_id = await service.queue_risk_analysis(risk_request.domain_name, risk_request.force_rescan)
    
    return {"task_id": task_id, "message": "Risk analysis queued successfully"}


@router.get("/analysis/{task_id}")
async def get_analysis_status(
    task_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Get the status of a risk analysis task.
    """
    service = RiskService(db)
    return await service.get_analysis_status(task_id)


@router.get("/config")
async def get_risk_config(
    db: AsyncSession = Depends(get_db),
):
    """
    Get current risk configuration.
    """
    service = RiskService(db)
    return await service.get_risk_config()


@router.get("/trends")
async def get_risk_trends(
    db: AsyncSession = Depends(get_db),
    days: int = 30,
):
    """
    Get risk trends over time.
    """
    service = RiskService(db)
    return await service.get_risk_trends(days)


@router.get("/factor-breakdown")
async def get_factor_breakdown(
    db: AsyncSession = Depends(get_db),
    days: int = 30,
):
    """
    Get risk factor breakdown over time.
    """
    service = RiskService(db)
    return await service.get_risk_factor_breakdown(days)