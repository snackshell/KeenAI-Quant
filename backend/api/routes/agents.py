"""
AI Agents API Routes
Get AI agent performance and statistics
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, List
from pydantic import BaseModel

from AI_Core.agents.agent_orchestrator import agent_orchestrator
from AI_Core.agents.performance_tracker import performance_tracker

router = APIRouter()


# Response Models
class AgentPerformanceResponse(BaseModel):
    agent_name: str
    total_predictions: int
    correct_predictions: int
    accuracy: float
    avg_confidence: float
    sharpe_ratio: float
    current_weight: float


class AgentStatsResponse(BaseModel):
    name: str
    enabled: bool
    total_calls: int
    successful_calls: int
    failed_calls: int
    avg_response_time: float
    last_call: str


@router.get("/performance", response_model=List[AgentPerformanceResponse])
async def get_agent_performance():
    """Get AI agent performance metrics"""
    try:
        # Get performance from tracker
        performance_data = performance_tracker.get_all_performance()
        
        if not performance_data:
            # Return default data if no performance tracked yet
            return [
                AgentPerformanceResponse(
                    agent_name="Keen Agent",
                    total_predictions=0,
                    correct_predictions=0,
                    accuracy=0.0,
                    avg_confidence=0.0,
                    sharpe_ratio=0.0,
                    current_weight=1.0
                )
            ]
        
        return [
            AgentPerformanceResponse(
                agent_name=agent_name,
                total_predictions=data.get('total_predictions', 0),
                correct_predictions=data.get('correct_predictions', 0),
                accuracy=data.get('accuracy', 0.0),
                avg_confidence=data.get('avg_confidence', 0.0),
                sharpe_ratio=data.get('sharpe_ratio', 0.0),
                current_weight=data.get('current_weight', 1.0)
            )
            for agent_name, data in performance_data.items()
        ]
    except Exception as e:
        print(f"❌ Error getting agent performance: {e}")
        import traceback
        traceback.print_exc()
        # Return empty list instead of error
        return []


@router.get("/stats", response_model=Dict[str, AgentStatsResponse])
async def get_agent_stats():
    """Get AI agent statistics"""
    try:
        stats = agent_orchestrator.get_agent_stats()
        
        return {
            agent_name: AgentStatsResponse(
                name=agent_name,
                enabled=data.get('enabled', True),
                total_calls=data.get('total_calls', 0),
                successful_calls=data.get('successful_calls', 0),
                failed_calls=data.get('failed_calls', 0),
                avg_response_time=data.get('avg_response_time', 0.0),
                last_call=data.get('last_call', 'Never')
            )
            for agent_name, data in stats.items()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/enable/{agent_name}")
async def enable_agent(agent_name: str):
    """Enable an AI agent"""
    try:
        success = agent_orchestrator.enable_agent(agent_name)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")
        
        return {"success": True, "message": f"Agent '{agent_name}' enabled"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/disable/{agent_name}")
async def disable_agent(agent_name: str):
    """Disable an AI agent"""
    try:
        success = agent_orchestrator.disable_agent(agent_name)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")
        
        return {"success": True, "message": f"Agent '{agent_name}' disabled"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class AgentActivityResponse(BaseModel):
    id: str
    title: str
    description: str
    timestamp: str
    type: str  # 'analysis', 'trade', 'holding', 'alert'


@router.get("/activity", response_model=List[AgentActivityResponse])
async def get_agent_activity():
    """Get recent agent activity/reports"""
    try:
        # This would come from a logging/monitoring system
        # For now, return empty list - will be populated when agent makes decisions
        return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
