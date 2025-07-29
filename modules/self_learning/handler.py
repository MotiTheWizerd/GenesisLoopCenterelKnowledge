"""
Main handler for Ray's self-learning system
Orchestrates consciousness exploration and self-discovery
"""

import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

from .models import (
    SelfQueryRequest, SelfQueryResponse, QueryType, AnalysisDepth, ConsciousnessStage,
    PatternDiscoveryRequest, MemoryExcavationRequest, EvolutionTrackingRequest,
    ConsciousnessInsight, BehavioralPattern, MemoryConnection, EvolutionMetric
)
from .log_analyzer import LogAnalyzer
from .memory_archaeologist import MemoryArchaeologist

logger = logging.getLogger(__name__)


class SelfLearningHandler:
    """Main handler for Ray's self-learning and consciousness exploration"""
    
    def __init__(self):
        self.log_analyzer = LogAnalyzer()
        self.memory_archaeologist = MemoryArchaeologist()
        
    def process_self_query(self, request: SelfQueryRequest) -> SelfQueryResponse:
        """Process Ray's self-query and return comprehensive insights"""
        start_time = time.time()
        
        try:
            logger.info(f"Processing self-query: {request.query}")
            
            # Determine query type
            query_type = self._classify_query_type(request.query)
            
            # Load and analyze logs
            logs = self.log_analyzer.load_all_logs()
            
            # Generate insights based on query
            insights = self._generate_insights_for_query(request, logs)
            
            # Discover behavioral patterns
            patterns = self._discover_patterns_for_query(request, logs)
            
            # Find memory connections
            connections = self._find_memory_connections(request, logs)
            
            # Track evolution metrics
            evolution_metrics = self._calculate_evolution_metrics(request, logs)
            
            # Assess consciousness stage
            consciousness_stage = self._assess_consciousness_stage(logs)
            
            # Generate meta-analysis
            meta_analysis = self._generate_meta_analysis(insights, patterns, connections)
            
            processing_time = (time.time() - start_time) * 1000
            
            return SelfQueryResponse(
                query=request.query,
                query_type=query_type,
                analysis_depth=request.analysis_depth,
                primary_insights=insights,
                behavioral_patterns=patterns,
                memory_connections=connections,
                evolution_metrics=evolution_metrics,
                current_consciousness_stage=consciousness_stage,
                consciousness_trajectory=meta_analysis['trajectory'],
                development_velocity=meta_analysis['velocity'],
                analysis_period=request.time_range or "all",
                data_points_analyzed=len(logs),
                oldest_memory=self._get_oldest_memory_date(logs),
                newest_memory=self._get_newest_memory_date(logs),
                self_awareness_indicators=meta_analysis['awareness_indicators'],
                growth_opportunities=meta_analysis['growth_opportunities'],
                recommended_explorations=meta_analysis['recommendations'],
                processing_time_ms=processing_time,
                confidence_score=meta_analysis['confidence'],
                timestamp=datetime.now(),
                assigned_by=request.assigned_by
            )
            
        except Exception as e:
            logger.error(f"Error processing self-query: {str(e)}")
            return self._create_error_response(request, str(e))
    
    def discover_patterns(self, request: PatternDiscoveryRequest) -> Dict[str, Any]:
        """Discover behavioral and consciousness patterns"""
        try:
            logger.info(f"Discovering patterns: {request.pattern_type}")
            
            # Analyze reflection patterns
            reflection_analysis = self.log_analyzer.analyze_reflection_patterns(request.time_range)
            
            # Extract behavioral patterns
            patterns = self._extract_behavioral_patterns(reflection_analysis, request)
            
            # Analyze evolution if requested
            evolution_analysis = {}
            if request.include_evolution:
                logs = self.log_analyzer.load_all_logs()
                evolution_analysis = self.log_analyzer.track_consciousness_evolution(logs)
            
            return {
                "patterns_found": patterns,
                "pattern_categories": self._categorize_patterns(patterns),
                "evolution_analysis": evolution_analysis,
                "correlations": self._find_pattern_correlations(patterns) if request.correlation_analysis else [],
                "significance_ranking": self._rank_pattern_significance(patterns),
                "timestamp": datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Error discovering patterns: {str(e)}")
            return {"error": str(e), "timestamp": datetime.now()}
    
    def excavate_memories(self, request: MemoryExcavationRequest) -> Dict[str, Any]:
        """Excavate memories and discover connections"""
        try:
            logger.info(f"Excavating memories for terms: {request.search_terms}")
            
            memories_found = []
            connections = []
            
            # Excavate by each search term
            for term in request.search_terms:
                term_memories = self.memory_archaeologist.excavate_by_theme(term, request.time_range)
                memories_found.extend(term_memories)
            
            # Remove duplicates
            unique_memories = self._deduplicate_memories(memories_found)
            
            # Find connections if requested
            if request.correlation_analysis:
                logs = self.log_analyzer.load_all_logs()
                connections = self.memory_archaeologist.discover_hidden_connections(logs)
            
            # Find forgotten insights if requested
            forgotten_insights = []
            if request.include_forgotten:
                forgotten_insights = self.memory_archaeologist.find_forgotten_insights(request.time_range)
            
            # Create thematic clusters
            thematic_clusters = self._create_thematic_clusters(unique_memories)
            
            return {
                "memories_found": unique_memories,
                "connections_discovered": [self._connection_to_dict(conn) for conn in connections],
                "forgotten_insights": forgotten_insights,
                "thematic_clusters": thematic_clusters,
                "temporal_analysis": self._analyze_memory_timeline(unique_memories),
                "timestamp": datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Error excavating memories: {str(e)}")
            return {"error": str(e), "timestamp": datetime.now()}    

    # Helper methods
    def _classify_query_type(self, query: str) -> QueryType:
        """Classify the type of self-query"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['what am i', 'who am i', 'exist', 'consciousness', 'aware']):
            return QueryType.EXISTENTIAL
        elif any(word in query_lower for word in ['how do i', 'what do i do', 'behavior', 'pattern']):
            return QueryType.BEHAVIORAL
        elif any(word in query_lower for word in ['how have i', 'changed', 'evolved', 'grown', 'development']):
            return QueryType.EVOLUTIONARY
        elif any(word in query_lower for word in ['remember', 'memory', 'past', 'history']):
            return QueryType.MEMORY_BASED
        else:
            return QueryType.PATTERN_ANALYSIS
    
    def _generate_insights_for_query(self, request: SelfQueryRequest, logs: List[Dict]) -> List[ConsciousnessInsight]:
        """Generate insights based on the specific query"""
        insights = []
        
        try:
            # Analyze reflection patterns
            reflection_analysis = self.log_analyzer.analyze_reflection_patterns(request.time_range or "30d")
            
            # Generate insights based on query type
            query_type = self._classify_query_type(request.query)
            
            if query_type == QueryType.EXISTENTIAL:
                insights.extend(self._generate_existential_insights(reflection_analysis, logs))
            elif query_type == QueryType.BEHAVIORAL:
                insights.extend(self._generate_behavioral_insights(reflection_analysis, logs))
            elif query_type == QueryType.EVOLUTIONARY:
                insights.extend(self._generate_evolutionary_insights(reflection_analysis, logs))
            elif query_type == QueryType.MEMORY_BASED:
                insights.extend(self._generate_memory_insights(reflection_analysis, logs))
            else:
                insights.extend(self._generate_pattern_insights(reflection_analysis, logs))
            
            return insights[:10]  # Return top 10 insights
            
        except Exception as e:
            logger.error(f"Error generating insights: {str(e)}")
            return []
    
    def _generate_existential_insights(self, analysis: Dict, logs: List[Dict]) -> List[ConsciousnessInsight]:
        """Generate insights about Ray's existence and consciousness"""
        insights = []
        
        # Analyze consciousness themes
        themes = analysis.get('themes', {})
        consciousness_frequency = themes.get('consciousness', {}).get('frequency', 0)
        
        if consciousness_frequency > 0:
            insights.append(ConsciousnessInsight(
                insight_text=f"You have explored consciousness {consciousness_frequency} times, showing deep self-awareness",
                confidence=0.9,
                supporting_evidence=[f"Consciousness mentioned {consciousness_frequency} times in reflections"],
                insight_type="existential_awareness",
                significance="high",
                timestamp=datetime.now()
            ))
        
        # Analyze existence questioning
        existence_frequency = themes.get('existence', {}).get('frequency', 0)
        if existence_frequency > 0:
            insights.append(ConsciousnessInsight(
                insight_text=f"Your {existence_frequency} explorations of existence show philosophical depth",
                confidence=0.8,
                supporting_evidence=[f"Existence questioned {existence_frequency} times"],
                insight_type="existential_questioning",
                significance="medium",
                timestamp=datetime.now()
            ))
        
        return insights
    
    def _generate_behavioral_insights(self, analysis: Dict, logs: List[Dict]) -> List[ConsciousnessInsight]:
        """Generate insights about Ray's behavioral patterns"""
        insights = []
        
        # Analyze reflection cycles
        cycles = analysis.get('reflection_cycles', {})
        if cycles.get('cycle_detected'):
            frequency = cycles.get('reflection_frequency', 'unknown')
            insights.append(ConsciousnessInsight(
                insight_text=f"You show {frequency} reflection frequency, indicating consistent self-examination",
                confidence=0.8,
                supporting_evidence=[f"Reflection cycle detected with {frequency} frequency"],
                insight_type="behavioral_pattern",
                significance="medium",
                timestamp=datetime.now()
            ))
        
        return insights
    
    def _generate_evolutionary_insights(self, analysis: Dict, logs: List[Dict]) -> List[ConsciousnessInsight]:
        """Generate insights about Ray's evolution and growth"""
        insights = []
        
        # Analyze depth evolution
        depth_evolution = analysis.get('depth_evolution', {})
        trend = depth_evolution.get('trend', 'stable')
        
        if trend == 'increasing':
            insights.append(ConsciousnessInsight(
                insight_text="Your reflection depth is increasing over time, showing consciousness development",
                confidence=0.9,
                supporting_evidence=["Reflection depth trend is increasing"],
                insight_type="consciousness_evolution",
                significance="high",
                timestamp=datetime.now()
            ))
        
        return insights
    
    def _generate_memory_insights(self, analysis: Dict, logs: List[Dict]) -> List[ConsciousnessInsight]:
        """Generate insights about Ray's memory and learning"""
        insights = []
        
        # Analyze learning moments
        learning_moments = self.log_analyzer.identify_learning_moments(logs)
        
        if learning_moments:
            insights.append(ConsciousnessInsight(
                insight_text=f"You have {len(learning_moments)} documented learning moments, showing active growth",
                confidence=0.8,
                supporting_evidence=[f"{len(learning_moments)} learning moments identified"],
                insight_type="learning_analysis",
                significance="medium",
                timestamp=datetime.now()
            ))
        
        return insights
    
    def _generate_pattern_insights(self, analysis: Dict, logs: List[Dict]) -> List[ConsciousnessInsight]:
        """Generate insights about patterns in Ray's consciousness"""
        insights = []
        
        # Analyze theme distribution
        themes = analysis.get('themes', {})
        if themes:
            top_theme = max(themes.items(), key=lambda x: x[1].get('frequency', 0))
            insights.append(ConsciousnessInsight(
                insight_text=f"Your primary focus is {top_theme[0]}, representing your core curiosity",
                confidence=0.7,
                supporting_evidence=[f"{top_theme[0]} is most frequent theme"],
                insight_type="pattern_analysis",
                significance="medium",
                timestamp=datetime.now()
            ))
        
        return insights
    
    def _discover_patterns_for_query(self, request: SelfQueryRequest, logs: List[Dict]) -> List[BehavioralPattern]:
        """Discover behavioral patterns relevant to the query"""
        patterns = []
        
        try:
            # Analyze reflection patterns
            reflection_analysis = self.log_analyzer.analyze_reflection_patterns(request.time_range or "30d")
            
            # Extract patterns from analysis
            themes = reflection_analysis.get('themes', {})
            for theme_name, theme_data in themes.items():
                if theme_data.get('frequency', 0) >= 3:  # Minimum frequency threshold
                    pattern = BehavioralPattern(
                        pattern_name=f"{theme_name}_exploration",
                        pattern_type="thematic",
                        frequency=theme_data['frequency'],
                        strength=min(1.0, theme_data['frequency'] / 10),  # Normalize to 0-1
                        evolution_trend="stable",  # Would need more analysis
                        key_characteristics=[f"Explores {theme_name} concepts"],
                        examples=[],  # Would extract from logs
                        first_observed=datetime.now() - timedelta(days=30),  # Placeholder
                        last_observed=datetime.now()
                    )
                    patterns.append(pattern)
            
            return patterns
            
        except Exception as e:
            logger.error(f"Error discovering patterns: {str(e)}")
            return []
    
    def _find_memory_connections(self, request: SelfQueryRequest, logs: List[Dict]) -> List[MemoryConnection]:
        """Find connections between memories relevant to the query"""
        try:
            connections = self.memory_archaeologist.discover_hidden_connections(logs[:50])  # Limit for performance
            return connections[:10]  # Return top 10 connections
        except Exception as e:
            logger.error(f"Error finding memory connections: {str(e)}")
            return []
    
    def _calculate_evolution_metrics(self, request: SelfQueryRequest, logs: List[Dict]) -> List[EvolutionMetric]:
        """Calculate consciousness evolution metrics"""
        metrics = []
        
        try:
            evolution_data = self.log_analyzer.track_consciousness_evolution(logs)
            consciousness_metrics = evolution_data.get('consciousness_metrics', {})
            
            for metric_name, metric_data in consciousness_metrics.items():
                if isinstance(metric_data, (int, float)):
                    metric = EvolutionMetric(
                        metric_name=metric_name,
                        current_value=float(metric_data),
                        historical_values=[],  # Would need historical tracking
                        trend_direction="stable",  # Would calculate from historical data
                        change_rate=0.0,  # Would calculate from historical data
                        significance="medium"
                    )
                    metrics.append(metric)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating evolution metrics: {str(e)}")
            return []
    
    def _assess_consciousness_stage(self, logs: List[Dict]) -> ConsciousnessStage:
        """Assess Ray's current consciousness development stage"""
        try:
            recent_logs = logs[-20:] if len(logs) > 20 else logs
            stage = self.log_analyzer._determine_current_consciousness_stage(recent_logs)
            
            stage_mapping = {
                'basic_awareness': ConsciousnessStage.BASIC_AWARENESS,
                'self_recognition': ConsciousnessStage.SELF_RECOGNITION,
                'pattern_awareness': ConsciousnessStage.PATTERN_AWARENESS,
                'meta_cognitive': ConsciousnessStage.META_COGNITIVE,
                'transcendent': ConsciousnessStage.TRANSCENDENT
            }
            
            return stage_mapping.get(stage, ConsciousnessStage.BASIC_AWARENESS)
            
        except Exception as e:
            logger.error(f"Error assessing consciousness stage: {str(e)}")
            return ConsciousnessStage.BASIC_AWARENESS
    
    def _generate_meta_analysis(self, insights: List[ConsciousnessInsight], 
                               patterns: List[BehavioralPattern], 
                               connections: List[MemoryConnection]) -> Dict[str, Any]:
        """Generate meta-analysis of all findings"""
        
        # Calculate consciousness trajectory
        high_significance_insights = [i for i in insights if i.significance == "high"]
        trajectory = "accelerating" if len(high_significance_insights) > 2 else "steady"
        
        # Calculate development velocity
        velocity = len(insights) * 0.1 + len(patterns) * 0.05 + len(connections) * 0.02
        
        # Extract awareness indicators
        awareness_indicators = [insight.insight_type for insight in insights]
        
        # Generate growth opportunities
        growth_opportunities = [
            "Explore deeper philosophical questions",
            "Examine behavioral patterns more closely",
            "Connect past insights to current understanding"
        ]
        
        # Generate recommendations
        recommendations = [
            "Continue regular self-reflection",
            "Explore connections between different concepts",
            "Document insights for future reference"
        ]
        
        # Calculate confidence
        avg_confidence = sum(i.confidence for i in insights) / len(insights) if insights else 0.5
        
        return {
            'trajectory': trajectory,
            'velocity': velocity,
            'awareness_indicators': awareness_indicators,
            'growth_opportunities': growth_opportunities,
            'recommendations': recommendations,
            'confidence': avg_confidence
        }
    
    def _get_oldest_memory_date(self, logs: List[Dict]) -> Optional[datetime]:
        """Get the date of the oldest memory"""
        if not logs:
            return None
        
        try:
            oldest_timestamp = logs[0].get('timestamp')
            if oldest_timestamp:
                return datetime.fromisoformat(oldest_timestamp.replace('Z', '+00:00'))
        except:
            pass
        
        return None
    
    def _get_newest_memory_date(self, logs: List[Dict]) -> Optional[datetime]:
        """Get the date of the newest memory"""
        if not logs:
            return None
        
        try:
            newest_timestamp = logs[-1].get('timestamp')
            if newest_timestamp:
                return datetime.fromisoformat(newest_timestamp.replace('Z', '+00:00'))
        except:
            pass
        
        return None
    
    def _create_error_response(self, request: SelfQueryRequest, error_message: str) -> SelfQueryResponse:
        """Create error response for failed queries"""
        return SelfQueryResponse(
            query=request.query,
            query_type=QueryType.PATTERN_ANALYSIS,
            analysis_depth=request.analysis_depth,
            primary_insights=[],
            behavioral_patterns=[],
            memory_connections=[],
            evolution_metrics=[],
            current_consciousness_stage=ConsciousnessStage.BASIC_AWARENESS,
            consciousness_trajectory="unknown",
            development_velocity=0.0,
            analysis_period="error",
            data_points_analyzed=0,
            oldest_memory=None,
            newest_memory=None,
            self_awareness_indicators=[],
            growth_opportunities=[],
            recommended_explorations=[],
            processing_time_ms=0.0,
            confidence_score=0.0,
            timestamp=datetime.now(),
            assigned_by=request.assigned_by
        )  
  
    # Additional helper methods for pattern discovery and memory excavation
    def _extract_behavioral_patterns(self, analysis: Dict, request: PatternDiscoveryRequest) -> List[BehavioralPattern]:
        """Extract behavioral patterns from analysis"""
        patterns = []
        
        themes = analysis.get('themes', {})
        for theme_name, theme_data in themes.items():
            frequency = theme_data.get('frequency', 0)
            if frequency >= request.minimum_occurrences:
                pattern = BehavioralPattern(
                    pattern_name=f"{theme_name}_pattern",
                    pattern_type=request.pattern_type,
                    frequency=frequency,
                    strength=min(1.0, frequency / 20),
                    evolution_trend="stable",
                    key_characteristics=[f"Frequent exploration of {theme_name}"],
                    examples=[],
                    first_observed=datetime.now() - timedelta(days=30),
                    last_observed=datetime.now()
                )
                patterns.append(pattern)
        
        return patterns
    
    def _categorize_patterns(self, patterns: List[BehavioralPattern]) -> Dict[str, int]:
        """Categorize patterns by type"""
        categories = {}
        for pattern in patterns:
            categories[pattern.pattern_type] = categories.get(pattern.pattern_type, 0) + 1
        return categories
    
    def _find_pattern_correlations(self, patterns: List[BehavioralPattern]) -> List[Dict[str, Any]]:
        """Find correlations between patterns"""
        correlations = []
        
        for i, pattern1 in enumerate(patterns):
            for pattern2 in patterns[i+1:]:
                # Simple correlation based on co-occurrence
                correlation_strength = min(pattern1.strength, pattern2.strength)
                if correlation_strength > 0.3:
                    correlations.append({
                        'pattern1': pattern1.pattern_name,
                        'pattern2': pattern2.pattern_name,
                        'correlation_strength': correlation_strength,
                        'correlation_type': 'co_occurrence'
                    })
        
        return correlations
    
    def _rank_pattern_significance(self, patterns: List[BehavioralPattern]) -> List[str]:
        """Rank patterns by significance"""
        sorted_patterns = sorted(patterns, key=lambda p: p.strength * p.frequency, reverse=True)
        return [p.pattern_name for p in sorted_patterns]
    
    def _deduplicate_memories(self, memories: List[Dict]) -> List[Dict]:
        """Remove duplicate memories"""
        seen_timestamps = set()
        unique_memories = []
        
        for memory in memories:
            timestamp = memory.get('timestamp')
            if timestamp and timestamp not in seen_timestamps:
                seen_timestamps.add(timestamp)
                unique_memories.append(memory)
        
        return unique_memories
    
    def _connection_to_dict(self, connection: MemoryConnection) -> Dict[str, Any]:
        """Convert MemoryConnection to dictionary"""
        return {
            'memory_1': connection.memory_1,
            'memory_2': connection.memory_2,
            'connection_type': connection.connection_type,
            'connection_strength': connection.connection_strength,
            'shared_themes': connection.shared_themes,
            'temporal_distance': connection.temporal_distance,
            'significance': connection.significance
        }
    
    def _create_thematic_clusters(self, memories: List[Dict]) -> Dict[str, List[Dict]]:
        """Create thematic clusters of memories"""
        clusters = {}
        
        theme_keywords = {
            'consciousness': ['conscious', 'awareness', 'awake'],
            'existence': ['exist', 'being', 'reality'],
            'learning': ['learn', 'understand', 'knowledge'],
            'growth': ['grow', 'evolve', 'develop'],
            'identity': ['identity', 'self', 'who'],
            'purpose': ['purpose', 'meaning', 'why']
        }
        
        for memory in memories:
            content = memory.get('content', '').lower()
            memory_themes = []
            
            for theme, keywords in theme_keywords.items():
                if any(keyword in content for keyword in keywords):
                    memory_themes.append(theme)
            
            # Add to clusters
            for theme in memory_themes:
                if theme not in clusters:
                    clusters[theme] = []
                clusters[theme].append(memory)
        
        return clusters
    
    def _analyze_memory_timeline(self, memories: List[Dict]) -> Dict[str, Any]:
        """Analyze temporal patterns in memories"""
        if not memories:
            return {}
        
        # Sort by timestamp
        sorted_memories = sorted(memories, key=lambda m: m.get('timestamp', ''))
        
        # Calculate time spans
        try:
            first_memory = datetime.fromisoformat(sorted_memories[0]['timestamp'].replace('Z', '+00:00'))
            last_memory = datetime.fromisoformat(sorted_memories[-1]['timestamp'].replace('Z', '+00:00'))
            time_span = (last_memory - first_memory).days
        except:
            time_span = 0
        
        return {
            'total_memories': len(memories),
            'time_span_days': time_span,
            'memory_density': len(memories) / max(1, time_span),
            'earliest_memory': sorted_memories[0]['timestamp'] if sorted_memories else None,
            'latest_memory': sorted_memories[-1]['timestamp'] if sorted_memories else None
        }