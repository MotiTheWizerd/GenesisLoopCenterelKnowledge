"""
Memory Analysis Tab Component
Deep analysis of Ray's memory structure and patterns
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from collections import Counter, defaultdict

def render_memory_analysis_tab():
    """Render the memory analysis tab"""
    
    st.header("🧠 Memory Structure Analysis")
    st.markdown("*Deep dive into Ray's memory patterns and consciousness structure*")
    
    # Check system status
    if not st.session_state.get('system_ready', False):
        st.error("❌ Memory system is not ready. Please ensure FAISS index and metadata files exist.")
        st.info("Run the embedding creation scripts first to enable memory analysis.")
        return
    
    memory_service = st.session_state.memory_service
    
    # Analysis options
    st.subheader("🔍 Analysis Options")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📋 Schema Analysis", help="Analyze memory field structure"):
            st.session_state.show_schema = True
    
    with col2:
        if st.button("📈 Pattern Analysis", help="Analyze memory patterns and trends"):
            st.session_state.show_patterns = True
    
    with col3:
        if st.button("🏥 Quality Analysis", help="Analyze memory data quality"):
            st.session_state.show_quality = True
    
    with col4:
        if st.button("📉 Value Analysis", help="Analyze memory value composition and importance"):
            st.session_state.show_value = True
    
    # Specific memory analysis
    st.subheader("🎯 Specific Memory Analysis")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        memory_id = st.text_input("Memory ID to analyze:", value="mem-6", help="Enter memory ID (e.g., mem-6)")
    with col2:
        if st.button("🔍 Analyze"):
            st.session_state.analyze_memory_id = memory_id
    
    # Display analyses based on user selection
    if st.session_state.get('show_schema', False):
        render_schema_analysis(memory_service)
    
    if st.session_state.get('show_patterns', False):
        render_pattern_analysis(memory_service)
    
    if st.session_state.get('show_quality', False):
        render_quality_analysis(memory_service)
    
    if st.session_state.get('show_value', False):
        render_value_analysis(memory_service)
    
    if st.session_state.get('analyze_memory_id'):
        render_specific_memory_analysis(memory_service, st.session_state.analyze_memory_id)

def render_schema_analysis(memory_service):
    """Render memory schema analysis"""
    st.subheader("📋 Memory Schema Analysis")
    
    with st.spinner("Analyzing memory schema..."):
        try:
            memories = memory_service._load_memories()
            sample_size = min(1000, len(memories))
            sample_memories = memories[:sample_size]
            
            # Analyze field presence and types
            field_stats = defaultdict(int)
            field_types = defaultdict(set)
            field_examples = defaultdict(list)
            
            for i, memory in enumerate(sample_memories):
                for field, value in memory.items():
                    field_stats[field] += 1
                    field_types[field].add(type(value).__name__)
                    
                    # Collect examples
                    if len(field_examples[field]) < 3:
                        if value not in [ex['value'] for ex in field_examples[field]]:
                            field_examples[field].append({
                                'value': str(value)[:100] + "..." if len(str(value)) > 100 else str(value),
                                'memory_id': f"mem-{i}"
                            })
            
            # Create schema dataframe
            schema_data = []
            for field in sorted(field_stats.keys()):
                presence_pct = (field_stats[field] / sample_size) * 100
                types = ', '.join(field_types[field])
                examples = ' | '.join([ex['value'] for ex in field_examples[field][:2]])
                
                schema_data.append({
                    'Field': str(field),
                    'Presence': f"{field_stats[field]}/{sample_size} ({presence_pct:.1f}%)",
                    'Types': str(types),
                    'Examples': str(examples)
                })
            
            schema_df = pd.DataFrame(schema_data)
            
            st.info(f"📊 Schema analysis based on {sample_size} memory entries")
            st.dataframe(schema_df, use_container_width=True)
            
            # Field presence chart
            if len(schema_data) > 0:
                try:
                    presence_data = []
                    for item in schema_data:
                        field = item['Field']
                        presence = field_stats[field] / sample_size * 100
                        presence_data.append({'Field': field, 'Presence %': presence})
                    
                    presence_df = pd.DataFrame(presence_data)
                    fig = px.bar(presence_df, x='Field', y='Presence %', 
                               title="Field Presence Across Memory Entries")
                    fig.update_layout(xaxis_tickangle=45)
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as chart_error:
                    st.warning(f"Chart display error: {chart_error}")
                    st.write("Field presence data available in table above.")
            
        except Exception as e:
            st.error(f"Error analyzing schema: {e}")

def render_pattern_analysis(memory_service):
    """Render memory pattern analysis"""
    st.subheader("📈 Memory Pattern Analysis")
    
    with st.spinner("Analyzing memory patterns..."):
        try:
            memories = memory_service._load_memories()
            
            # Enhanced analysis
            sources = Counter()
            content_lengths = []
            timestamps = []
            importance_scores = []
            tag_counts = Counter()
            content_types = Counter()
            
            # Content type classification patterns
            filename_patterns = ['\.md', '\.json', '\.py', '\.txt', '\.csv', 'directory', 'file', 'shared Google Drive']
            agent_patterns = ['Sound good', 'Got it', 'Yep', 'Yes', 'No', 'Okay', 'Sure', 'I understand']
            data_patterns = ['copy and paste', 'content', 'data', 'processing', 'reference', 'api']
            
            for i, memory in enumerate(memories):
                # Source analysis
                source = memory.get('source', 'unknown')
                sources[source] += 1
                
                # Content analysis
                content = memory.get('content', '')
                content_str = str(content).lower()
                content_lengths.append(len(str(content)))
                
                # Content type classification
                if any(pattern in content_str for pattern in filename_patterns):
                    content_types['filename/data-processing'] += 1
                elif any(pattern in content_str for pattern in agent_patterns):
                    content_types['agent_reply/system_task'] += 1
                elif any(pattern in content_str for pattern in data_patterns):
                    content_types['data_reference'] += 1
                elif len(content_str) < 50:
                    content_types['short_response'] += 1
                else:
                    content_types['other'] += 1
                
                # Timestamps
                timestamp = memory.get('timestamp')
                if timestamp:
                    timestamps.append(timestamp)
                
                # Importance
                importance = memory.get('importance')
                if isinstance(importance, (int, float)):
                    importance_scores.append(importance)
                
                # Tags
                tags = memory.get('tags', [])
                if isinstance(tags, list):
                    for tag in tags:
                        tag_counts[tag] += 1
            
            # Enhanced statistics display
            st.subheader("📊 Statistics Across All Entries")
            
            # Overview metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Entries", f"{len(memories):,}")
            with col2:
                avg_length = sum(content_lengths) / len(content_lengths) if content_lengths else 0
                st.metric("Avg Length", f"{avg_length:.0f} chars")
            with col3:
                short_entries = sum(1 for length in content_lengths if length < 50)
                st.metric("Short Entries", f"{short_entries}")
            with col4:
                long_entries = sum(1 for length in content_lengths if length > 300)
                st.metric("Long Entries", f"{long_entries}")
            
            # Content type analysis (like your analysis)
            st.subheader("🏷️ Entry Content Types (Inferred)")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Content type breakdown
                content_type_data = []
                for content_type, count in content_types.most_common():
                    pct = (count / len(memories)) * 100
                    content_type_data.append({
                        'Content Type': str(content_type.replace('_', ' ').title()),
                        'Count': str(count),
                        'Percentage': f"{pct:.1f}%"
                    })
                
                content_type_df = pd.DataFrame(content_type_data)
                st.dataframe(content_type_df, use_container_width=True)
                
                # Highlight key findings
                filename_count = content_types.get('filename/data-processing', 0)
                agent_count = content_types.get('agent_reply/system_task', 0)
                
                st.info(f"📁 {filename_count}/{len(memories)} contain filename or data-processing references")
                st.info(f"🤖 {agent_count}/{len(memories)} are agent replies or system tasks")
            
            with col2:
                st.subheader("🔸 Source Distribution")
                source_data = []
                for source, count in sources.most_common():
                    pct = (count / len(memories)) * 100
                    source_data.append({
                        'Source': str(source), 
                        'Count': str(count), 
                        'Percentage': f"{pct:.1f}%"
                    })
                
                source_df = pd.DataFrame(source_data)
                st.dataframe(source_df, use_container_width=True)
                
                # Pie chart
                try:
                    # Convert Count back to numeric for pie chart
                    source_df_numeric = source_df.copy()
                    source_df_numeric['Count'] = source_df_numeric['Count'].astype(int)
                    
                    fig_pie = px.pie(source_df_numeric, values='Count', names='Source', 
                                   title="Memory Sources Distribution")
                    st.plotly_chart(fig_pie, use_container_width=True)
                except Exception as chart_error:
                    st.warning(f"Pie chart display error: {chart_error}")
                    st.write("Source distribution data available in table above.")
            
            # Length distribution analysis
            st.subheader("� Conteont Length Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if content_lengths:
                    # Length categories
                    very_short = sum(1 for l in content_lengths if l < 30)
                    short = sum(1 for l in content_lengths if 30 <= l < 100)
                    medium = sum(1 for l in content_lengths if 100 <= l < 400)
                    long = sum(1 for l in content_lengths if l >= 400)
                    
                    length_categories = pd.DataFrame([
                        {'Category': 'Very Short (< 30 chars)', 'Count': str(very_short), 'Example': 'yep first'},
                        {'Category': 'Short (30-100 chars)', 'Count': str(short), 'Example': 'Sound good?'},
                        {'Category': 'Medium (100-400 chars)', 'Count': str(medium), 'Example': 'Agent responses'},
                        {'Category': 'Long (400+ chars)', 'Count': str(long), 'Example': 'Detailed content'}
                    ])
                    
                    st.dataframe(length_categories, use_container_width=True)
                    
                    # Key insights
                    if medium > 0:
                        avg_medium = sum(l for l in content_lengths if 100 <= l < 400) / medium
                        st.success(f"📊 Medium entries average: ~{avg_medium:.0f} chars (like Memory 7)")
                    
                    if very_short > 0:
                        st.info(f"⚡ {very_short} very short entries (like 'yep first')")
            
            with col2:
                if content_lengths:
                    length_stats = {
                        'Min': min(content_lengths),
                        'Max': max(content_lengths),
                        'Average': sum(content_lengths) / len(content_lengths),
                        'Median': sorted(content_lengths)[len(content_lengths)//2]
                    }
                    
                    stats_df = pd.DataFrame([
                        {'Metric': str(k), 'Value': f"{v:.0f} chars"} 
                        for k, v in length_stats.items()
                    ])
                    st.dataframe(stats_df, use_container_width=True)
                    
                    # Histogram
                    try:
                        fig_hist = px.histogram(x=content_lengths, nbins=30,
                                              title="Content Length Distribution",
                                              labels={'x': 'Content Length (chars)', 'y': 'Frequency'})
                        st.plotly_chart(fig_hist, use_container_width=True)
                    except Exception as chart_error:
                        st.warning(f"Histogram display error: {chart_error}")
                        st.write("Content length statistics available in table above.")
            
            # Timeline analysis
            if timestamps:
                st.subheader("🔸 Timeline Analysis")
                timestamps.sort()
                earliest = datetime.fromtimestamp(timestamps[0])
                latest = datetime.fromtimestamp(timestamps[-1])
                span = latest - earliest
                
                timeline_info = {
                    'Earliest Memory': earliest.strftime('%Y-%m-%d %H:%M:%S'),
                    'Latest Memory': latest.strftime('%Y-%m-%d %H:%M:%S'),
                    'Time Span': str(span),
                    'Total Entries': len(timestamps)
                }
                
                timeline_df = pd.DataFrame([
                    {'Metric': k, 'Value': v} for k, v in timeline_info.items()
                ])
                st.dataframe(timeline_df, use_container_width=True)
            
            # Content examples section
            st.subheader("📝 Content Examples by Type")
            
            # Find examples of each content type
            examples = {
                'filename/data-processing': [],
                'agent_reply/system_task': [],
                'short_response': [],
                'other': []
            }
            
            for i, memory in enumerate(memories[:50]):  # Sample first 50
                content = str(memory.get('content', ''))
                content_lower = content.lower()
                
                # Classify and collect examples
                if any(pattern in content_lower for pattern in filename_patterns):
                    if len(examples['filename/data-processing']) < 3:
                        examples['filename/data-processing'].append({
                            'id': f"mem-{i}",
                            'content': content[:100] + "..." if len(content) > 100 else content
                        })
                elif any(pattern in content_lower for pattern in agent_patterns):
                    if len(examples['agent_reply/system_task']) < 3:
                        examples['agent_reply/system_task'].append({
                            'id': f"mem-{i}",
                            'content': content[:100] + "..." if len(content) > 100 else content
                        })
                elif len(content) < 50:
                    if len(examples['short_response']) < 3:
                        examples['short_response'].append({
                            'id': f"mem-{i}",
                            'content': content
                        })
                else:
                    if len(examples['other']) < 3:
                        examples['other'].append({
                            'id': f"mem-{i}",
                            'content': content[:100] + "..." if len(content) > 100 else content
                        })
            
            # Display examples
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**📁 Filename/Data-Processing Examples:**")
                for ex in examples['filename/data-processing']:
                    st.code(f"{ex['id']}: {ex['content']}")
                
                st.write("**⚡ Short Response Examples:**")
                for ex in examples['short_response']:
                    st.code(f"{ex['id']}: {ex['content']}")
            
            with col2:
                st.write("**🤖 Agent Reply/System Task Examples:**")
                for ex in examples['agent_reply/system_task']:
                    st.code(f"{ex['id']}: {ex['content']}")
                
                st.write("**📄 Other Content Examples:**")
                for ex in examples['other']:
                    st.code(f"{ex['id']}: {ex['content']}")
            
            # Top tags
            if tag_counts:
                st.subheader("🔸 Top Tags")
                tag_data = []
                for tag, count in tag_counts.most_common(10):
                    pct = (count / len(memories)) * 100
                    tag_data.append({
                        'Tag': str(tag), 
                        'Count': str(count), 
                        'Percentage': f"{pct:.1f}%"
                    })
                
                tag_df = pd.DataFrame(tag_data)
                st.dataframe(tag_df, use_container_width=True)
            
            # Importance distribution
            if importance_scores:
                st.subheader("🔸 Importance Distribution")
                try:
                    fig_importance = px.histogram(x=importance_scores, nbins=20,
                                                title="Importance Score Distribution",
                                                labels={'x': 'Importance Score', 'y': 'Frequency'})
                    st.plotly_chart(fig_importance, use_container_width=True)
                except Exception as chart_error:
                    st.warning(f"Importance chart display error: {chart_error}")
                    st.write(f"Importance scores available: {len(importance_scores)} entries")
            
        except Exception as e:
            st.error(f"Error analyzing patterns: {e}")

def render_quality_analysis(memory_service):
    """Render memory quality analysis"""
    st.subheader("🏥 Memory Quality Analysis")
    
    with st.spinner("Analyzing memory quality..."):
        try:
            memories = memory_service._load_memories()
            
            # Quality metrics
            complete_memories = 0
            missing_fields = defaultdict(int)
            empty_fields = defaultdict(int)
            
            required_fields = ['content', 'source', 'timestamp']
            optional_fields = ['tags', 'importance', 'type']
            
            for memory in memories:
                is_complete = True
                
                # Check required fields
                for field in required_fields:
                    if field not in memory:
                        missing_fields[field] += 1
                        is_complete = False
                    elif not memory[field]:
                        empty_fields[field] += 1
                        is_complete = False
                
                # Check optional fields
                for field in optional_fields:
                    if field not in memory:
                        missing_fields[field] += 1
                    elif not memory[field]:
                        empty_fields[field] += 1
                
                if is_complete:
                    complete_memories += 1
            
            # Display quality metrics
            completeness_pct = (complete_memories / len(memories)) * 100
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Complete Memories", 
                         f"{complete_memories:,}", 
                         f"{completeness_pct:.1f}%")
            
            with col2:
                st.metric("Total Memories", f"{len(memories):,}")
            
            with col3:
                if completeness_pct >= 95:
                    st.success(f"Quality: EXCELLENT")
                elif completeness_pct >= 80:
                    st.warning(f"Quality: GOOD")
                else:
                    st.error(f"Quality: NEEDS IMPROVEMENT")
            
            # Missing fields analysis
            if missing_fields:
                st.subheader("🔸 Missing Fields")
                missing_data = []
                for field, count in missing_fields.most_common():
                    pct = (count / len(memories)) * 100
                    missing_data.append({
                        'Field': str(field),
                        'Missing Count': str(count),
                        'Missing %': f"{pct:.1f}%"
                    })
                
                missing_df = pd.DataFrame(missing_data)
                st.dataframe(missing_df, use_container_width=True)
            
            # Empty fields analysis
            if empty_fields:
                st.subheader("🔸 Empty Fields")
                empty_data = []
                for field, count in empty_fields.most_common():
                    pct = (count / len(memories)) * 100
                    empty_data.append({
                        'Field': str(field),
                        'Empty Count': str(count),
                        'Empty %': f"{pct:.1f}%"
                    })
                
                empty_df = pd.DataFrame(empty_data)
                st.dataframe(empty_df, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error analyzing quality: {e}")

def render_value_analysis(memory_service):
    """Render memory value composition analysis"""
    st.subheader("📉 Memory Value Composition Analysis")
    st.markdown("*Strategic assessment of memory importance and redundancy*")
    
    with st.spinner("Analyzing memory value composition..."):
        try:
            memories = memory_service._load_memories()
            
            # Value classification patterns
            low_importance_patterns = [
                'sound good', 'got it', 'yep', 'yes', 'no', 'okay', 'sure', 
                'i understand', 'thanks', 'thank you', 'alright', 'perfect',
                'filename', 'directory', 'file', '.md', '.json', '.py', '.txt'
            ]
            
            mid_importance_patterns = [
                'guidance', 'summary', 'scaffolding', 'analysis', 'review',
                'explanation', 'breakdown', 'structure', 'organize', 'plan'
            ]
            
            high_value_patterns = [
                'strategic', 'insight', 'reflection', 'system-changing', 'breakthrough',
                'discovery', 'innovation', 'paradigm', 'fundamental', 'core principle'
            ]
            
            # Redundancy detection patterns
            redundancy_patterns = [
                'directory-api-json-reference', 'shared google drive', 'copy and paste',
                'content', 'data', 'processing'
            ]
            
            # Analyze each memory
            value_categories = {
                'low_importance': [],
                'mid_importance': [],
                'high_value': [],
                'redundant': []
            }
            
            content_frequency = Counter()
            
            for i, memory in enumerate(memories):
                content = str(memory.get('content', '')).lower()
                memory_info = {
                    'id': f"mem-{i}",
                    'content': memory.get('content', ''),
                    'length': len(content),
                    'importance': memory.get('importance', 0)
                }
                
                # Track content frequency for redundancy detection
                content_key = content[:50]  # First 50 chars as key
                content_frequency[content_key] += 1
                
                # Classify by value
                if any(pattern in content for pattern in high_value_patterns):
                    value_categories['high_value'].append(memory_info)
                elif any(pattern in content for pattern in mid_importance_patterns):
                    value_categories['mid_importance'].append(memory_info)
                elif any(pattern in content for pattern in low_importance_patterns) or len(content) < 50:
                    value_categories['low_importance'].append(memory_info)
                else:
                    # Default classification based on length and importance
                    importance = memory.get('importance', 0)
                    if isinstance(importance, (int, float)):
                        if importance >= 0.8:
                            value_categories['high_value'].append(memory_info)
                        elif importance >= 0.5:
                            value_categories['mid_importance'].append(memory_info)
                        else:
                            value_categories['low_importance'].append(memory_info)
                    else:
                        value_categories['low_importance'].append(memory_info)
                
                # Check for redundancy
                if any(pattern in content for pattern in redundancy_patterns):
                    value_categories['redundant'].append(memory_info)
            
            # Calculate percentages
            total_memories = len(memories)
            value_composition = {
                'Low-importance ops': {
                    'count': len(value_categories['low_importance']),
                    'percentage': (len(value_categories['low_importance']) / total_memories) * 100,
                    'notes': 'Setup, file-name echoing, confirmations'
                },
                'Mid-importance ops': {
                    'count': len(value_categories['mid_importance']),
                    'percentage': (len(value_categories['mid_importance']) / total_memories) * 100,
                    'notes': 'Guidance, summary scaffolding, analysis'
                },
                'High-value insight': {
                    'count': len(value_categories['high_value']),
                    'percentage': (len(value_categories['high_value']) / total_memories) * 100,
                    'notes': 'Strategic, reflective, system-changing memory'
                }
            }
            
            # Redundancy analysis
            redundant_count = sum(1 for count in content_frequency.values() if count > 1)
            redundancy_percentage = (redundant_count / total_memories) * 100
            
            # Display meta-analysis table
            st.subheader("📊 Meta-Analysis: Memory Value Composition")
            
            composition_data = []
            for category, data in value_composition.items():
                composition_data.append({
                    'Category': str(category),
                    'Count': str(data['count']),
                    'Percentage': f"{data['percentage']:.0f}%",
                    'Notes': str(data['notes'])
                })
            
            # Add redundancy row
            composition_data.append({
                'Category': 'Redundancy signals',
                'Count': str(redundant_count),
                'Percentage': f"{redundancy_percentage:.0f}%",
                'Notes': 'Repeated content patterns across entries'
            })
            
            composition_df = pd.DataFrame(composition_data)
            st.dataframe(composition_df, use_container_width=True)
            
            # Visual breakdown
            col1, col2 = st.columns(2)
            
            with col1:
                # Value composition pie chart
                try:
                    fig_value = px.pie(
                        values=[data['count'] for data in value_composition.values()],
                        names=list(value_composition.keys()),
                        title="Memory Value Distribution",
                        color_discrete_map={
                            'Low-importance ops': '#ff7f7f',
                            'Mid-importance ops': '#ffbf7f', 
                            'High-value insight': '#7fff7f'
                        }
                    )
                    st.plotly_chart(fig_value, use_container_width=True)
                except Exception as chart_error:
                    st.warning(f"Value chart display error: {chart_error}")
                    st.write("Value composition data available in table above.")
            
            with col2:
                # Key insights
                st.subheader("🔍 Key Insights")
                
                low_pct = value_composition['Low-importance ops']['percentage']
                high_pct = value_composition['High-value insight']['percentage']
                
                if low_pct > 60:
                    st.warning(f"⚠️ {low_pct:.0f}% low-importance operations detected")
                
                if high_pct == 0:
                    st.error("❌ No high-value insights found in current memory set")
                elif high_pct < 10:
                    st.warning(f"⚠️ Only {high_pct:.0f}% high-value insights")
                else:
                    st.success(f"✅ {high_pct:.0f}% high-value insights detected")
                
                if redundancy_percentage > 25:
                    st.warning(f"🔄 {redundancy_percentage:.0f}% redundancy detected")
                
                # Memory efficiency score
                efficiency_score = (high_pct * 3 + value_composition['Mid-importance ops']['percentage'] * 1.5) / 4.5 * 100
                
                if efficiency_score >= 70:
                    st.success(f"📈 Memory Efficiency: EXCELLENT ({efficiency_score:.0f}%)")
                elif efficiency_score >= 50:
                    st.info(f"📊 Memory Efficiency: GOOD ({efficiency_score:.0f}%)")
                else:
                    st.error(f"📉 Memory Efficiency: NEEDS IMPROVEMENT ({efficiency_score:.0f}%)")
            
            # Detailed breakdowns
            st.subheader("📋 Category Breakdowns")
            
            tab1, tab2, tab3, tab4 = st.tabs(["Low-Importance", "Mid-Importance", "High-Value", "Redundant"])
            
            with tab1:
                st.write(f"**{len(value_categories['low_importance'])} Low-Importance Operations:**")
                for mem in value_categories['low_importance'][:10]:  # Show first 10
                    preview = mem['content'][:100] + "..." if len(mem['content']) > 100 else mem['content']
                    st.text(f"{mem['id']}: {preview}")
            
            with tab2:
                st.write(f"**{len(value_categories['mid_importance'])} Mid-Importance Operations:**")
                for mem in value_categories['mid_importance'][:10]:
                    preview = mem['content'][:100] + "..." if len(mem['content']) > 100 else mem['content']
                    st.text(f"{mem['id']}: {preview}")
            
            with tab3:
                st.write(f"**{len(value_categories['high_value'])} High-Value Insights:**")
                if value_categories['high_value']:
                    for mem in value_categories['high_value']:
                        preview = mem['content'][:200] + "..." if len(mem['content']) > 200 else mem['content']
                        st.success(f"{mem['id']}: {preview}")
                else:
                    st.info("No high-value insights detected. Consider:")
                    st.write("- Adding strategic reflections")
                    st.write("- Capturing system-changing decisions")
                    st.write("- Recording breakthrough moments")
            
            with tab4:
                st.write(f"**Redundancy Analysis:**")
                redundant_patterns = [content for content, count in content_frequency.most_common(10) if count > 1]
                for i, pattern in enumerate(redundant_patterns):
                    count = content_frequency[pattern]
                    st.text(f"Pattern {i+1} (appears {count}x): {pattern}...")
            
            # Recommendations
            st.subheader("💡 Optimization Recommendations")
            
            if low_pct > 60:
                st.write("🔧 **Reduce Low-Importance Operations:**")
                st.write("- Filter out simple confirmations and file echoing")
                st.write("- Batch similar setup operations")
                st.write("- Focus on capturing decision points instead of acknowledgments")
            
            if high_pct < 10:
                st.write("📈 **Increase High-Value Capture:**")
                st.write("- Record strategic insights and breakthroughs")
                st.write("- Capture system-changing decisions")
                st.write("- Document learning moments and reflections")
            
            if redundancy_percentage > 25:
                st.write("🔄 **Address Redundancy:**")
                st.write("- Implement deduplication for similar content")
                st.write("- Consolidate repeated filename references")
                st.write("- Create summary entries instead of multiple similar ones")
            
        except Exception as e:
            st.error(f"Error analyzing memory value: {e}")

def render_specific_memory_analysis(memory_service, memory_id):
    """Render analysis of a specific memory"""
    st.subheader(f"🎯 Specific Memory Analysis: {memory_id}")
    
    try:
        # Get memory from metadata
        metadata = memory_service._load_metadata()
        memory = metadata.get(memory_id)
        
        if not memory:
            # Try to find in raw memories
            try:
                idx = int(memory_id.replace('mem-', ''))
                memories = memory_service._load_memories()
                if idx < len(memories):
                    memory = memories[idx]
                    st.info(f"Found memory at index {idx} in raw data")
            except:
                pass
        
        if not memory:
            st.error(f"Memory {memory_id} not found")
            return
        
        # Display memory details
        st.success(f"✅ Memory {memory_id} found")
        
        # Create detailed analysis
        analysis_data = []
        
        for field, value in memory.items():
            field_info = {'Field': field, 'Type': type(value).__name__}
            
            if field == 'content':
                field_info['Details'] = f"Length: {len(str(value))} chars, Words: {len(str(value).split())}"
                field_info['Preview'] = str(value)[:200] + "..." if len(str(value)) > 200 else str(value)
            
            elif field == 'timestamp':
                if isinstance(value, (int, float)):
                    dt = datetime.fromtimestamp(value)
                    field_info['Details'] = f"Human: {dt.strftime('%Y-%m-%d %H:%M:%S')}"
                    field_info['Preview'] = f"Raw: {value}"
                else:
                    field_info['Details'] = "Non-numeric timestamp"
                    field_info['Preview'] = str(value)
            
            elif field == 'tags':
                if isinstance(value, list):
                    field_info['Details'] = f"Count: {len(value)}"
                    field_info['Preview'] = ', '.join(map(str, value))
                else:
                    field_info['Details'] = "Non-list tags"
                    field_info['Preview'] = str(value)
            
            elif field == 'importance':
                field_info['Details'] = f"Value: {value}"
                if isinstance(value, (int, float)):
                    if value >= 0.8:
                        field_info['Preview'] = "HIGH 🔥"
                    elif value >= 0.5:
                        field_info['Preview'] = "MEDIUM 📊"
                    else:
                        field_info['Preview'] = "LOW 📝"
                else:
                    field_info['Preview'] = str(value)
            
            else:
                field_info['Details'] = f"Length: {len(str(value))}"
                field_info['Preview'] = str(value)[:100] + "..." if len(str(value)) > 100 else str(value)
            
            analysis_data.append(field_info)
        
        # Display as dataframe
        analysis_df = pd.DataFrame(analysis_data)
        st.dataframe(analysis_df, use_container_width=True)
        
        # Show full content if it exists
        if 'content' in memory:
            st.subheader("📄 Full Content")
            st.text_area("Memory Content:", memory['content'], height=200, disabled=True)
        
        # Embedding analysis if available
        st.subheader("🔗 Embedding Analysis")
        try:
            embedding_info = memory_service.get_embedding_info()
            st.info(f"Current embedding backend: {embedding_info['backend']} ({embedding_info['dimension']}D)")
            
            if st.button("Generate Embedding", key=f"embed_{memory_id}"):
                with st.spinner("Generating embedding..."):
                    embedding_manager = memory_service._get_embedding_manager()
                    vector = embedding_manager.embed(memory['content'])
                    
                    st.success(f"✅ Embedding generated: {len(vector)} dimensions")
                    st.write(f"First 10 values: {vector[:10]}")
                    
        except Exception as e:
            st.error(f"Embedding analysis failed: {e}")
        
    except Exception as e:
        st.error(f"Error analyzing memory {memory_id}: {e}")

# Initialize session state for this tab
if 'show_schema' not in st.session_state:
    st.session_state.show_schema = False
if 'show_patterns' not in st.session_state:
    st.session_state.show_patterns = False
if 'show_quality' not in st.session_state:
    st.session_state.show_quality = False
if 'show_value' not in st.session_state:
    st.session_state.show_value = False
if 'analyze_memory_id' not in st.session_state:
    st.session_state.analyze_memory_id = None