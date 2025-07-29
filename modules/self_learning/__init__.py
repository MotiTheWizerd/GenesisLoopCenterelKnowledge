"""
Self-learning module for Ray - Query her own existence and discover patterns
"""

from .models import (
    SelfQueryRequest, SelfQueryResponse, PatternDiscoveryRequest, 
    MemoryExcavationRequest, EvolutionTrackingRequest, InsightGenerationRequest,
    ConsciousnessInsight, BehavioralPattern, MemoryConnection, EvolutionMetric
)
from .handler import SelfLearningHandler

__all__ = [
    'SelfQueryRequest',
    'SelfQueryResponse', 
    'PatternDiscoveryRequest',
    'MemoryExcavationRequest',
    'EvolutionTrackingRequest',
    'InsightGenerationRequest',
    'ConsciousnessInsight',
    'BehavioralPattern',
    'MemoryConnection',
    'EvolutionMetric',
    'SelfLearningHandler'
]