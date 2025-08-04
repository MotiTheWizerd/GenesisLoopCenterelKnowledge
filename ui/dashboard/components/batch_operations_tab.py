"""
Batch Operations Tab Component
Web interface for CLI tools and bulk operations
"""

import streamlit as st
import subprocess
import os
import json
import tempfile
from datetime import datetime
import pandas as pd

def render_batch_operations_tab():
    """Render the batch operations tab"""
    
    st.header("⚡ Batch Operations")
    st.markdown("*Web interface for bulk operations and CLI tools*")
    
    # Check system status
    if not st.session_state.get('system_ready', False):
        st.error("❌ Memory system is not ready. Please ensure FAISS index and metadata files exist.")
        return
    
    # Operation categories
    st.subheader("🔧 Available Operations")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📥 Raw Data Import", help="Import .txt, .json, .jsonl files"):
            st.session_state.show_raw_import = True
    
    with col2:
        if st.button("🔍 Redundancy Detection", help="Find and remove duplicate memories"):
            st.session_state.show_redundancy_detection = True
    
    with col3:
        if st.button("🧹 Bulk Cleanup", help="Advanced cleanup operations"):
            st.session_state.show_bulk_cleanup = True
    
    with col4:
        if st.button("📊 Batch Analysis", help="Run analysis on memory batches"):
            st.session_state.show_batch_analysis = True
    
    # Display operation interfaces
    if st.session_state.get('show_raw_import', False):
        render_raw_import_interface()
    
    if st.session_state.get('show_redundancy_detection', False):
        render_redundancy_detection_interface()
    
    if st.session_state.get('show_bulk_cleanup', False):
        render_bulk_cleanup_interface()
    
    if st.session_state.get('show_batch_analysis', False):
        render_batch_analysis_interface()

def render_raw_import_interface():
    """Render raw data import interface"""
    st.subheader("📥 Raw Data Import")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Choose a file to import",
        type=['txt', 'json', 'jsonl'],
        help="Upload .txt, .json, or .jsonl files to import into Ray's memory system"
    )
    
    if uploaded_file is not None:
        # Display file info
        st.info(f"📄 File: {uploaded_file.name} ({uploaded_file.size} bytes)")
        
        # Import options
        col1, col2 = st.columns(2)
        
        with col1:
            embedding_backend = st.selectbox(
                "Embedding Backend:",
                ["gemini", "minilm"],
                index=0,
                help="Choose embedding backend (Gemini recommended for quality)"
            )
        
        with col2:
            merge_with_existing = st.checkbox(
                "Merge with existing memories",
                value=True,
                help="Add to existing memories (unchecked = replace all)"
            )
        
        # Additional options for .txt files
        chunk_size = 1000
        if uploaded_file.name.endswith('.txt'):
            chunk_size = st.slider(
                "Chunk size (for .txt files):",
                min_value=100,
                max_value=5000,
                value=1000,
                step=100,
                help="Size of text chunks in characters"
            )
        
        # API key input for Gemini
        gemini_api_key = None
        if embedding_backend == "gemini":
            gemini_api_key = st.text_input(
                "Gemini API Key:",
                type="password",
                value=os.getenv('GEMINI_API_KEY', ''),
                help="Enter your Gemini API key or set GEMINI_API_KEY environment variable"
            )
            
            if not gemini_api_key:
                st.warning("⚠️ Gemini API key required for Gemini backend")
        
        # Import button
        if st.button("🚀 Import File", type="primary"):
            if embedding_backend == "gemini" and not gemini_api_key:
                st.error("❌ Gemini API key required")
                return
            
            import_file(uploaded_file, embedding_backend, gemini_api_key, merge_with_existing, chunk_size)

def render_redundancy_detection_interface():
    """Render redundancy detection interface"""
    st.subheader("🔍 Redundancy Detection")
    
    # Detection options
    col1, col2 = st.columns(2)
    
    with col1:
        similarity_threshold = st.slider(
            "Similarity Threshold:",
            min_value=0.5,
            max_value=1.0,
            value=0.85,
            step=0.05,
            help="Higher values = more strict duplicate detection"
        )
    
    with col2:
        auto_cleanup = st.checkbox(
            "Auto-execute cleanup",
            value=False,
            help="Automatically execute suggested deletions (use with caution!)"
        )
    
    # Run detection
    if st.button("🔍 Detect Redundancies", type="primary"):
        run_redundancy_detection(similarity_threshold, auto_cleanup)

