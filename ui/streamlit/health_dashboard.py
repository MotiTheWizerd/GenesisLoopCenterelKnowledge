import streamlit as st
import requests

st.set_page_config(page_title="Ray Health Dashboard", layout="centered")

st.title("💚 Ray's Health Monitoring Dashboard")

try:
    response = requests.get("http://localhost:8000/health/status")
    data = response.json()

    st.markdown(f"### Overall Status: `{data['overall_status']}`")
    st.progress(data["performance_score"] / 100)

    st.subheader("🖥️ System Metrics")
    st.write(data["system_metrics"])

    st.subheader("🧠 Consciousness Metrics")
    st.write(data["consciousness_metrics"])

    st.subheader("📚 Learning Metrics")
    st.write(data["learning_metrics"])

    if data.get("recommendations"):
        st.subheader("🧪 Recommendations")
        for r in data["recommendations"]:
            st.markdown(f"- {r}")

except Exception as e:
    st.error("❌ Could not fetch Ray's health status.")
    st.text(str(e))
