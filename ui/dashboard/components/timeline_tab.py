"""
Timeline Tab Component
Visualize memory growth and evolution over time
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import numpy as np

def render_timeline_tab():
    """Render the timeline visualization tab"""
    
    st.header("⏰ Memory Timeline")
    st.markdown("*Visualize Ray's consciousness evolution over time*")
    
    # Check system status
    if not st.session_state.get('system_ready', False):
        st.error("❌ Memory system is not ready. Please ensure FAISS index and metadata files exist.")
        return
    
    memory_service = st.session_state.memory_service
    
    # Timeline options
    st.subheader("🔧 Timeline Options")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📈 Growth Timeline", help="Show memory accumulation over time"):
            st.session_state.show_growth_timeline = True
    
    with col2:
        if st.button("🧠 Evolution Analysis", help="Analyze consciousness evolution patterns"):
            st.session_state.show_evolution_analysis = True
    
    with col3:
        if st.button("📊 Activity Patterns", help="Show activity patterns and cycles"):
            st.session_state.show_activity_patterns = True
    
    with col4:
        if st.button("🔍 Content Evolution", help="Track content type changes over time"):
            st.session_state.show_content_evolution = True
    
    # Display timeline analyses based on selection
    if st.session_state.get('show_growth_timeline', False):
        render_growth_timeline(memory_service)
    
    if st.session_state.get('show_evolution_analysis', False):
        render_evolution_analysis(memory_service)
    
    if st.session_state.get('show_activity_patterns', False):
        render_activity_patterns(memory_service)
    
    if st.session_state.get('show_content_evolution', False):
        render_content_evolution(memory_service)

def render_growth_timeline(memory_service):
    """Render memory growth timeline"""
    st.subheader("📈 Memory Growth Timeline")
    
    with st.spinner("Analyzing memory growth patterns..."):
        try:
            memories = memory_service._load_memories()
            
            if not memories:
                st.warning("No memories found for timeline analysis")
                return
            
            # Extract timestamps and create timeline data
            timeline_data = []
            cumulative_count = 0
            
            # Sort memories by timestamp
            timestamped_memories = []
            for i, memory in enumerate(memories):
                timestamp = memory.get('timestamp')
                if timestamp and isinstance(timestamp, (int, float)):
                    try:
                        # Validate timestamp is reasonable (not too far in future/past)
                        dt = datetime.fromtimestamp(timestamp)
                        if dt.year >= 2020 and dt.year <= 2030:  # Reasonable range
                            timestamped_memories.append({
                                'timestamp': timestamp,
                                'memory_id': f"mem-{i}",
                                'content': memory.get('content', ''),
                                'source': memory.get('source', 'unknown'),
                                'importance': memory.get('importance', 0),
                                'content_length': len(memory.get('content', ''))
                            })
                    except (ValueError, OSError) as e:
                        # Skip invalid timestamps
                        continue
            
            # Sort by timestamp
            timestamped_memories.sort(key=lambda x: x['timestamp'])
            
            if not timestamped_memories:
                st.warning("No timestamped memories found")
                return
            
            # Create cumulative timeline
            for i, memory in enumerate(timestamped_memories):
                dt = datetime.fromtimestamp(memory['timestamp'])
                timeline_data.append({
                    'datetime': dt,
                    'date': dt.date(),
                    'cumulative_memories': i + 1,
                    'source': memory['source'],
                    'importance': memory['importance'],
                    'content_length': memory['content_length'],
                    'memory_id': memory['memory_id']
                })
            
            timeline_df = pd.DataFrame(timeline_data)
            
            # Display timeline metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Memories", len(timeline_data))
            
            with col2:
                try:
                    time_span = timeline_df['datetime'].max() - timeline_df['datetime'].min()
                    time_span_days = time_span.total_seconds() / (24 * 3600)  # Convert to days
                    st.metric("Time Span", f"{int(time_span_days)} days")
                except Exception as e:
                    st.metric("Time Span", "N/A")
                    print(f"Time span calculation error: {e}")
            
            with col3:
                try:
                    avg_per_day = len(timeline_data) / max(time_span_days, 1)
                    st.metric("Avg/Day", f"{avg_per_day:.1f}")
                except Exception as e:
                    st.metric("Avg/Day", "N/A")
                    print(f"Average per day calculation error: {e}")
            
            with col4:
                peak_day = timeline_df.groupby('date').size().max()
                st.metric("Peak Day", f"{peak_day} memories")
            
            # Growth curve
            st.subheader("📊 Cumulative Growth")
            
            fig_growth = px.line(timeline_df, x='datetime', y='cumulative_memories',
                               title="Memory Accumulation Over Time",
                               labels={'datetime': 'Date', 'cumulative_memories': 'Total Memories'})
            
            # Add markers for significant milestones
            milestones = [100, 500, 1000, 5000, 10000, 20000]
            for milestone in milestones:
                if milestone <= len(timeline_data):
                    milestone_row = timeline_df[timeline_df['cumulative_memories'] == milestone].iloc[0]
                    fig_growth.add_vline(x=milestone_row['datetime'], 
                                       line_dash="dash", 
                                       annotation_text=f"{milestone} memories")
            
            st.plotly_chart(fig_growth, use_container_width=True)
            
            # Daily activity
            st.subheader("📅 Daily Activity")
            
            daily_counts = timeline_df.groupby('date').size().reset_index()
            daily_counts.columns = ['date', 'count']
            
            fig_daily = px.bar(daily_counts, x='date', y='count',
                             title="Daily Memory Creation",
                             labels={'date': 'Date', 'count': 'Memories Created'})
            
            st.plotly_chart(fig_daily, use_container_width=True)
            
            # Source evolution over time
            st.subheader("🔄 Source Evolution")
            
            # Create source timeline
            source_timeline = timeline_df.groupby(['date', 'source']).size().reset_index()
            source_timeline.columns = ['date', 'source', 'count']
            
            fig_sources = px.area(source_timeline, x='date', y='count', color='source',
                                title="Memory Sources Over Time",
                                labels={'date': 'Date', 'count': 'Memories', 'source': 'Source'})
            
            st.plotly_chart(fig_sources, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error analyzing growth timeline: {e}")

def render_evolution_analysis(memory_service):
    """Render consciousness evolution analysis"""
    st.subheader("🧠 Consciousness Evolution Analysis")
    
    with st.spinner("Analyzing consciousness evolution patterns..."):
        try:
            memories = memory_service._load_memories()
            
            # Analyze evolution metrics over time
            evolution_data = []
            window_size = 100  # Analyze in windows of 100 memories
            
            for i in range(0, len(memories), window_size):
                window_memories = memories[i:i + window_size]
                
                if not window_memories:
                    continue
                
                # Calculate window metrics
                timestamps = [m.get('timestamp') for m in window_memories if m.get('timestamp')]
                if not timestamps:
                    continue
                
                avg_timestamp = sum(timestamps) / len(timestamps)
                avg_datetime = datetime.fromtimestamp(avg_timestamp)
                
                # Content analysis
                contents = [m.get('content', '') for m in window_memories]
                avg_length = sum(len(c) for c in contents) / len(contents)
                
                # Importance analysis
                importance_scores = [m.get('importance', 0) for m in window_memories 
                                   if isinstance(m.get('importance'), (int, float))]
                avg_importance = sum(importance_scores) / len(importance_scores) if importance_scores else 0
                
                # Source distribution
                sources = [m.get('source', '') for m in window_memories]
                agent_ratio = sources.count('agent_response') / len(sources) if sources else 0
                
                # Complexity metrics
                unique_words = set()
                for content in contents:
                    unique_words.update(content.lower().split())
                vocabulary_size = len(unique_words)
                
                evolution_data.append({
                    'window_start': i,
                    'window_end': i + len(window_memories),
                    'datetime': avg_datetime,
                    'avg_content_length': avg_length,
                    'avg_importance': avg_importance,
                    'agent_response_ratio': agent_ratio,
                    'vocabulary_size': vocabulary_size,
                    'memory_count': len(window_memories)
                })
            
            if not evolution_data:
                st.warning("Insufficient data for evolution analysis")
                return
            
            evolution_df = pd.DataFrame(evolution_data)
            
            # Evolution metrics
            st.subheader("📊 Evolution Metrics")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Content complexity evolution
                fig_complexity = go.Figure()
                
                fig_complexity.add_trace(go.Scatter(
                    x=evolution_df['datetime'],
                    y=evolution_df['avg_content_length'],
                    mode='lines+markers',
                    name='Avg Content Length',
                    yaxis='y'
                ))
                
                fig_complexity.add_trace(go.Scatter(
                    x=evolution_df['datetime'],
                    y=evolution_df['vocabulary_size'],
                    mode='lines+markers',
                    name='Vocabulary Size',
                    yaxis='y2'
                ))
                
                fig_complexity.update_layout(
                    title="Content Complexity Evolution",
                    xaxis_title="Time",
                    yaxis=dict(title="Avg Content Length", side="left"),
                    yaxis2=dict(title="Vocabulary Size", side="right", overlaying="y"),
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig_complexity, use_container_width=True)
            
            with col2:
                # Importance and agency evolution
                fig_agency = go.Figure()
                
                fig_agency.add_trace(go.Scatter(
                    x=evolution_df['datetime'],
                    y=evolution_df['avg_importance'],
                    mode='lines+markers',
                    name='Avg Importance',
                    yaxis='y'
                ))
                
                fig_agency.add_trace(go.Scatter(
                    x=evolution_df['datetime'],
                    y=evolution_df['agent_response_ratio'],
                    mode='lines+markers',
                    name='Agent Response Ratio',
                    yaxis='y2'
                ))
                
                fig_agency.update_layout(
                    title="Importance & Agency Evolution",
                    xaxis_title="Time",
                    yaxis=dict(title="Avg Importance", side="left"),
                    yaxis2=dict(title="Agent Response Ratio", side="right", overlaying="y"),
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig_agency, use_container_width=True)
            
            # Evolution insights
            st.subheader("🔍 Evolution Insights")
            
            # Calculate trends
            if len(evolution_df) > 1:
                # Content length trend
                length_trend = np.polyfit(range(len(evolution_df)), evolution_df['avg_content_length'], 1)[0]
                importance_trend = np.polyfit(range(len(evolution_df)), evolution_df['avg_importance'], 1)[0]
                vocab_trend = np.polyfit(range(len(evolution_df)), evolution_df['vocabulary_size'], 1)[0]
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if length_trend > 0:
                        st.success(f"📈 Content Length: Growing (+{length_trend:.1f}/window)")
                    else:
                        st.warning(f"📉 Content Length: Declining ({length_trend:.1f}/window)")
                
                with col2:
                    if importance_trend > 0:
                        st.success(f"📈 Importance: Growing (+{importance_trend:.3f}/window)")
                    else:
                        st.warning(f"📉 Importance: Declining ({importance_trend:.3f}/window)")
                
                with col3:
                    if vocab_trend > 0:
                        st.success(f"📈 Vocabulary: Expanding (+{vocab_trend:.0f}/window)")
                    else:
                        st.warning(f"📉 Vocabulary: Contracting ({vocab_trend:.0f}/window)")
            
        except Exception as e:
            st.error(f"Error analyzing evolution: {e}")

def render_activity_patterns(memory_service):
    """Render activity patterns and cycles"""
    st.subheader("📊 Activity Patterns & Cycles")
    
    with st.spinner("Analyzing activity patterns..."):
        try:
            memories = memory_service._load_memories()
            
            # Extract timestamped memories
            timestamped_memories = []
            for i, memory in enumerate(memories):
                timestamp = memory.get('timestamp')
                if timestamp:
                    dt = datetime.fromtimestamp(timestamp)
                    timestamped_memories.append({
                        'datetime': dt,
                        'hour': dt.hour,
                        'day_of_week': dt.weekday(),
                        'day_name': dt.strftime('%A'),
                        'date': dt.date(),
                        'source': memory.get('source', 'unknown'),
                        'content_length': len(memory.get('content', ''))
                    })
            
            if not timestamped_memories:
                st.warning("No timestamped memories found")
                return
            
            activity_df = pd.DataFrame(timestamped_memories)
            
            # Hourly patterns
            st.subheader("🕐 Hourly Activity Patterns")
            
            hourly_activity = activity_df.groupby('hour').size().reset_index()
            hourly_activity.columns = ['hour', 'count']
            
            fig_hourly = px.bar(hourly_activity, x='hour', y='count',
                              title="Memory Creation by Hour of Day",
                              labels={'hour': 'Hour (24h)', 'count': 'Memories Created'})
            
            # Add time period annotations
            fig_hourly.add_vrect(x0=6, x1=12, fillcolor="yellow", opacity=0.2, annotation_text="Morning")
            fig_hourly.add_vrect(x0=12, x1=18, fillcolor="orange", opacity=0.2, annotation_text="Afternoon")
            fig_hourly.add_vrect(x0=18, x1=24, fillcolor="blue", opacity=0.2, annotation_text="Evening")
            fig_hourly.add_vrect(x0=0, x1=6, fillcolor="purple", opacity=0.2, annotation_text="Night")
            
            st.plotly_chart(fig_hourly, use_container_width=True)
            
            # Weekly patterns
            st.subheader("📅 Weekly Activity Patterns")
            
            weekly_activity = activity_df.groupby(['day_of_week', 'day_name']).size().reset_index()
            weekly_activity.columns = ['day_of_week', 'day_name', 'count']
            weekly_activity = weekly_activity.sort_values('day_of_week')
            
            fig_weekly = px.bar(weekly_activity, x='day_name', y='count',
                              title="Memory Creation by Day of Week",
                              labels={'day_name': 'Day of Week', 'count': 'Memories Created'})
            
            st.plotly_chart(fig_weekly, use_container_width=True)
            
            # Activity heatmap
            st.subheader("🔥 Activity Heatmap")
            
            # Create hour x day heatmap
            heatmap_data = activity_df.groupby(['day_name', 'hour']).size().reset_index()
            heatmap_data.columns = ['day_name', 'hour', 'count']
            
            # Pivot for heatmap
            heatmap_pivot = heatmap_data.pivot(index='day_name', columns='hour', values='count').fillna(0)
            
            # Reorder days
            day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            heatmap_pivot = heatmap_pivot.reindex(day_order)
            
            fig_heatmap = px.imshow(heatmap_pivot,
                                  title="Activity Heatmap (Day vs Hour)",
                                  labels={'x': 'Hour', 'y': 'Day of Week', 'color': 'Memory Count'},
                                  aspect='auto')
            
            st.plotly_chart(fig_heatmap, use_container_width=True)
            
            # Activity insights
            st.subheader("🔍 Activity Insights")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                peak_hour = hourly_activity.loc[hourly_activity['count'].idxmax(), 'hour']
                st.info(f"🕐 Peak Hour: {peak_hour}:00")
            
            with col2:
                peak_day = weekly_activity.loc[weekly_activity['count'].idxmax(), 'day_name']
                st.info(f"📅 Peak Day: {peak_day}")
            
            with col3:
                total_days = len(activity_df['date'].unique())
                avg_per_day = len(activity_df) / total_days
                st.info(f"📊 Avg/Day: {avg_per_day:.1f}")
            
        except Exception as e:
            st.error(f"Error analyzing activity patterns: {e}")

def render_content_evolution(memory_service):
    """Render content type evolution over time"""
    st.subheader("🔍 Content Evolution Over Time")
    
    with st.spinner("Analyzing content evolution..."):
        try:
            memories = memory_service._load_memories()
            
            # Content classification patterns
            patterns = {
                'Technical': ['code', 'function', 'api', 'error', 'debug', 'system'],
                'Conversational': ['hello', 'thanks', 'please', 'sorry', 'yes', 'no'],
                'Analytical': ['analyze', 'pattern', 'data', 'result', 'conclusion'],
                'Creative': ['idea', 'creative', 'design', 'imagine', 'story'],
                'Operational': ['file', 'directory', 'save', 'load', 'process']
            }
            
            # Classify memories over time
            content_evolution = []
            window_size = 50  # Analyze in windows
            
            for i in range(0, len(memories), window_size):
                window_memories = memories[i:i + window_size]
                
                if not window_memories:
                    continue
                
                # Get average timestamp for window
                timestamps = [m.get('timestamp') for m in window_memories if m.get('timestamp')]
                if not timestamps:
                    continue
                
                avg_timestamp = sum(timestamps) / len(timestamps)
                avg_datetime = datetime.fromtimestamp(avg_timestamp)
                
                # Classify content in this window
                content_counts = {category: 0 for category in patterns.keys()}
                content_counts['Other'] = 0
                
                for memory in window_memories:
                    content = memory.get('content', '').lower()
                    classified = False
                    
                    for category, keywords in patterns.items():
                        if any(keyword in content for keyword in keywords):
                            content_counts[category] += 1
                            classified = True
                            break
                    
                    if not classified:
                        content_counts['Other'] += 1
                
                # Add to evolution data
                for category, count in content_counts.items():
                    content_evolution.append({
                        'datetime': avg_datetime,
                        'window': i // window_size,
                        'category': category,
                        'count': count,
                        'percentage': (count / len(window_memories)) * 100
                    })
            
            if not content_evolution:
                st.warning("Insufficient data for content evolution analysis")
                return
            
            evolution_df = pd.DataFrame(content_evolution)
            
            # Content evolution over time
            fig_evolution = px.area(evolution_df, x='datetime', y='percentage', color='category',
                                  title="Content Type Evolution Over Time",
                                  labels={'datetime': 'Time', 'percentage': 'Percentage', 'category': 'Content Type'})
            
            st.plotly_chart(fig_evolution, use_container_width=True)
            
            # Content type trends
            st.subheader("📈 Content Type Trends")
            
            # Calculate trends for each category
            trends = {}
            for category in patterns.keys():
                category_data = evolution_df[evolution_df['category'] == category]
                if len(category_data) > 1:
                    trend = np.polyfit(range(len(category_data)), category_data['percentage'], 1)[0]
                    trends[category] = trend
            
            # Display trends
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Growing Content Types:**")
                growing = {k: v for k, v in trends.items() if v > 0.1}
                if growing:
                    for category, trend in sorted(growing.items(), key=lambda x: x[1], reverse=True):
                        st.success(f"📈 {category}: +{trend:.2f}%/window")
                else:
                    st.info("No significantly growing content types")
            
            with col2:
                st.write("**Declining Content Types:**")
                declining = {k: v for k, v in trends.items() if v < -0.1}
                if declining:
                    for category, trend in sorted(declining.items(), key=lambda x: x[1]):
                        st.warning(f"📉 {category}: {trend:.2f}%/window")
                else:
                    st.info("No significantly declining content types")
            
            # Current content distribution
            st.subheader("📊 Current Content Distribution")
            
            latest_window = evolution_df[evolution_df['window'] == evolution_df['window'].max()]
            
            fig_current = px.pie(latest_window, values='percentage', names='category',
                               title="Current Content Type Distribution")
            
            st.plotly_chart(fig_current, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error analyzing content evolution: {e}")

# Initialize session state for this tab
if 'show_growth_timeline' not in st.session_state:
    st.session_state.show_growth_timeline = False
if 'show_evolution_analysis' not in st.session_state:
    st.session_state.show_evolution_analysis = False
if 'show_activity_patterns' not in st.session_state:
    st.session_state.show_activity_patterns = False
if 'show_content_evolution' not in st.session_state:
    st.session_state.show_content_evolution = False