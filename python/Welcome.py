import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Digital Manufacturing System",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional styling
st.markdown("""
    <style>
        h1 {
            color: #1a202c;
            font-weight: 700;
            letter-spacing: -0.5px;
            margin-bottom: 0.5rem;
        }
        .welcome-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
        }
        .welcome-header {
            font-size: 3rem;
            font-weight: 700;
            color: #1a202c;
            margin-bottom: 1rem;
        }
        .welcome-subtitle {
            font-size: 1.25rem;
            color: #4a5568;
            margin-bottom: 2rem;
            max-width: 600px;
        }
        .welcome-description {
            font-size: 1rem;
            color: #718096;
            margin-bottom: 3rem;
            max-width: 700px;
            line-height: 1.6;
        }
        .feature-item {
            background: #f7fafc;
            padding: 1.5rem;
            border-radius: 12px;
            border-left: 4px solid #667eea;
        }
        .feature-icon {
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }
        .feature-title {
            font-weight: 600;
            color: #2d3748;
            margin-bottom: 0.5rem;
        }
        .feature-text {
            font-size: 0.9rem;
            color: #718096;
        }
        .footer {
            position: fixed;
            left: 0;
            bottom: 0;
            width: 100%;
            background-color: #f7fafc;
            border-top: 1px solid #e2e8f0;
            padding: 1rem;
            text-align: center;
            font-size: 0.85rem;
            color: #718096;
            z-index: 1000;
        }
        .footer a {
            color: #667eea;
            text-decoration: none;
            margin: 0 0.5rem;
        }
        .footer a:hover {
            text-decoration: underline;
        }
    </style>
    """, unsafe_allow_html=True)

# Welcome page content
st.markdown("""
<div class="welcome-container">
    <div class="welcome-header">🏭 Manufacturing Dashboard</div>
    <div class="welcome-subtitle">Smart Production Intelligence System</div>
    <div class="welcome-description">
        Welcome to the Digital Manufacturing System. This comprehensive platform provides real-time 
        monitoring and analytics of your production quality, process performance, and operational metrics. 
        Leverage data-driven insights to optimize manufacturing efficiency and minimize defects.
    </div>
</div>
""", unsafe_allow_html=True)

# Navigation info
st.info("👉 Use the sidebar to navigate to Login, Dashboard, or Admin Panel pages")

# Feature highlights
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="feature-item">
        <div class="feature-icon">📊</div>
        <div class="feature-title">Real-time Analytics</div>
        <div class="feature-text">Monitor production metrics and quality indicators in real-time with live data feeds</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-item">
        <div class="feature-icon">🔍</div>
        <div class="feature-title">Advanced Insights</div>
        <div class="feature-text">Analyze patterns, trends, and anomalies across multiple process steps</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="feature-item">
        <div class="feature-icon">⚡</div>
        <div class="feature-title">Performance Tracking</div>
        <div class="feature-text">Track quality rates, failure counts, and process efficiency metrics</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("")
st.markdown("")


# Footer
st.markdown("""
<div class="footer">
    <div style="margin-bottom: 0.3rem;">
        © 2026 Jeff Huang | <strong>For Demonstration Purposes Only</strong>
    </div>
    <div>
        <a href="https://www.linkedin.com/in/jhuang116" target="_blank">LinkedIn</a> |
        <a href="https://bobbaninja.github.io" target="_blank">GitHub</a> |
        <a href="mailto:bobbaninja@gmail.com">Email</a>
    </div>
</div>
""", unsafe_allow_html=True)
