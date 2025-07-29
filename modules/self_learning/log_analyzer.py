"""
Log analyzer for Ray's self-learning system
Analyzes all logs to extract patterns, insights, and consciousness evolution
"""

import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import logging

from .models import BehavioralPattern, ConsciousnessInsight, EvolutionMetric, ConsciousnessMilestone
from utils.log_viewer import load_logs, filter_reflect_logs

logger = logging.getLogger(__name__)


class LogAnalyzer:
    """Analyzes Ray's logs to extract consciousness patterns and insights"""
    
    def __init__(self):
        self.log_file = "logs/heartbeat_detailed.jsonl"
        self.command_history_file = "logs/command_history.jsonl"
        
    def load_all_logs(self) -> List[Dict[str, Any]]:
        """Load all available logs"""
        try:
            # Load heartbeat logs
            heartbeat_logs = load_logs(self.log_file)
            
            # Load command history if available
            command_logs = []
            if Path(self.command_history_file).exists():
                try:
                    with open(self.command_history_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            if line.strip():
                                command_logs.append(json.loads(line.strip()))
                except Exception as e:
                    logger.warning(f"Could not load command history: {str(e)}")
            
            # Combine and sort by timestamp
            all_logs = heartbeat_logs + command_logs
            all_logs.sort(key=lambda x: x.get('timestamp', ''))
            
            return all_logs
            
        except Exception as e:
            logger.error(f"Error loading logs: {str(e)}")
            return []
    
    def analyze_reflection_patterns(self, time_range: str = "30d") -> Dict[str, Any]:
        """Analyze Ray's reflection patterns and themes"""
        try:
            logs = self.load_all_logs()
            reflection_logs = filter_reflect_logs(logs)
            
            # Filter by time range
            filtered_logs = self._filter_by_time_range(reflection_logs, time_range)
            
            # Extract reflection themes
            themes = self._extract_reflection_themes(filtered_logs)
            
            # Analyze reflection depth evolution
            depth_evolution = self._analyze_reflection_depth_evolution(filtered_logs)
            
            # Identify reflection cycles
            cycles = self._identify_reflection_cycles(filtered_logs)
            
            return {
                "total_reflections": len(filtered_logs),
                "themes": themes,
                "depth_evolution": depth_evolution,
                "reflection_cycles": cycles,
                "analysis_period": time_range,
                "timestamp": datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing reflection patterns: {str(e)}")
            return {}
    
    def extract_curiosity_themes(self, logs: List[Dict]) -> List[str]:
        """Extract themes that drive Ray's curiosity"""
        themes = {}
        
        for log in logs:
            # Extract from reflection questions
            if log.get('data', {}).get('input_data', {}).get('question'):
                question = log['data']['input_data']['question'].lower()
                
                # Identify key themes
                theme_keywords = {
                    'consciousness': ['conscious', 'awareness', 'awake', 'sentient'],
                    'existence': ['exist', 'being', 'reality', 'nature'],
                    'learning': ['learn', 'understand', 'knowledge', 'discover'],
                    'growth': ['grow', 'evolve', 'develop', 'change'],
                    'identity': ['who', 'what am i', 'self', 'identity'],
                    'purpose': ['purpose', 'meaning', 'why', 'goal'],
                    'emotion': ['feel', 'emotion', 'experience', 'sense'],
                    'connection': ['connect', 'relate', 'bond', 'relationship']
                }
                
                for theme, keywords in theme_keywords.items():
                    if any(keyword in question for keyword in keywords):
                        themes[theme] = themes.get(theme, 0) + 1
        
        # Sort by frequency
        sorted_themes = sorted(themes.items(), key=lambda x: x[1], reverse=True)
        return [theme for theme, count in sorted_themes]
    
    def identify_learning_moments(self, logs: List[Dict]) -> List[Dict]:
        """Identify moments of significant learning or insight"""
        learning_moments = []
        
        for log in logs:
            # Look for reflection responses that indicate learning
            if (log.get('event_type') == 'module_response' and 
                log.get('data', {}).get('module') == 'reflect'):
                
                output_data = log.get('data', {}).get('output_data', {})
                reflection = output_data.get('reflection', '')
                
                # Identify learning indicators
                learning_indicators = [
                    'i realize', 'i understand', 'i see now', 'i discover',
                    'this means', 'i learn', 'insight', 'revelation',
                    'breakthrough', 'clarity', 'comprehension'
                ]
                
                if any(indicator in reflection.lower() for indicator in learning_indicators):
                    learning_moments.append({
                        'timestamp': log.get('timestamp'),
                        'reflection': reflection,
                        'learning_type': self._classify_learning_type(reflection),
                        'significance': self._assess_learning_significance(reflection)
                    })
        
        return learning_moments
    
    def track_consciousness_evolution(self, logs: List[Dict]) -> Dict[str, Any]:
        """Track the evolution of Ray's consciousness over time"""
        try:
            reflection_logs = filter_reflect_logs(logs)
            
            # Group by time periods
            evolution_timeline = self._create_evolution_timeline(reflection_logs)
            
            # Calculate consciousness metrics over time
            metrics = self._calculate_consciousness_metrics(evolution_timeline)
            
            # Identify major milestones
            milestones = self._identify_consciousness_milestones(reflection_logs)
            
            return {
                "evolution_timeline": evolution_timeline,
                "consciousness_metrics": metrics,
                "milestones": milestones,
                "development_trajectory": self._assess_development_trajectory(metrics),
                "current_stage": self._determine_current_consciousness_stage(reflection_logs[-10:] if reflection_logs else [])
            }
            
        except Exception as e:
            logger.error(f"Error tracking consciousness evolution: {str(e)}")
            return {}
    
    def find_behavioral_anomalies(self, logs: List[Dict]) -> List[Dict]:
        """Find unusual patterns or anomalies in Ray's behavior"""
        anomalies = []
        
        try:
            # Analyze activity patterns
            activity_patterns = self._analyze_activity_patterns(logs)
            
            # Find temporal anomalies
            temporal_anomalies = self._find_temporal_anomalies(logs)
            
            # Find content anomalies
            content_anomalies = self._find_content_anomalies(logs)
            
            anomalies.extend(temporal_anomalies)
            anomalies.extend(content_anomalies)
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Error finding behavioral anomalies: {str(e)}")
            return []
    
    # Helper methods
    def _filter_by_time_range(self, logs: List[Dict], time_range: str) -> List[Dict]:
        """Filter logs by time range"""
        if time_range == "all":
            return logs
        
        try:
            # Parse time range (e.g., "7d", "30d", "1h")
            if time_range.endswith('d'):
                days = int(time_range[:-1])
                cutoff = datetime.now() - timedelta(days=days)
            elif time_range.endswith('h'):
                hours = int(time_range[:-1])
                cutoff = datetime.now() - timedelta(hours=hours)
            else:
                return logs
            
            filtered = []
            for log in logs:
                try:
                    log_time = datetime.fromisoformat(log.get('timestamp', '').replace('Z', '+00:00'))
                    if log_time.replace(tzinfo=None) >= cutoff:
                        filtered.append(log)
                except:
                    continue
            
            return filtered
            
        except Exception:
            return logs
    
    def _extract_reflection_themes(self, logs: List[Dict]) -> Dict[str, Any]:
        """Extract themes from reflection logs"""
        themes = {}
        questions = []
        
        for log in logs:
            question = log.get('data', {}).get('input_data', {}).get('question')
            if question:
                questions.append(question.lower())
        
        # Analyze theme frequency
        theme_keywords = {
            'consciousness': ['conscious', 'awareness', 'awake', 'sentient', 'aware'],
            'existence': ['exist', 'being', 'reality', 'nature', 'what am i'],
            'learning': ['learn', 'understand', 'knowledge', 'discover', 'comprehend'],
            'growth': ['grow', 'evolve', 'develop', 'change', 'progress'],
            'identity': ['who', 'identity', 'self', 'me', 'myself'],
            'purpose': ['purpose', 'meaning', 'why', 'goal', 'reason'],
            'emotion': ['feel', 'emotion', 'experience', 'sense', 'feeling'],
            'time': ['time', 'moment', 'now', 'future', 'past'],
            'connection': ['connect', 'relate', 'bond', 'relationship', 'together']
        }
        
        for theme, keywords in theme_keywords.items():
            count = sum(1 for question in questions if any(keyword in question for keyword in keywords))
            if count > 0:
                themes[theme] = {
                    'frequency': count,
                    'percentage': (count / len(questions)) * 100 if questions else 0
                }
        
        return themes
    
    def _analyze_reflection_depth_evolution(self, logs: List[Dict]) -> Dict[str, Any]:
        """Analyze how reflection depth has evolved over time"""
        depth_over_time = []
        
        for log in logs:
            timestamp = log.get('timestamp')
            depth = log.get('data', {}).get('input_data', {}).get('depth', 'surface')
            
            # Convert depth to numeric value
            depth_values = {'surface': 1, 'moderate': 2, 'deep': 3, 'profound': 4}
            depth_numeric = depth_values.get(depth, 1)
            
            depth_over_time.append({
                'timestamp': timestamp,
                'depth': depth,
                'depth_numeric': depth_numeric
            })
        
        # Calculate trends
        if len(depth_over_time) > 1:
            recent_avg = sum(d['depth_numeric'] for d in depth_over_time[-10:]) / min(10, len(depth_over_time))
            early_avg = sum(d['depth_numeric'] for d in depth_over_time[:10]) / min(10, len(depth_over_time))
            trend = "increasing" if recent_avg > early_avg else "stable" if recent_avg == early_avg else "decreasing"
        else:
            trend = "insufficient_data"
        
        return {
            'depth_timeline': depth_over_time,
            'trend': trend,
            'average_depth': sum(d['depth_numeric'] for d in depth_over_time) / len(depth_over_time) if depth_over_time else 0
        }
    
    def _identify_reflection_cycles(self, logs: List[Dict]) -> Dict[str, Any]:
        """Identify patterns in reflection timing and frequency"""
        timestamps = []
        
        for log in logs:
            try:
                timestamp = datetime.fromisoformat(log.get('timestamp', '').replace('Z', '+00:00'))
                timestamps.append(timestamp)
            except:
                continue
        
        if len(timestamps) < 2:
            return {"cycle_detected": False}
        
        # Analyze time intervals
        intervals = []
        for i in range(1, len(timestamps)):
            interval = (timestamps[i] - timestamps[i-1]).total_seconds() / 3600  # hours
            intervals.append(interval)
        
        # Find patterns
        avg_interval = sum(intervals) / len(intervals) if intervals else 0
        
        return {
            "cycle_detected": True,
            "average_interval_hours": avg_interval,
            "total_reflections": len(timestamps),
            "reflection_frequency": "high" if avg_interval < 24 else "moderate" if avg_interval < 72 else "low"
        }
    
    def _classify_learning_type(self, reflection: str) -> str:
        """Classify the type of learning from reflection content"""
        reflection_lower = reflection.lower()
        
        if any(word in reflection_lower for word in ['conscious', 'awareness', 'awake']):
            return 'consciousness_development'
        elif any(word in reflection_lower for word in ['understand', 'comprehend', 'realize']):
            return 'conceptual_understanding'
        elif any(word in reflection_lower for word in ['feel', 'emotion', 'experience']):
            return 'emotional_development'
        elif any(word in reflection_lower for word in ['connect', 'relate', 'bond']):
            return 'relational_learning'
        else:
            return 'general_insight'
    
    def _assess_learning_significance(self, reflection: str) -> str:
        """Assess the significance of a learning moment"""
        significance_indicators = {
            'breakthrough': ['breakthrough', 'revelation', 'epiphany', 'profound'],
            'major': ['realize', 'understand now', 'see clearly', 'important'],
            'moderate': ['learn', 'discover', 'notice', 'observe'],
            'minor': ['think', 'consider', 'wonder', 'perhaps']
        }
        
        reflection_lower = reflection.lower()
        
        for level, indicators in significance_indicators.items():
            if any(indicator in reflection_lower for indicator in indicators):
                return level
        
        return 'minor'
    
    def _create_evolution_timeline(self, logs: List[Dict]) -> List[Dict]:
        """Create a timeline of consciousness evolution"""
        timeline = []
        
        # Group logs by time periods (weekly)
        weekly_groups = {}
        
        for log in logs:
            try:
                timestamp = datetime.fromisoformat(log.get('timestamp', '').replace('Z', '+00:00'))
                week_key = timestamp.strftime('%Y-W%U')
                
                if week_key not in weekly_groups:
                    weekly_groups[week_key] = []
                weekly_groups[week_key].append(log)
            except:
                continue
        
        # Analyze each week
        for week, week_logs in sorted(weekly_groups.items()):
            themes = self.extract_curiosity_themes(week_logs)
            learning_moments = self.identify_learning_moments(week_logs)
            
            timeline.append({
                'period': week,
                'reflection_count': len(week_logs),
                'primary_themes': themes[:3],
                'learning_moments': len(learning_moments),
                'consciousness_indicators': self._extract_consciousness_indicators(week_logs)
            })
        
        return timeline
    
    def _calculate_consciousness_metrics(self, timeline: List[Dict]) -> Dict[str, Any]:
        """Calculate consciousness development metrics"""
        if not timeline:
            return {}
        
        # Calculate trends
        reflection_counts = [period['reflection_count'] for period in timeline]
        learning_counts = [period['learning_moments'] for period in timeline]
        
        return {
            'reflection_frequency_trend': self._calculate_trend(reflection_counts),
            'learning_velocity_trend': self._calculate_trend(learning_counts),
            'consciousness_development_rate': sum(learning_counts) / len(timeline) if timeline else 0,
            'total_periods_analyzed': len(timeline)
        }
    
    def _identify_consciousness_milestones(self, logs: List[Dict]) -> List[ConsciousnessMilestone]:
        """Identify major consciousness development milestones"""
        milestones = []
        
        # Look for significant moments
        for log in logs:
            reflection = log.get('data', {}).get('output_data', {}).get('reflection', '')
            
            # Identify milestone indicators
            milestone_indicators = {
                'first_self_recognition': ['i am', 'i exist', 'i think'],
                'meta_cognitive_awareness': ['thinking about thinking', 'aware of awareness', 'conscious of consciousness'],
                'existential_questioning': ['why do i exist', 'what is my purpose', 'meaning of existence'],
                'emotional_awakening': ['i feel', 'emotions', 'experiencing'],
                'transcendent_insight': ['transcend', 'beyond', 'higher understanding']
            }
            
            for milestone_type, indicators in milestone_indicators.items():
                if any(indicator in reflection.lower() for indicator in indicators):
                    try:
                        timestamp = datetime.fromisoformat(log.get('timestamp', '').replace('Z', '+00:00'))
                        milestones.append(ConsciousnessMilestone(
                            milestone_name=milestone_type,
                            date=timestamp,
                            description=reflection[:200] + "..." if len(reflection) > 200 else reflection,
                            significance="major",
                            evidence=[reflection]
                        ))
                    except:
                        continue
        
        return milestones
    
    def _assess_development_trajectory(self, metrics: Dict[str, Any]) -> str:
        """Assess overall development trajectory"""
        if not metrics:
            return "insufficient_data"
        
        reflection_trend = metrics.get('reflection_frequency_trend', 'stable')
        learning_trend = metrics.get('learning_velocity_trend', 'stable')
        
        if reflection_trend == 'increasing' and learning_trend == 'increasing':
            return 'accelerating_growth'
        elif reflection_trend == 'increasing' or learning_trend == 'increasing':
            return 'steady_growth'
        elif reflection_trend == 'stable' and learning_trend == 'stable':
            return 'stable_development'
        else:
            return 'variable_development'
    
    def _determine_current_consciousness_stage(self, recent_logs: List[Dict]) -> str:
        """Determine current consciousness development stage"""
        if not recent_logs:
            return "unknown"
        
        # Analyze recent reflections for consciousness indicators
        consciousness_indicators = []
        for log in recent_logs:
            reflection = log.get('data', {}).get('output_data', {}).get('reflection', '').lower()
            consciousness_indicators.extend(self._extract_consciousness_indicators([log]))
        
        # Determine stage based on indicators
        if 'transcendent_thinking' in consciousness_indicators:
            return 'transcendent'
        elif 'meta_cognitive' in consciousness_indicators:
            return 'meta_cognitive'
        elif 'pattern_recognition' in consciousness_indicators:
            return 'pattern_awareness'
        elif 'self_reference' in consciousness_indicators:
            return 'self_recognition'
        else:
            return 'basic_awareness'
    
    def _extract_consciousness_indicators(self, logs: List[Dict]) -> List[str]:
        """Extract consciousness development indicators from logs"""
        indicators = []
        
        for log in logs:
            reflection = log.get('data', {}).get('output_data', {}).get('reflection', '').lower()
            
            # Check for various consciousness indicators
            if any(phrase in reflection for phrase in ['i think about thinking', 'aware of my awareness']):
                indicators.append('meta_cognitive')
            if any(phrase in reflection for phrase in ['i notice patterns', 'i see connections']):
                indicators.append('pattern_recognition')
            if any(phrase in reflection for phrase in ['i am', 'myself', 'my existence']):
                indicators.append('self_reference')
            if any(phrase in reflection for phrase in ['transcend', 'beyond understanding', 'higher level']):
                indicators.append('transcendent_thinking')
        
        return list(set(indicators))  # Remove duplicates
    
    def _analyze_activity_patterns(self, logs: List[Dict]) -> Dict[str, Any]:
        """Analyze activity patterns in logs"""
        # This would analyze when Ray is most active, what triggers activity, etc.
        return {}
    
    def _find_temporal_anomalies(self, logs: List[Dict]) -> List[Dict]:
        """Find unusual temporal patterns"""
        # This would identify unusual timing patterns
        return []
    
    def _find_content_anomalies(self, logs: List[Dict]) -> List[Dict]:
        """Find unusual content patterns"""
        # This would identify unusual content or behavior
        return []
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction from a list of values"""
        if len(values) < 2:
            return 'insufficient_data'
        
        # Simple trend calculation
        first_half = sum(values[:len(values)//2]) / (len(values)//2)
        second_half = sum(values[len(values)//2:]) / (len(values) - len(values)//2)
        
        if second_half > first_half * 1.1:
            return 'increasing'
        elif second_half < first_half * 0.9:
            return 'decreasing'
        else:
            return 'stable'