def render_bulk_cleanup_interface():
    """Render bulk cleanup interface"""
    st.subheader("🧹 Advanced Bulk Cleanup")
    
    # Cleanup criteria
    st.write("**Select cleanup criteria:**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        cleanup_short = st.checkbox("Remove very short memories (< 20 chars)", value=True)
        cleanup_low_importance = st.checkbox("Remove low importance memories (< 0.2)", value=False)
        cleanup_confirmations = st.checkbox("Remove simple confirmations ('yes', 'ok', etc.)", value=True)
    
    with col2:
        cleanup_duplicates = st.checkbox("Remove exact duplicates", value=True)
        cleanup_empty = st.checkbox("Remove empty or whitespace-only memories", value=True)
        cleanup_errors = st.checkbox("Remove error messages and system logs", value=False)
    
    # Custom cleanup
    st.write("**Custom cleanup:**")
    custom_patterns = st.text_area(
        "Remove memories containing these patterns (one per line):",
        placeholder="error\nfailed\ntest\n...",
        help="Enter text patterns to remove (case-insensitive)"
    )
    
    # Preview cleanup
    if st.button("👀 Preview Cleanup"):
        preview_cleanup(cleanup_short, cleanup_low_importance, cleanup_confirmations,
                       cleanup_duplicates, cleanup_empty, cleanup_errors, custom_patterns)
    
    # Execute cleanup
    st.warning("⚠️ This action cannot be undone! Make sure to backup your data.")
    if st.button("🧹 Execute Cleanup", type="primary"):
        execute_cleanup(cleanup_short, cleanup_low_importance, cleanup_confirmations,
                       cleanup_duplicates, cleanup_empty, cleanup_errors, custom_patterns)

def render_batch_analysis_interface():
    """Render batch analysis interface"""
    st.subheader("📊 Batch Analysis")
    
    # Analysis options
    analysis_types = st.multiselect(
        "Select analysis types:",
        [
            "Content Quality Assessment",
            "Importance Score Distribution",
            "Source Balance Analysis",
            "Temporal Pattern Analysis",
            "Vocabulary Growth Analysis",
            "Embedding Quality Check"
        ],
        default=["Content Quality Assessment", "Source Balance Analysis"]
    )
    
    # Batch size
    batch_size = st.slider(
        "Batch size:",
        min_value=100,
        max_value=5000,
        value=1000,
        step=100,
        help="Number of memories to analyze per batch"
    )
    
    # Run analysis
    if st.button("📊 Run Batch Analysis", type="primary"):
        run_batch_analysis(analysis_types, batch_size)

def import_file(uploaded_file, backend, api_key, merge, chunk_size):
    """Import uploaded file using raw_loader.py"""
    try:
        with st.spinner(f"Importing {uploaded_file.name}..."):
            # Save uploaded file to temporary location
            with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{uploaded_file.name}") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name
            
            # Prepare command
            cmd = [
                "python", "tools/raw_loader.py",
                tmp_file_path,
                "--backend", backend,
                "--chunk-size", str(chunk_size)
            ]
            
            if not merge:
                cmd.append("--no-merge")
            
            if backend == "gemini" and api_key:
                cmd.extend(["--api-key", api_key])
            
            # Set environment variable for API key
            env = os.environ.copy()
            if backend == "gemini" and api_key:
                env['GEMINI_API_KEY'] = api_key
            
            # Run import
            result = subprocess.run(cmd, capture_output=True, text=True, env=env)
            
            # Clean up temp file
            os.unlink(tmp_file_path)
            
            if result.returncode == 0:
                st.success("✅ Import completed successfully!")
                st.code(result.stdout)
                
                # Clear memory service cache
                if hasattr(st.session_state, 'memory_service'):
                    st.session_state.memory_service._memories = None
                    st.session_state.memory_service._metadata = None
                    st.session_state.memory_service._faiss_index = None
                
                st.info("🔄 Memory system cache cleared. Refresh other tabs to see new data.")
            else:
                st.error("❌ Import failed!")
                st.code(result.stderr)
                
    except Exception as e:
        st.error(f"Error during import: {e}")

def run_redundancy_detection(threshold, auto_cleanup):
    """Run redundancy detection"""
    try:
        with st.spinner("Detecting redundant memories..."):
            # Prepare command
            cmd = [
                "python", "tools/redundancy_detector.py",
                "--threshold", str(threshold),
                "--report", "redundancy_report.txt"
            ]
            
            if not auto_cleanup:
                cmd.append("--no-script")
            
            # Run detection
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                st.success("✅ Redundancy detection completed!")
                st.code(result.stdout)
                
                # Display report if it exists
                if os.path.exists("redundancy_report.txt"):
                    with open("redundancy_report.txt", 'r', encoding='utf-8') as f:
                        report_content = f.read()
                    
                    st.subheader("📄 Redundancy Report")
                    st.text_area("Report:", value=report_content, height=400)
                    
                    # Offer download
                    st.download_button(
                        "📥 Download Report",
                        data=report_content,
                        file_name=f"redundancy_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain"
                    )
                
                if auto_cleanup and os.path.exists("cleanup_script.py"):
                    st.warning("⚠️ Auto-cleanup script generated. Review before running!")
                    
                    with open("cleanup_script.py", 'r', encoding='utf-8') as f:
                        script_content = f.read()
                    
                    st.code(script_content, language='python')
                    
                    if st.button("🚀 Execute Cleanup Script"):
                        exec_result = subprocess.run(["python", "cleanup_script.py"], 
                                                   capture_output=True, text=True)
                        if exec_result.returncode == 0:
                            st.success("✅ Cleanup executed successfully!")
                            st.code(exec_result.stdout)
                        else:
                            st.error("❌ Cleanup failed!")
                            st.code(exec_result.stderr)
            else:
                st.error("❌ Redundancy detection failed!")
                st.code(result.stderr)
                
    except Exception as e:
        st.error(f"Error during redundancy detection: {e}")

def preview_cleanup(short, low_imp, confirmations, duplicates, empty, errors, custom_patterns):
    """Preview cleanup operations"""
    try:
        memory_service = st.session_state.memory_service
        memories = memory_service._load_memories()
        
        # Identify memories for cleanup
        cleanup_candidates = []
        
        custom_pattern_list = [p.strip().lower() for p in custom_patterns.split('\n') if p.strip()] if custom_patterns else []
        
        for i, memory in enumerate(memories):
            content = memory.get('content', '')
            content_lower = content.lower()
            importance = memory.get('importance', 0)
            
            reasons = []
            
            # Check criteria
            if short and len(content) < 20:
                reasons.append("Very short content")
            
            if low_imp and isinstance(importance, (int, float)) and importance < 0.2:
                reasons.append("Low importance")
            
            if confirmations and any(word in content_lower for word in ['yes', 'ok', 'okay', 'sure', 'yep', 'got it']):
                reasons.append("Simple confirmation")
            
            if empty and not content.strip():
                reasons.append("Empty content")
            
            if errors and any(word in content_lower for word in ['error', 'failed', 'exception', 'traceback']):
                reasons.append("Error message")
            
            if custom_pattern_list and any(pattern in content_lower for pattern in custom_pattern_list):
                reasons.append("Custom pattern match")
            
            if reasons:
                cleanup_candidates.append({
                    'memory_id': f"mem-{i}",
                    'content': content[:100] + "..." if len(content) > 100 else content,
                    'importance': importance,
                    'reasons': ', '.join(reasons)
                })
        
        # Display preview
        st.subheader(f"👀 Cleanup Preview ({len(cleanup_candidates)} memories)")
        
        if cleanup_candidates:
            preview_df = pd.DataFrame(cleanup_candidates)
            st.dataframe(preview_df, use_container_width=True)
            
            st.info(f"📊 Would remove {len(cleanup_candidates)} out of {len(memories)} memories ({len(cleanup_candidates)/len(memories)*100:.1f}%)")
        else:
            st.success("✅ No memories match the cleanup criteria")
            
    except Exception as e:
        st.error(f"Error previewing cleanup: {e}")

def execute_cleanup(short, low_imp, confirmations, duplicates, empty, errors, custom_patterns):
    """Execute cleanup operations"""
    try:
        with st.spinner("Executing cleanup operations..."):
            memory_service = st.session_state.memory_service
            memories = memory_service._load_memories()
            metadata = memory_service._load_metadata()
            
            # Create backup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_memories = f"extract/agent_memories_cleanup_backup_{timestamp}.json"
            backup_metadata = f"extract/memory_metadata_cleanup_backup_{timestamp}.json"
            
            import shutil
            shutil.copy("extract/agent_memories.json", backup_memories)
            shutil.copy("extract/memory_metadata.json", backup_metadata)
            
            # Identify memories to keep
            custom_pattern_list = [p.strip().lower() for p in custom_patterns.split('\n') if p.strip()] if custom_patterns else []
            
            cleaned_memories = []
            removed_count = 0
            
            for i, memory in enumerate(memories):
                content = memory.get('content', '')
                content_lower = content.lower()
                importance = memory.get('importance', 0)
                
                should_remove = False
                
                # Check removal criteria
                if short and len(content) < 20:
                    should_remove = True
                elif low_imp and isinstance(importance, (int, float)) and importance < 0.2:
                    should_remove = True
                elif confirmations and any(word in content_lower for word in ['yes', 'ok', 'okay', 'sure', 'yep', 'got it']):
                    should_remove = True
                elif empty and not content.strip():
                    should_remove = True
                elif errors and any(word in content_lower for word in ['error', 'failed', 'exception', 'traceback']):
                    should_remove = True
                elif custom_pattern_list and any(pattern in content_lower for pattern in custom_pattern_list):
                    should_remove = True
                
                if not should_remove:
                    cleaned_memories.append(memory)
                else:
                    removed_count += 1
            
            # Remove duplicates if requested
            if duplicates:
                seen_content = set()
                deduped_memories = []
                
                for memory in cleaned_memories:
                    content_hash = hash(memory.get('content', ''))
                    if content_hash not in seen_content:
                        seen_content.add(content_hash)
                        deduped_memories.append(memory)
                    else:
                        removed_count += 1
                
                cleaned_memories = deduped_memories
            
            # Create new metadata
            cleaned_metadata = {}
            for i, memory in enumerate(cleaned_memories):
                cleaned_metadata[f"mem-{i}"] = memory
            
            # Save cleaned data
            with open("extract/agent_memories.json", 'w', encoding='utf-8') as f:
                json.dump(cleaned_memories, f, indent=2, ensure_ascii=False)
            
            with open("extract/memory_metadata.json", 'w', encoding='utf-8') as f:
                json.dump(cleaned_metadata, f, indent=2, ensure_ascii=False)
            
            st.success(f"✅ Cleanup completed!")
            st.info(f"📊 Removed {removed_count} memories, kept {len(cleaned_memories)}")
            st.info(f"💾 Backup saved to: {backup_memories}")
            
            # Clear cache
            memory_service._memories = None
            memory_service._metadata = None
            memory_service._faiss_index = None
            
            st.warning("🔄 Remember to rebuild the FAISS index!")
            
    except Exception as e:
        st.error(f"Error during cleanup: {e}")

def run_batch_analysis(analysis_types, batch_size):
    """Run batch analysis operations"""
    try:
        with st.spinner("Running batch analysis..."):
            memory_service = st.session_state.memory_service
            memories = memory_service._load_memories()
            
            results = {}
            
            # Process in batches
            for i in range(0, len(memories), batch_size):
                batch = memories[i:i + batch_size]
                batch_num = i // batch_size + 1
                
                st.write(f"Processing batch {batch_num}...")
                
                for analysis_type in analysis_types:
                    if analysis_type not in results:
                        results[analysis_type] = []
                    
                    if analysis_type == "Content Quality Assessment":
                        quality_score = assess_content_quality(batch)
                        results[analysis_type].append(quality_score)
                    
                    elif analysis_type == "Source Balance Analysis":
                        balance_score = assess_source_balance(batch)
                        results[analysis_type].append(balance_score)
                    
                    # Add more analysis types as needed
            
            # Display results
            st.subheader("📊 Batch Analysis Results")
            
            for analysis_type, scores in results.items():
                st.write(f"**{analysis_type}:**")
                avg_score = sum(scores) / len(scores) if scores else 0
                st.metric(f"Average Score", f"{avg_score:.2f}")
                
                # Plot scores over batches
                if len(scores) > 1:
                    import plotly.express as px
                    fig = px.line(x=range(1, len(scores) + 1), y=scores,
                                title=f"{analysis_type} Over Batches",
                                labels={'x': 'Batch Number', 'y': 'Score'})
                    st.plotly_chart(fig, use_container_width=True)
            
    except Exception as e:
        st.error(f"Error during batch analysis: {e}")

def assess_content_quality(batch):
    """Assess content quality for a batch"""
    if not batch:
        return 0
    
    total_score = 0
    for memory in batch:
        content = memory.get('content', '')
        score = 0
        
        # Length score
        if len(content) > 50:
            score += 0.3
        
        # Completeness score
        if content.strip():
            score += 0.2
        
        # Complexity score (word count)
        words = len(content.split())
        if words > 10:
            score += 0.3
        
        # Importance score
        importance = memory.get('importance', 0)
        if isinstance(importance, (int, float)):
            score += importance * 0.2
        
        total_score += min(score, 1.0)
    
    return total_score / len(batch)

def assess_source_balance(batch):
    """Assess source balance for a batch"""
    if not batch:
        return 0
    
    sources = [memory.get('source', '') for memory in batch]
    agent_count = sources.count('agent_response')
    user_count = sources.count('user_input')
    
    if agent_count + user_count == 0:
        return 0
    
    # Balance score (closer to 50/50 is better)
    balance_ratio = min(agent_count, user_count) / max(agent_count, user_count) if max(agent_count, user_count) > 0 else 0
    return balance_ratio

# Initialize session state for this tab
if 'show_raw_import' not in st.session_state:
    st.session_state.show_raw_import = False
if 'show_redundancy_detection' not in st.session_state:
    st.session_state.show_redundancy_detection = False
if 'show_bulk_cleanup' not in st.session_state:
    st.session_state.show_bulk_cleanup = False
if 'show_batch_analysis' not in st.session_state:
    st.session_state.show_batch_analysis = False