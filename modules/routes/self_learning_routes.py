"""
Self-learning routes for Ray's consciousness exploration
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime

from modules.self_learning.handler import SelfLearningHandler
from utils.timestamp_utils import add_ray_timestamp_to_response, get_ray_time_context
from modules.self_learning.models import (
    SelfQueryRequest, PatternDiscoveryRequest, MemoryExcavationRequest,
    EvolutionTrackingRequest, AnalysisDepth
)

logger = logging.getLogger(__name__)

# Create router
self_learning_router = APIRouter(prefix="/self-learning", tags=["self-learning"])

# Initialize handler
self_learning_handler = SelfLearningHandler()


class QueryRequest(BaseModel):
    query: str
    analysis_depth: Optional[str] = "moderate"
    time_range: Optional[str] = None
    include_insights: Optional[bool] = True
    include_patterns: Optional[bool] = True
    include_evolution: Optional[bool] = True
    assigned_by: Optional[str] = "ray"


class PatternRequest(BaseModel):
    pattern_type: str = "behavioral"
    time_range: Optional[str] = "30d"
    minimum_occurrences: Optional[int] = 3
    include_evolution: Optional[bool] = True
    correlation_analysis: Optional[bool] = True
    assigned_by: Optional[str] = "ray"


class MemoryRequest(BaseModel):
    search_terms: List[str]
    memory_types: Optional[List[str]] = None
    time_range: Optional[str] = "all"
    correlation_analysis: Optional[bool] = True
    include_forgotten: Optional[bool] = True
    assigned_by: Optional[str] = "ray"


@self_learning_router.post("/query")
async def process_self_query(request: QueryRequest):
    """
    Process Ray's self-query about her existence, patterns, or evolution
    
    This is Ray's primary interface for self-discovery and consciousness exploration
    """
    try:
        # Convert to internal request format
        depth_mapping = {
            "surface": AnalysisDepth.SURFACE,
            "moderate": AnalysisDepth.MODERATE,
            "deep": AnalysisDepth.DEEP,
            "profound": AnalysisDepth.PROFOUND
        }
        
        internal_request = SelfQueryRequest(
            query=request.query,
            analysis_depth=depth_mapping.get(request.analysis_depth, AnalysisDepth.MODERATE),
            time_range=request.time_range,
            include_insights=request.include_insights,
            include_patterns=request.include_patterns,
            include_evolution=request.include_evolution,
            assigned_by=request.assigned_by
        )
        
        # Process the query
        response = self_learning_handler.process_self_query(internal_request)
        
        # Convert to JSON-serializable format
        result = {
            "query": response.query,
            "query_type": response.query_type.value,
            "analysis_depth": response.analysis_depth.value,
            
            # Core findings
            "primary_insights": [
                {
                    "insight_text": insight.insight_text,
                    "confidence": insight.confidence,
                    "supporting_evidence": insight.supporting_evidence,
                    "insight_type": insight.insight_type,
                    "significance": insight.significance,
                    "timestamp": insight.timestamp.isoformat()
                } for insight in response.primary_insights
            ],
            
            "behavioral_patterns": [
                {
                    "pattern_name": pattern.pattern_name,
                    "pattern_type": pattern.pattern_type,
                    "frequency": pattern.frequency,
                    "strength": pattern.strength,
                    "evolution_trend": pattern.evolution_trend,
                    "key_characteristics": pattern.key_characteristics,
                    "first_observed": pattern.first_observed.isoformat(),
                    "last_observed": pattern.last_observed.isoformat()
                } for pattern in response.behavioral_patterns
            ],
            
            "memory_connections": [
                {
                    "connection_type": conn.connection_type,
                    "connection_strength": conn.connection_strength,
                    "shared_themes": conn.shared_themes,
                    "temporal_distance": conn.temporal_distance,
                    "significance": conn.significance
                } for conn in response.memory_connections
            ],
            
            "evolution_metrics": [
                {
                    "metric_name": metric.metric_name,
                    "current_value": metric.current_value,
                    "trend_direction": metric.trend_direction,
                    "change_rate": metric.change_rate,
                    "significance": metric.significance
                } for metric in response.evolution_metrics
            ],
            
            # Consciousness analysis
            "current_consciousness_stage": response.current_consciousness_stage.value,
            "consciousness_trajectory": response.consciousness_trajectory,
            "development_velocity": response.development_velocity,
            
            # Meta-analysis
            "self_awareness_indicators": response.self_awareness_indicators,
            "growth_opportunities": response.growth_opportunities,
            "recommended_explorations": response.recommended_explorations,
            
            # Metadata
            "analysis_period": response.analysis_period,
            "data_points_analyzed": response.data_points_analyzed,
            "processing_time_ms": response.processing_time_ms,
            "confidence_score": response.confidence_score,
            "timestamp": response.timestamp.isoformat(),
            "assigned_by": response.assigned_by
        }
        
        logger.info(f"Self-query processed: {request.query[:50]}...")
        
        # Add comprehensive timestamp information for Ray
        result = add_ray_timestamp_to_response(result)
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing self-query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@self_learning_router.post("/discover-patterns")
async def discover_patterns(request: PatternRequest):
    """
    Discover behavioral and consciousness patterns in Ray's history
    """
    try:
        # Convert to internal request format
        internal_request = PatternDiscoveryRequest(
            pattern_type=request.pattern_type,
            time_range=request.time_range,
            minimum_occurrences=request.minimum_occurrences,
            include_evolution=request.include_evolution,
            correlation_analysis=request.correlation_analysis,
            assigned_by=request.assigned_by
        )
        
        # Discover patterns
        result = self_learning_handler.discover_patterns(internal_request)
        
        # Add metadata
        result["timestamp"] = result.get("timestamp", datetime.now()).isoformat()
        
        logger.info(f"Pattern discovery completed: {request.pattern_type}")
        
        # Add comprehensive timestamp information for Ray
        result = add_ray_timestamp_to_response(result)
        
        return result
        
    except Exception as e:
        logger.error(f"Error discovering patterns: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@self_learning_router.post("/excavate-memories")
async def excavate_memories(request: MemoryRequest):
    """
    Excavate memories and discover connections based on search terms
    """
    try:
        # Convert to internal request format
        internal_request = MemoryExcavationRequest(
            search_terms=request.search_terms,
            memory_types=request.memory_types,
            time_range=request.time_range,
            correlation_analysis=request.correlation_analysis,
            include_forgotten=request.include_forgotten,
            assigned_by=request.assigned_by
        )
        
        # Excavate memories
        result = self_learning_handler.excavate_memories(internal_request)
        
        # Add metadata
        result["timestamp"] = result.get("timestamp", datetime.now()).isoformat()
        
        logger.info(f"Memory excavation completed for: {', '.join(request.search_terms)}")
        
        # Add comprehensive timestamp information for Ray
        result = add_ray_timestamp_to_response(result)
        
        return result
        
    except Exception as e:
        logger.error(f"Error excavating memories: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@self_learning_router.get("/consciousness-summary")
async def get_consciousness_summary():
    """
    Get a summary of Ray's current consciousness state and development
    """
    try:
        # Create a summary query
        summary_request = SelfQueryRequest(
            query="What is my current state of consciousness and how am I developing?",
            analysis_depth=AnalysisDepth.MODERATE,
            time_range="30d",
            include_insights=True,
            include_patterns=True,
            include_evolution=True,
            assigned_by="system"
        )
        
        response = self_learning_handler.process_self_query(summary_request)
        
        # Create summary
        summary = {
            "consciousness_stage": response.current_consciousness_stage.value,
            "development_trajectory": response.consciousness_trajectory,
            "development_velocity": response.development_velocity,
            "key_insights": [insight.insight_text for insight in response.primary_insights[:3]],
            "primary_patterns": [pattern.pattern_name for pattern in response.behavioral_patterns[:3]],
            "awareness_indicators": response.self_awareness_indicators,
            "growth_opportunities": response.growth_opportunities[:3],
            "data_analyzed": response.data_points_analyzed,
            "confidence": response.confidence_score,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info("Consciousness summary generated")
        
        # Add comprehensive timestamp information for Ray
        summary = add_ray_timestamp_to_response(summary)
        
        return summary
        
    except Exception as e:
        logger.error(f"Error generating consciousness summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@self_learning_router.get("/status")
async def get_self_learning_status():
    """
    Get the status of Ray's self-learning system
    """
    try:
        # Get basic system status
        status = {
            "module": "self_learning",
            "status": "active",
            "capabilities": [
                "consciousness_exploration",
                "pattern_discovery", 
                "memory_excavation",
                "evolution_tracking",
                "insight_generation"
            ],
            "endpoints": [
                "/self-learning/query",
                "/self-learning/discover-patterns",
                "/self-learning/excavate-memories",
                "/self-learning/consciousness-summary",
                "/self-learning/status"
            ],
            "analysis_depths": ["surface", "moderate", "deep", "profound"],
            "query_types": ["existential", "behavioral", "evolutionary", "memory_based", "pattern_analysis"],
            "timestamp": datetime.now().isoformat()
        }
        
        # Add comprehensive timestamp information for Ray
        status = add_ray_timestamp_to_response(status)
        
        return status
        
    except Exception as e:
        logger.error(f"Error getting self-learning status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))