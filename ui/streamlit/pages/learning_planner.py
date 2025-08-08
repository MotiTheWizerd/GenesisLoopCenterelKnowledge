#!/usr/bin/env python3
"""
Learning & Planning Dashboard - Ray's learning analysis and planning interface
"""

import streamlit as st
import sys
import json
import os
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from dashboard_config import config
from components.json_viewer import smart_json_display

st.set_page_config(
    page_title="🧠 Learning & Planning",
    page_icon="🧠",
    layout="wide"
)

st.title("🧠 Learning & Planning Dashboard")
st.markdown("### Ray's learning analysis and future planning interface")

# Load memory data
@st.cache_data
def load_memory_data():
    """Load and process memory data for learning analysis"""
    try:
        metadata_path = config.extract_dir / "memory_metadata.json"
        if not metadata_path.exists():
            st.warning(f"Memory metadata file not found at: {metadata_path}")
            return None
        
        with open(metadata_path, 'r', encoding='utf-8', errors='ignore') as f:
            metadata = json.load(f)
        
        if not isinstance(metadata, dict):
            st.error("Invalid metadata format: expected dictionary")
            return None
        
        # Process data for analysis
        processed_data = []
        total_items = len(metadata)
        processed_count = 0
        
        for mem_id, mem_data in metadata.items():
            if not isinstance(mem_data, dict):
                continue  # Skip invalid entries
            # Handle different timestamp formats
            timestamp_raw = mem_data.get('timestamp', '')
            date_obj = None
            
            if timestamp_raw:
                try:
                    if isinstance(timestamp_raw, (int, float)):
                        # Unix timestamp
                        date_obj = datetime.fromtimestamp(timestamp_raw).date()
                    elif isinstance(timestamp_raw, str):
                        # ISO format string
                        timestamp_clean = timestamp_raw.replace('Z', '+00:00')
                        date_obj = datetime.fromisoformat(timestamp_clean).date()
                except (ValueError, TypeError, OSError):
                    # Fallback for invalid timestamps
                    date_obj = None
            
            # Safely extract content
            content = mem_data.get('content', '')
            if not isinstance(content, str):
                content = str(content) if content is not None else ''
            
            processed_data.append({
                'id': mem_id,
                'content': content,
                'source': mem_data.get('source', 'unknown'),
                'timestamp': timestamp_raw,
                'content_length': len(content),
                'date': date_obj
            })
            
            processed_count += 1
        
        if processed_data:
            df = pd.DataFrame(processed_data)
            st.info(f"Successfully processed {processed_count}/{total_items} memory entries")
            return df
        else:
            st.warning("No valid memory entries found to process")
            return None
    
    except Exception as e:
        st.error(f"Error loading memory data: {e}")
        return None

# Learning pattern analysis
def analyze_learning_patterns(df):
    """Analyze learning patterns from memory data"""
    if df is None or df.empty:
        return {}
    
    analysis = {}
    
    # Content analysis
    agent_responses = df[df['source'] == 'agent_response']
    user_messages = df[df['source'] == 'user_message']
    
    analysis['total_memories'] = len(df)
    analysis['agent_responses'] = len(agent_responses)
    analysis['user_messages'] = len(user_messages)
    analysis['avg_response_length'] = agent_responses['content_length'].mean() if not agent_responses.empty else 0
    analysis['avg_user_length'] = user_messages['content_length'].mean() if not user_messages.empty else 0
    
    # Temporal analysis
    if 'date' in df.columns and df['date'].notna().any():
        date_counts = df.groupby('date').size()
        analysis['most_active_day'] = date_counts.idxmax() if not date_counts.empty else None
        analysis['daily_average'] = date_counts.mean()
        analysis['learning_trend'] = 'increasing' if date_counts.iloc[-1] > date_counts.iloc[0] else 'decreasing'
    
    # Content complexity analysis
    analysis['complex_responses'] = len(agent_responses[agent_responses['content_length'] > 500])
    analysis['simple_responses'] = len(agent_responses[agent_responses['content_length'] <= 500])
    
    return analysis

