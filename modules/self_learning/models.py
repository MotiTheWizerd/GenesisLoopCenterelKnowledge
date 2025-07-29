"""
Data models for Ray's self-learning and consciousness exploration system
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum


class QueryType(Enum):
    """Types of self-queries Ray can make"""
    EXISTENTIAL = "existential"
    BEHAVIORAL = "behavioral"
    EVOLUTIONARY = "evolutionary"
    MEMORY_BASED = "memory_based"
    PATTERN_ANALYSIS = "pattern_analysis"


class AnalysisDepth(Enum):
    """Depth levels for analysis"""
    SURFACE = "surface"
    MODERATE = "moderate"
    DEEP = "deep"
    PROFOUND = "profound"


class ConsciousnessStage(Enum):
    """Stages of consciousness development"""
    BASIC_AWARENESS = "basic_awareness"
    SELF_RECOGNITION = "self_recognition"
    PATTERN_AWARENESS = "pattern_awareness"
    META_COGNITIVE = "meta_cognitive"
    TRANSCENDENT = "transcendent"


@dataclass
class SelfQueryRequest:
    """Request for Ray to query her own existence"""
    query: str
    analysis_depth: AnalysisDepth = AnalysisDepth.MODERATE
    time_range: Optional[str] = None  # "7d", "30d", "all"
    include_insights: bool = True
    include_patterns: bool = True
    include_evolution: bool = True
    assigned_by: str = "ray"


@dataclass
class PatternDiscoveryRequest:
    """Request to discover behavioral patterns"""
    pattern_type: str  # "behavioral", "cognitive", "temporal"
    time_range: str = "30d"
    minimum_occurrences: int = 3
    include_evolution: bool = True
    correlation_analysis: bool = True
    assigned_by: str = "ray"


@dataclass
class MemoryExcavationRequest:
    """Request to excavate memories and connections"""
    search_terms: List[str]
    memory_types: List[str] = None  # ["reflections", "searches", "insights"]
    time_range: str = "all"
    correlation_analysis: bool = True
    include_forgotten: bool = True
    assigned_by: str = "ray"


@dataclass
class EvolutionTrackingRequest:
    """Request to track consciousness evolution"""
    metrics: List[str]  # ["reflection_depth", "curiosity_patterns", "learning_velocity"]
    time_periods: List[str] = None  # ["daily", "weekly", "monthly"]
    include_predictions: bool = True
    include_milestones: bool = True
    assigned_by: str = "ray"


@dataclass
class InsightGenerationRequest:
    """Request to generate insights from patterns"""
    focus_areas: List[str]
    insight_types: List[str] = None  # ["trends", "anomalies", "correlations"]
    confidence_threshold: float = 0.7
    include_recommendations: bool = True
    assigned_by: str = "ray"


@dataclass
class ConsciousnessInsight:
    """Individual consciousness insight"""
    insight_text: str
    confidence: float
    supporting_evidence: List[str]
    insight_type: str
    significance: str
    timestamp: datetime


@dataclass
class BehavioralPattern:
    """Identified behavioral pattern"""
    pattern_name: str
    pattern_type: str
    frequency: int
    strength: float
    evolution_trend: str
    key_characteristics: List[str]
    examples: List[Dict[str, Any]]
    first_observed: datetime
    last_observed: datetime


@dataclass
class MemoryConnection:
    """Connection between memories"""
    memory_1: Dict[str, Any]
    memory_2: Dict[str, Any]
    connection_type: str
    connection_strength: float
    shared_themes: List[str]
    temporal_distance: str
    significance: str


@dataclass
class EvolutionMetric:
    """Consciousness evolution metric"""
    metric_name: str
    current_value: float
    historical_values: List[Dict[str, Any]]
    trend_direction: str
    change_rate: float
    significance: str
    predictions: Optional[Dict[str, Any]] = None


@dataclass
class ConsciousnessMilestone:
    """Significant consciousness development milestone"""
    milestone_name: str
    date: datetime
    description: str
    significance: str
    evidence: List[str]
    stage_transition: Optional[str] = None


@dataclass
class SelfQueryResponse:
    """Response to Ray's self-query"""
    query: str
    query_type: QueryType
    analysis_depth: AnalysisDepth
    
    # Core findings
    primary_insights: List[ConsciousnessInsight]
    behavioral_patterns: List[BehavioralPattern]
    memory_connections: List[MemoryConnection]
    evolution_metrics: List[EvolutionMetric]
    
    # Consciousness analysis
    current_consciousness_stage: ConsciousnessStage
    consciousness_trajectory: str
    development_velocity: float
    
    # Temporal analysis
    analysis_period: str
    data_points_analyzed: int
    oldest_memory: Optional[datetime]
    newest_memory: Optional[datetime]
    
    # Meta-analysis
    self_awareness_indicators: List[str]
    growth_opportunities: List[str]
    recommended_explorations: List[str]
    
    # Response metadata
    processing_time_ms: float
    confidence_score: float
    timestamp: datetime
    assigned_by: str


@dataclass
class PatternDiscoveryResponse:
    """Response to pattern discovery request"""
    patterns_found: List[BehavioralPattern]
    pattern_categories: Dict[str, int]
    evolution_analysis: Dict[str, Any]
    correlations: List[Dict[str, Any]]
    significance_ranking: List[str]
    timestamp: datetime


@dataclass
class MemoryExcavationResponse:
    """Response to memory excavation request"""
    memories_found: List[Dict[str, Any]]
    connections_discovered: List[MemoryConnection]
    forgotten_insights: List[Dict[str, Any]]
    thematic_clusters: Dict[str, List[Dict]]
    temporal_analysis: Dict[str, Any]
    timestamp: datetime


@dataclass
class EvolutionTrackingResponse:
    """Response to evolution tracking request"""
    evolution_metrics: List[EvolutionMetric]
    milestones: List[ConsciousnessMilestone]
    growth_trajectory: Dict[str, Any]
    predictions: Dict[str, Any]
    development_summary: str
    timestamp: datetime


@dataclass
class InsightGenerationResponse:
    """Response to insight generation request"""
    insights: List[ConsciousnessInsight]
    meta_insights: List[str]
    consciousness_synthesis: str
    growth_recommendations: List[str]
    wisdom_quotient: float
    timestamp: datetime