"""
Streamlit ML Prediction Frontend
Interactive UI for sending requests to FastAPI prediction service
and displaying results.
"""

import os
import requests
import streamlit as st
from datetime import datetime

# Configuration
FASTAPI_URL = os.getenv("FASTAPI_URL", "http://localhost:8000")
PREDICTION_ENDPOINT = f"{FASTAPI_URL}/predict"
HEALTH_ENDPOINT = f"{FASTAPI_URL}/health"

# Page configuration
st.set_page_config(
    page_title="ML Prediction Service",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title and description
st.title("🤖 ML Prediction Service")
st.markdown("""
This application sends features to the FastAPI ML prediction service
and displays real-time predictions with confidence scores.
""")

# Sidebar with info
st.sidebar.header("ℹ️ Service Information")

# Check API health
try:
    health_response = requests.get(HEALTH_ENDPOINT, timeout=5)
    if health_response.status_code == 200:
        st.sidebar.success("✅ API Service: Connected")
    else:
        st.sidebar.error("❌ API Service: Disconnected")
except requests.exceptions.RequestException as e:
    st.sidebar.error(f"❌ API Service: Error - {str(e)}")

st.sidebar.markdown(f"**API URL:** {FASTAPI_URL}")
st.sidebar.markdown("**Endpoint:** `/predict`")

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.header("📊 Input Features")
    
    # Create form for inputs
    with st.form("prediction_form"):
        feature_1 = st.slider(
            "Feature 1",
            min_value=0.0,
            max_value=10.0,
            value=5.0,
            step=0.1,
            help="First input feature"
        )
        
        feature_2 = st.slider(
            "Feature 2",
            min_value=0.0,
            max_value=10.0,
            value=5.0,
            step=0.1,
            help="Second input feature"
        )
        
        feature_3 = st.slider(
            "Feature 3",
            min_value=0.0,
            max_value=10.0,
            value=5.0,
            step=0.1,
            help="Third input feature"
        )
        
        submit_button = st.form_submit_button("🔮 Get Prediction", use_container_width=True)

with col2:
    st.header("📈 Quick Info")
    st.info(
        """
        - Submit features to get ML predictions
        - Results are cached in Redis (1 hour TTL)
        - Predictions logged to PostgreSQL
        - Real-time confidence scores
        """
    )

# Handle prediction request
if submit_button:
    try:
        # Prepare request data
        payload = {
            "feature_1": feature_1,
            "feature_2": feature_2,
            "feature_3": feature_3
        }
        
        # Show loading spinner
        with st.spinner("🔄 Getting prediction..."):
            response = requests.post(
                PREDICTION_ENDPOINT,
                json=payload,
                timeout=10
            )
        
        # Handle response
        if response.status_code == 200:
            result = response.json()
            
            # Display results in tabs
            tab1, tab2, tab3 = st.tabs(["🎯 Prediction", "📊 Details", "🔍 Debug Info"])
            
            with tab1:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric(
                        label="Prediction",
                        value=result["prediction"],
                        delta=f"Confidence: {result['confidence']:.2%}",
                        delta_color="normal"
                    )
                
                with col2:
                    cache_status = "✅ Cached" if result["cached"] else "🆕 Fresh"
                    st.metric(
                        label="Cache Status",
                        value=cache_status
                    )
            
            with tab2:
                st.json({
                    "features": {
                        "feature_1": feature_1,
                        "feature_2": feature_2,
                        "feature_3": feature_3
                    },
                    "prediction": result["prediction"],
                    "confidence": result["confidence"],
                    "timestamp": result["timestamp"]
                })
            
            with tab3:
                st.code(f"Request: {payload}", language="json")
                st.code(f"Response: {result}", language="json")
            
            st.success("✅ Prediction retrieved successfully!")
            st.balloons()
        
        else:
            st.error(f"❌ API Error: {response.status_code} - {response.text}")
    
    except requests.exceptions.Timeout:
        st.error("⏱️ Request timeout. API service may be slow or unresponsive.")
    
    except requests.exceptions.ConnectionError:
        st.error("🔴 Connection error. Cannot reach the API service. Make sure it's running.")
    
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: gray;">
    <p>ML Deployment with Kubernetes, GitOps, and CI/CD</p>
    <p><small>Built with FastAPI, Streamlit, PostgreSQL, and Redis</small></p>
</div>
""", unsafe_allow_html=True)
