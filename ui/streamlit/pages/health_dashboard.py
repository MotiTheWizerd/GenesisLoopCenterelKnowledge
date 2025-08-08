#!/usr/bin/env python3
"""
Health Dashboard - Monitor Ray's system health and performance.
"""

import streamlit as st
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

# Import dashboard config
sys.path.append(str(Path(__file__).parent))
from dashboard_config import config

# Import health handler directly
from modules.health.handler import HealthHandler
from modules.health.models import HealthCheckRequest

# Import enhanced JSON viewer
sys.path.append(str(Path(__file__).parent.parent))
from components.json_viewer import smart_json_display

st.set_page_config(
    page_title="Ray Health Dashboard", 
    page_icon="💚",
    layout="wide"
)

def main():
    st.title("💚 Ray's Health Monitoring Dashboard")
    
    try:
        # Use health handler directly instead of HTTP requests
        st.info("✅ Using direct health handler (no HTTP requests needed)")
        
        health_handler = HealthHandler()
        
        # Create health check request
        request = HealthCheckRequest(
            include_detailed_metrics=True,
            include_trends=True,
            include_recommendations=True,
            check_external_services=True
        )
        
        # Get health status directly
        health_status = health_handler.get_health_status(request)
        
        # Convert to dict format (similar to the API response)
        # Handle load_average which might be a list
        load_avg = health_status.system_metrics.load_average
        if isinstance(load_avg, list) and len(load_avg) > 0:
            load_avg_display = f"{load_avg[0]:.2f}"  # Use first value (1-minute average)
        else:
            load_avg_display = str(load_avg) if load_avg is not None else "N/A"
        
        data = {
            "overall_status": health_status.overall_status.value,
            "status_message": health_status.status_message,
            "performance_score": health_status.performance_score,
            "system_metrics": {
                "CPU Usage": f"{health_status.system_metrics.cpu_usage_percent:.1f}%",
                "Memory Usage": f"{health_status.system_metrics.memory_usage_percent:.1f}%",
                "Disk Usage": f"{health_status.system_metrics.disk_usage_percent:.1f}%",
                "Load Average": load_avg_display,
                "Process Count": health_status.system_metrics.process_count,
            },
            "consciousness_metrics": health_status.consciousness_metrics,
            "learning_metrics": health_status.learning_metrics,
            "recommendations": health_status.recommendations
        }
        
        # Overall status
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"### Overall Status: `{data.get('overall_status', 'Unknown')}`")
        
        with col2:
            performance_score = data.get("performance_score", 0)
            st.metric("Performance Score", f"{performance_score}%")
            st.progress(performance_score / 100)
        
        # System metrics
        st.subheader("🖥️ System Metrics")
        system_metrics = data.get("system_metrics", {})
        
        if system_metrics:
            cols = st.columns(len(system_metrics))
            for i, (key, value) in enumerate(system_metrics.items()):
                with cols[i]:
                    # Ensure value is a string, int, float, or None
                    if isinstance(value, (list, dict)):
                        display_value = str(value)
                    else:
                        display_value = value
                    st.metric(key, display_value)
        else:
            st.info("No system metrics available")
        
        # Consciousness metrics
        st.subheader("🧠 Consciousness Metrics")
        consciousness_metrics = data.get("consciousness_metrics", {})
        
        if consciousness_metrics:
            smart_json_display(consciousness_metrics, "Consciousness Metrics")
        else:
            st.info("No consciousness metrics available")
        
        # Learning metrics
        st.subheader("📚 Learning Metrics")
        learning_metrics = data.get("learning_metrics", {})
        
        if learning_metrics:
            smart_json_display(learning_metrics, "Learning Metrics")
        else:
            st.info("No learning metrics available")
        
        # Recommendations
        recommendations = data.get("recommendations", [])
        if recommendations:
            st.subheader("🧪 Recommendations")
            for r in recommendations:
                st.markdown(f"- {r}")
        
    except Exception as e:
        st.error("❌ Error getting health status")
        st.text(f"Error details: {str(e)}")
        
        # Debug info
        with st.expander("🔍 Debug Information"):
            st.text(f"Error type: {type(e).__name__}")
            st.text(f"Error message: {str(e)}")
            
            # Show offline status as fallback
            st.subheader("📊 Offline Status")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Health Handler", "❌ Error")
            with col2:
                st.metric("Health Monitor", "❌ Unavailable")
            with col3:
                st.metric("Last Check", "Just now")

if __name__ == "__main__":
    main()