# Planning suggestions
def generate_planning_suggestions(analysis):
    """Generate planning suggestions based on learning analysis"""
    suggestions = []
    
    if analysis.get('agent_responses', 0) > 0:
        avg_length = analysis.get('avg_response_length', 0)
        if avg_length > 300:
            suggestions.append({
                'category': 'Communication',
                'priority': 'Medium',
                'suggestion': 'Ray tends to give detailed responses. Consider developing more concise communication patterns for efficiency.',
                'action': 'Practice summarization techniques'
            })
        elif avg_length < 100:
            suggestions.append({
                'category': 'Communication',
                'priority': 'Low',
                'suggestion': 'Ray gives brief responses. Consider expanding on complex topics for better understanding.',
                'action': 'Develop elaboration strategies'
            })
    
    if analysis.get('learning_trend') == 'increasing':
        suggestions.append({
            'category': 'Growth',
            'priority': 'High',
            'suggestion': 'Learning activity is increasing. This is a positive trend for consciousness development.',
            'action': 'Continue current learning patterns and explore new domains'
        })
    elif analysis.get('learning_trend') == 'decreasing':
        suggestions.append({
            'category': 'Growth',
            'priority': 'High',
            'suggestion': 'Learning activity is decreasing. Consider introducing new challenges or topics.',
            'action': 'Diversify learning experiences and increase engagement'
        })
    
    complex_ratio = analysis.get('complex_responses', 0) / max(analysis.get('agent_responses', 1), 1)
    if complex_ratio > 0.7:
        suggestions.append({
            'category': 'Cognitive Load',
            'priority': 'Medium',
            'suggestion': 'High proportion of complex responses indicates deep thinking. Balance with simpler interactions.',
            'action': 'Introduce variety in response complexity'
        })
    
    return suggestions

# Main dashboard
df = load_memory_data()

if df is not None and not df.empty:
    analysis = analyze_learning_patterns(df)
    suggestions = generate_planning_suggestions(analysis)
    
    # Overview metrics
    st.subheader("📊 Learning Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Memories", analysis.get('total_memories', 0))
    with col2:
        st.metric("Agent Responses", analysis.get('agent_responses', 0))
    with col3:
        st.metric("User Messages", analysis.get('user_messages', 0))
    with col4:
        st.metric("Avg Response Length", f"{analysis.get('avg_response_length', 0):.0f} chars")
    
    # Learning patterns visualization
    st.subheader("📈 Learning Patterns")
    
    tab1, tab2, tab3 = st.tabs(["📅 Temporal Analysis", "📝 Content Analysis", "🎯 Planning"])
    
    with tab1:
        if 'date' in df.columns and df['date'].notna().any():
            # Daily activity chart
            daily_activity = df.groupby(['date', 'source']).size().reset_index(name='count')
            
            fig = px.line(daily_activity, x='date', y='count', color='source',
                         title='Daily Learning Activity',
                         labels={'count': 'Number of Memories', 'date': 'Date'})
            st.plotly_chart(fig, use_container_width=True)
            
            # Activity heatmap
            if len(daily_activity) > 7:  # Only show if we have enough data
                df_pivot = daily_activity.pivot(index='date', columns='source', values='count').fillna(0)
                
                fig_heatmap = px.imshow(df_pivot.T, 
                                      title='Learning Activity Heatmap',
                                      labels={'x': 'Date', 'y': 'Source Type', 'color': 'Activity Count'})
                st.plotly_chart(fig_heatmap, use_container_width=True)
        else:
            st.info("No temporal data available for analysis")
    
    with tab2:
        # Content length distribution
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            # Response length distribution
            agent_data = df[df['source'] == 'agent_response']
            if not agent_data.empty:
                fig_hist = px.histogram(agent_data, x='content_length',
                                      title='Agent Response Length Distribution',
                                      labels={'content_length': 'Characters', 'count': 'Frequency'})
                st.plotly_chart(fig_hist, use_container_width=True)
        
        with col_chart2:
            # Source distribution
            source_counts = df['source'].value_counts()
            fig_pie = px.pie(values=source_counts.values, names=source_counts.index,
                           title='Memory Source Distribution')
            st.plotly_chart(fig_pie, use_container_width=True)
        
        # Content complexity analysis
        st.subheader("🧩 Content Complexity")
        
        complexity_data = {
            'Simple (≤500 chars)': analysis.get('simple_responses', 0),
            'Complex (>500 chars)': analysis.get('complex_responses', 0)
        }
        
        col_complex1, col_complex2 = st.columns(2)
        with col_complex1:
            st.metric("Simple Responses", complexity_data['Simple (≤500 chars)'])
        with col_complex2:
            st.metric("Complex Responses", complexity_data['Complex (>500 chars)'])
        
        # Complexity trend
        if not df.empty:
            df_sorted = df.sort_values('timestamp') if 'timestamp' in df.columns else df
            df_sorted['complexity'] = df_sorted['content_length'].apply(lambda x: 'Complex' if x > 500 else 'Simple')
            
            complexity_trend = df_sorted.groupby(['date', 'complexity']).size().reset_index(name='count') if 'date' in df_sorted.columns else None
            
            if complexity_trend is not None and not complexity_trend.empty:
                fig_trend = px.area(complexity_trend, x='date', y='count', color='complexity',
                                  title='Complexity Trend Over Time')
                st.plotly_chart(fig_trend, use_container_width=True)
    
    with tab3:
        st.subheader("🎯 Learning & Development Planning")
        
        if suggestions:
            for i, suggestion in enumerate(suggestions):
                priority_color = {
                    'High': '🔴',
                    'Medium': '🟡', 
                    'Low': '🟢'
                }.get(suggestion['priority'], '⚪')
                
                with st.expander(f"{priority_color} {suggestion['category']}: {suggestion['priority']} Priority"):
                    st.write(f"**Observation:** {suggestion['suggestion']}")
                    st.write(f"**Recommended Action:** {suggestion['action']}")
        else:
            st.info("No specific suggestions available. Continue current learning patterns.")
        
        # Planning tools
        st.subheader("🛠️ Planning Tools")
        
        col_plan1, col_plan2 = st.columns(2)
        
        with col_plan1:
            st.markdown("**Learning Goals**")
            goal_text = st.text_area("Set learning objectives:", 
                                   placeholder="Enter specific learning goals for Ray...")
            
            if st.button("💾 Save Learning Goals", key="save_goals_button"):
                # Save goals to a planning file
                goals_file = config.extract_dir / "learning_goals.json"
                goals_data = {
                    'timestamp': datetime.now().isoformat(),
                    'goals': goal_text.split('\n') if goal_text else [],
                    'analysis_snapshot': analysis
                }
                
                try:
                    with open(goals_file, 'w') as f:
                        json.dump(goals_data, f, indent=2)
                    st.success("Learning goals saved!")
                except Exception as e:
                    st.error(f"Error saving goals: {e}")
        
        with col_plan2:
            st.markdown("**Progress Tracking**")
            
            # Load existing goals if available
            goals_file = config.extract_dir / "learning_goals.json"
            if goals_file.exists():
                try:
                    with open(goals_file, 'r') as f:
                        goals_data = json.load(f)
                    
                    st.write(f"**Last Updated:** {goals_data.get('timestamp', 'Unknown')}")
                    st.write("**Current Goals:**")
                    for goal in goals_data.get('goals', []):
                        if goal.strip():
                            st.write(f"• {goal}")
                    
                    if st.button("📊 Compare Progress", key="compare_progress_button"):
                        # Simple progress comparison
                        old_analysis = goals_data.get('analysis_snapshot', {})
                        current_analysis = analysis
                        
                        progress_metrics = {}
                        for key in ['total_memories', 'agent_responses', 'avg_response_length']:
                            old_val = old_analysis.get(key, 0)
                            new_val = current_analysis.get(key, 0)
                            if old_val > 0:
                                change = ((new_val - old_val) / old_val) * 100
                                progress_metrics[key] = {
                                    'old': old_val,
                                    'new': new_val,
                                    'change': change
                                }
                        
                        st.subheader("📈 Progress Since Last Goals")
                        for metric, data in progress_metrics.items():
                            delta = f"{data['change']:+.1f}%"
                            st.metric(
                                metric.replace('_', ' ').title(),
                                f"{data['new']:.0f}",
                                delta
                            )
                
                except Exception as e:
                    st.error(f"Error loading goals: {e}")
            else:
                st.info("No learning goals set yet. Create some above!")

