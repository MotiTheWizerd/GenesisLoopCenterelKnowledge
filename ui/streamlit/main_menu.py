#!/usr/bin/env python3
"""
Main menu for Ray's Streamlit dashboards.
Provides easy navigation to all available monitoring and analysis tools.
"""

import streamlit as st
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

st.set_page_config(
    page_title="Ray's Dashboard Hub",
    page_icon="🧠",
    layout="wide"
)

st.title("🧠 Ray's Dashboard Hub")
st.markdown("### Welcome to Ray's comprehensive monitoring and analysis suite")

# Main dashboard sections
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Log Analysis")
    
    if st.button("📑 Simple Log Viewer", key="simple_log"):
        st.switch_page("pages/01_simple_log_viewer.py")
        
    if st.button("🔍 Advanced Log Viewer", key="advanced_log"):
        st.switch_page("pages/02_advanced_log_viewer.py")
        
    if st.button("📊 Main Log Dashboard", key="main_log"):
        st.switch_page("pages/03_log_dashboard.py")

    st.subheader("🔍 Memory & Processing")
    
    if st.button("🧠 Memory Explorer", key="memory_explorer"):
        st.switch_page("pages/memory_explorer_tab.py")
        
    if st.button("📊 Memory Analysis", key="memory_analysis"):
        st.switch_page("pages/memory_analysis_tab.py")
        
    if st.button("⚙️ Memory Management", key="memory_management"):
        st.switch_page("pages/memory_management_tab.py")
    
    st.subheader("🤖 AI Intelligence")
    
    if st.button("🔍 Embedding Search", key="embedding_search"):
        st.switch_page("pages/embedding_search.py")
        
    if st.button("🧠 Learning & Planning", key="learning_planning"):
        st.switch_page("pages/learning_planner.py")

with col2:
    st.subheader("💚 System Health")
    
    if st.button("💚 Health Dashboard", key="health"):
        st.switch_page("pages/health_dashboard.py")
        
    if st.button("📈 Statistics Dashboard", key="stats"):
        st.switch_page("pages/04_statistics_dashboard.py")
        
    if st.button("⏱️ Timeline View", key="timeline"):
        st.switch_page("pages/05_timeline_view.py")

    st.subheader("⚙️ Operations")
    
    if st.button("🔧 System Operations", key="system_ops"):
        st.info("System operations panel - Coming soon!")
        
    if st.button("📋 Task Management", key="task_mgmt"):
        st.info("Task management interface - Coming soon!")
        
    if st.button("🔄 Data Processing", key="data_proc"):
        st.info("Data processing tools - Coming soon!")

# System status overview
st.markdown("---")
st.subheader("📡 System Status Overview")

try:
    import requests
    response = requests.get("http://localhost:8000/health/status")
    if response.status_code == 200:
        data = response.json()
        status_col1, status_col2, status_col3 = st.columns(3)
        
        with status_col1:
            st.metric("System Status", data["overall_status"])
        
        with status_col2:
            st.metric("Performance Score", f"{data['performance_score']}%")
        
        with status_col3:
            st.metric("Active Tasks", data.get("active_tasks", "N/A"))
    else:
        st.warning("⚠️ Health monitoring service is not responding")
except Exception as e:
    st.error("❌ Could not connect to health monitoring service")

# Documentation and help
st.markdown("---")
st.markdown("""
### 📚 Documentation
- Refer to `/docs/DASHBOARD_FEATURES_v2.md` for detailed features
- Check `/docs/real-time-monitoring-guide.md` for monitoring best practices
- See `/docs/STREAMLIT_DASHBOARD_UPDATES.md` for recent improvements
- View `/docs/components/JSON_VIEWER_GUIDE.md` for JSON display features
- Read `/docs/DASHBOARD_CONFIGURATION_GUIDE.md` for configuration details
""")

# Footer
st.markdown("---")
st.markdown("*Powered by Ray's Consciousness Engine - v1.1.0*")
