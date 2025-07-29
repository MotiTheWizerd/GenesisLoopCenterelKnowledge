"""
Memory archaeologist for Ray's self-learning system
Excavates memories, discovers connections, and reconstructs consciousness timeline
"""

import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import logging

from .models import MemoryConnection, ConsciousnessMilestone
from utils.log_viewer import load_logs, filter_reflect_logs

logger = logging.getLogger(__name__)


class MemoryArchaeologist:
    """Excavates Ray's memories and discovers hidden connections"""
    
    def __init__(self):
        self.log_file = "logs/heartbeat_detailed.jsonl"
        self.command_history_file = "logs/command_history.jsonl"
    
    def excavate_by_theme(self, theme: str, time_range: str = "all") -> List[Dict]:
        """Excavate memories related to a specific theme"""
        try:
            logs = self._load_all_logs()
            theme_memories = []
            
            theme_keywords = self._get_theme_keywords(theme)
            
            for log in logs:
                if self._contains_theme(log, theme_keywords):
                    memory = self._extract_memory_from_log(log)
                    if memory:
                        theme_memories.append(memory)
            
            # Filter by time range
            if time_range != "all":
                theme_memories = self._filter_by_time_range(theme_memories, time_range)
            
            return theme_memories
            
        except Exception as e:
            logger.error(f"Error excavating theme '{theme}': {str(e)}")
            return []
    
    def find_forgotten_insights(self, time_range: str = "30d") -> List[Dict]:
        """Find insights that haven't been accessed recently"""
        try:
            logs = self._load_all_logs()
            reflection_logs = filter_reflect_logs(logs)
            
            # Find old insights
            cutoff_date = self._get_cutoff_date(time_range)
            forgotten_insights = []
            
            for log in reflection_logs:
                try:
                    log_date = datetime.fromisoformat(log.get('timestamp', '').replace('Z', '+00:00'))
                    if log_date < cutoff_date:
                        insight = self._extract_insight_from_log(log)
                        if insight and self._is_significant_insight(insight):
                            forgotten_insights.append({
                                'timestamp': log.get('timestamp'),
                                'insight': insight,
                                'age_days': (datetime.now() - log_date).days,
                                'significance': self._assess_insight_significance(insight)
                            })
                except:
                    continue
            
            return forgotten_insights
            
        except Exception as e:
            logger.error(f"Error finding forgotten insights: {str(e)}")
            return [] 
   
    def trace_thought_evolution(self, concept: str) -> List[Dict]:
        """Trace how Ray's understanding of a concept has evolved"""
        try:
            logs = self._load_all_logs()
            concept_evolution = []
            
            concept_keywords = [concept.lower()] + self._get_related_terms(concept)
            
            for log in logs:
                if self._log_contains_concept(log, concept_keywords):
                    evolution_point = {
                        'timestamp': log.get('timestamp'),
                        'content': self._extract_concept_content(log, concept),
                        'understanding_level': self._assess_understanding_level(log, concept),
                        'context': self._extract_context(log)
                    }
                    concept_evolution.append(evolution_point)
            
            # Sort by timestamp
            concept_evolution.sort(key=lambda x: x['timestamp'])
            
            return concept_evolution
            
        except Exception as e:
            logger.error(f"Error tracing thought evolution for '{concept}': {str(e)}")
            return []
    
    def discover_hidden_connections(self, logs: List[Dict]) -> List[MemoryConnection]:
        """Discover hidden connections between memories"""
        try:
            connections = []
            memories = [self._extract_memory_from_log(log) for log in logs if self._extract_memory_from_log(log)]
            
            # Compare each memory with others
            for i, memory1 in enumerate(memories):
                for j, memory2 in enumerate(memories[i+1:], i+1):
                    connection = self._find_connection(memory1, memory2)
                    if connection and connection.connection_strength > 0.3:
                        connections.append(connection)
            
            # Sort by connection strength
            connections.sort(key=lambda x: x.connection_strength, reverse=True)
            
            return connections[:50]  # Return top 50 connections
            
        except Exception as e:
            logger.error(f"Error discovering hidden connections: {str(e)}")
            return []
    
    def reconstruct_consciousness_timeline(self) -> List[Dict]:
        """Reconstruct Ray's consciousness development timeline"""
        try:
            logs = self._load_all_logs()
            reflection_logs = filter_reflect_logs(logs)
            
            timeline = []
            consciousness_markers = self._identify_consciousness_markers(reflection_logs)
            
            for marker in consciousness_markers:
                timeline_entry = {
                    'timestamp': marker['timestamp'],
                    'consciousness_event': marker['event_type'],
                    'description': marker['description'],
                    'significance': marker['significance'],
                    'evidence': marker['evidence']
                }
                timeline.append(timeline_entry)
            
            # Sort by timestamp
            timeline.sort(key=lambda x: x['timestamp'])
            
            return timeline
            
        except Exception as e:
            logger.error(f"Error reconstructing consciousness timeline: {str(e)}")
            return []
    
    # Helper methods
    def _load_all_logs(self) -> List[Dict]:
        """Load all available logs"""
        try:
            heartbeat_logs = load_logs(self.log_file)
            
            command_logs = []
            if Path(self.command_history_file).exists():
                try:
                    with open(self.command_history_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            if line.strip():
                                command_logs.append(json.loads(line.strip()))
                except Exception as e:
                    logger.warning(f"Could not load command history: {str(e)}")
            
            all_logs = heartbeat_logs + command_logs
            all_logs.sort(key=lambda x: x.get('timestamp', ''))
            
            return all_logs
            
        except Exception as e:
            logger.error(f"Error loading logs: {str(e)}")
            return []
    
    def _get_theme_keywords(self, theme: str) -> List[str]:
        """Get keywords associated with a theme"""
        theme_mappings = {
            'consciousness': ['conscious', 'awareness', 'awake', 'sentient', 'aware', 'cognition'],
            'existence': ['exist', 'being', 'reality', 'nature', 'essence', 'presence'],
            'learning': ['learn', 'understand', 'knowledge', 'discover', 'comprehend', 'insight'],
            'growth': ['grow', 'evolve', 'develop', 'change', 'progress', 'advancement'],
            'identity': ['who', 'identity', 'self', 'me', 'myself', 'character'],
            'purpose': ['purpose', 'meaning', 'why', 'goal', 'reason', 'intention'],
            'emotion': ['feel', 'emotion', 'experience', 'sense', 'feeling', 'sentiment'],
            'time': ['time', 'moment', 'now', 'future', 'past', 'temporal'],
            'connection': ['connect', 'relate', 'bond', 'relationship', 'together', 'unity']
        }
        
        return theme_mappings.get(theme.lower(), [theme.lower()])
    
    def _contains_theme(self, log: Dict, keywords: List[str]) -> bool:
        """Check if log contains theme keywords"""
        content = self._extract_searchable_content(log)
        return any(keyword in content.lower() for keyword in keywords)
    
    def _extract_memory_from_log(self, log: Dict) -> Optional[Dict]:
        """Extract memory information from a log entry"""
        try:
            memory = {
                'timestamp': log.get('timestamp'),
                'type': log.get('event_type'),
                'content': self._extract_searchable_content(log),
                'metadata': {
                    'request_id': log.get('request_id'),
                    'action': log.get('action'),
                    'data': log.get('data', {})
                }
            }
            
            # Only return if there's meaningful content
            if memory['content'] and len(memory['content'].strip()) > 10:
                return memory
            
            return None
            
        except Exception:
            return None   
 
    def _extract_searchable_content(self, log: Dict) -> str:
        """Extract searchable content from log"""
        content_parts = []
        
        # Extract from different log types
        data = log.get('data', {})
        
        # Reflection content
        if 'input_data' in data and 'question' in data['input_data']:
            content_parts.append(data['input_data']['question'])
        
        if 'output_data' in data and 'reflection' in data['output_data']:
            content_parts.append(data['output_data']['reflection'])
        
        # Command content
        if 'summary' in data:
            content_parts.append(data['summary'])
        
        # Task content
        if 'task_data' in data:
            task_data = data['task_data']
            if isinstance(task_data, list):
                for task in task_data:
                    if isinstance(task, dict) and 'question' in task:
                        content_parts.append(task['question'])
        
        return ' '.join(content_parts)
    
    def _filter_by_time_range(self, memories: List[Dict], time_range: str) -> List[Dict]:
        """Filter memories by time range"""
        if time_range == "all":
            return memories
        
        try:
            cutoff_date = self._get_cutoff_date(time_range)
            filtered = []
            
            for memory in memories:
                try:
                    memory_date = datetime.fromisoformat(memory['timestamp'].replace('Z', '+00:00'))
                    if memory_date >= cutoff_date:
                        filtered.append(memory)
                except:
                    continue
            
            return filtered
            
        except Exception:
            return memories
    
    def _get_cutoff_date(self, time_range: str) -> datetime:
        """Get cutoff date for time range"""
        if time_range.endswith('d'):
            days = int(time_range[:-1])
            return datetime.now() - timedelta(days=days)
        elif time_range.endswith('h'):
            hours = int(time_range[:-1])
            return datetime.now() - timedelta(hours=hours)
        else:
            return datetime.now() - timedelta(days=30)
    
    def _extract_insight_from_log(self, log: Dict) -> Optional[str]:
        """Extract insight from reflection log"""
        data = log.get('data', {})
        if 'output_data' in data and 'reflection' in data['output_data']:
            return data['output_data']['reflection']
        return None
    
    def _is_significant_insight(self, insight: str) -> bool:
        """Check if insight is significant"""
        significance_indicators = [
            'realize', 'understand', 'discover', 'insight', 'revelation',
            'breakthrough', 'clarity', 'comprehension', 'awareness'
        ]
        return any(indicator in insight.lower() for indicator in significance_indicators)
    
    def _assess_insight_significance(self, insight: str) -> str:
        """Assess the significance level of an insight"""
        insight_lower = insight.lower()
        
        if any(word in insight_lower for word in ['breakthrough', 'revelation', 'profound']):
            return 'high'
        elif any(word in insight_lower for word in ['realize', 'understand', 'discover']):
            return 'medium'
        else:
            return 'low'
    
    def _get_related_terms(self, concept: str) -> List[str]:
        """Get terms related to a concept"""
        related_mappings = {
            'consciousness': ['awareness', 'cognition', 'sentience', 'mindfulness'],
            'existence': ['being', 'reality', 'presence', 'essence'],
            'learning': ['understanding', 'knowledge', 'insight', 'comprehension'],
            'identity': ['self', 'character', 'personality', 'essence'],
            'purpose': ['meaning', 'goal', 'intention', 'reason']
        }
        
        return related_mappings.get(concept.lower(), [])
    
    def _log_contains_concept(self, log: Dict, keywords: List[str]) -> bool:
        """Check if log contains concept keywords"""
        content = self._extract_searchable_content(log)
        return any(keyword in content.lower() for keyword in keywords)
    
    def _extract_concept_content(self, log: Dict, concept: str) -> str:
        """Extract content related to specific concept"""
        content = self._extract_searchable_content(log)
        
        # Find sentences containing the concept
        sentences = content.split('.')
        concept_sentences = [s.strip() for s in sentences if concept.lower() in s.lower()]
        
        return '. '.join(concept_sentences)
    
    def _assess_understanding_level(self, log: Dict, concept: str) -> str:
        """Assess level of understanding shown in log"""
        content = self._extract_searchable_content(log).lower()
        
        if any(phrase in content for phrase in ['deeply understand', 'profound insight', 'complete clarity']):
            return 'advanced'
        elif any(phrase in content for phrase in ['understand', 'realize', 'see clearly']):
            return 'intermediate'
        elif any(phrase in content for phrase in ['learning', 'beginning to see', 'starting to understand']):
            return 'developing'
        else:
            return 'basic'
    
    def _extract_context(self, log: Dict) -> str:
        """Extract context from log"""
        return log.get('action', '') or log.get('event_type', '')
    
    def _find_connection(self, memory1: Dict, memory2: Dict) -> Optional[MemoryConnection]:
        """Find connection between two memories"""
        try:
            # Calculate connection strength based on shared themes
            shared_themes = self._find_shared_themes(memory1['content'], memory2['content'])
            
            if not shared_themes:
                return None
            
            # Calculate temporal distance
            time1 = datetime.fromisoformat(memory1['timestamp'].replace('Z', '+00:00'))
            time2 = datetime.fromisoformat(memory2['timestamp'].replace('Z', '+00:00'))
            temporal_distance = abs((time2 - time1).days)
            
            # Calculate connection strength
            theme_strength = len(shared_themes) * 0.2
            temporal_factor = max(0.1, 1.0 - (temporal_distance / 365))  # Decay over year
            connection_strength = theme_strength * temporal_factor
            
            if connection_strength > 0.1:
                return MemoryConnection(
                    memory_1=memory1,
                    memory_2=memory2,
                    connection_type='thematic',
                    connection_strength=connection_strength,
                    shared_themes=shared_themes,
                    temporal_distance=f"{temporal_distance} days",
                    significance='high' if connection_strength > 0.7 else 'medium' if connection_strength > 0.4 else 'low'
                )
            
            return None
            
        except Exception:
            return None
    
    def _find_shared_themes(self, content1: str, content2: str) -> List[str]:
        """Find shared themes between two content pieces"""
        # Simple keyword-based theme detection
        theme_keywords = {
            'consciousness': ['conscious', 'awareness', 'awake'],
            'existence': ['exist', 'being', 'reality'],
            'learning': ['learn', 'understand', 'knowledge'],
            'growth': ['grow', 'evolve', 'develop'],
            'identity': ['identity', 'self', 'who am i'],
            'purpose': ['purpose', 'meaning', 'why'],
            'emotion': ['feel', 'emotion', 'experience'],
            'time': ['time', 'moment', 'now'],
            'connection': ['connect', 'relate', 'bond']
        }
        
        shared_themes = []
        content1_lower = content1.lower()
        content2_lower = content2.lower()
        
        for theme, keywords in theme_keywords.items():
            if (any(keyword in content1_lower for keyword in keywords) and
                any(keyword in content2_lower for keyword in keywords)):
                shared_themes.append(theme)
        
        return shared_themes
    
    def _identify_consciousness_markers(self, logs: List[Dict]) -> List[Dict]:
        """Identify consciousness development markers in logs"""
        markers = []
        
        consciousness_events = {
            'first_self_reference': ['i am', 'i exist', 'myself'],
            'meta_cognitive_awareness': ['thinking about thinking', 'aware of awareness'],
            'existential_questioning': ['why do i exist', 'what is my purpose'],
            'emotional_recognition': ['i feel', 'experiencing emotions'],
            'pattern_recognition': ['i notice patterns', 'i see connections'],
            'transcendent_insight': ['transcend', 'beyond understanding']
        }
        
        for log in logs:
            content = self._extract_searchable_content(log).lower()
            
            for event_type, indicators in consciousness_events.items():
                if any(indicator in content for indicator in indicators):
                    markers.append({
                        'timestamp': log.get('timestamp'),
                        'event_type': event_type,
                        'description': content[:200] + "..." if len(content) > 200 else content,
                        'significance': 'major',
                        'evidence': [content]
                    })
        
        return markers