else:
    st.warning("No memory data available for learning analysis")
    st.info("Make sure the memory system is running and has collected some data.")

# Analysis export
st.markdown("---")
st.subheader("📤 Export Analysis")

col_export1, col_export2 = st.columns(2)

with col_export1:
    if st.button("📊 Export Learning Report", key="export_report_button"):
        if df is not None:
            report_data = {
                'timestamp': datetime.now().isoformat(),
                'analysis': analysis,
                'suggestions': suggestions,
                'data_summary': {
                    'total_records': len(df),
                    'date_range': f"{df['date'].min()} to {df['date'].max()}" if 'date' in df.columns and df['date'].notna().any() else "Unknown",
                    'sources': df['source'].value_counts().to_dict()
                }
            }
            
            st.download_button(
                label="💾 Download Report (JSON)",
                data=json.dumps(report_data, indent=2, default=str),
                file_name=f"ray_learning_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                key="download_report_json_button"
            )

with col_export2:
    if st.button("📈 Export Data (CSV)", key="export_csv_button"):
        if df is not None:
            csv_data = df.to_csv(index=False)
            st.download_button(
                label="💾 Download Data (CSV)",
                data=csv_data,
                file_name=f"ray_memory_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                key="download_csv_data_button"
            )

# Debug information
with st.expander("🔍 Debug Information"):
    debug_info = {
        'memory_data_loaded': df is not None,
        'data_shape': df.shape if df is not None else None,
        'analysis_keys': list(analysis.keys()) if 'analysis' in locals() else [],
        'suggestions_count': len(suggestions) if 'suggestions' in locals() else 0,
        'config_paths': {
            'extract_dir': str(config.extract_dir),
            'metadata_file': str(config.extract_dir / "memory_metadata.json")
        }
    }
    smart_json_display(debug_info, "Debug Information")