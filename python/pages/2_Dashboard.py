import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# Page configuration
st.set_page_config(
    page_title="Dashboard - Manufacturing Dashboard",
    page_icon="📊",
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

# Footer function
def show_footer():
    """Display footer with author information on all pages"""
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

# Check if user is logged in
if 'user' not in st.session_state or st.session_state.user is None:
    st.warning("⚠️ Please log in to access the dashboard")
    st.info("👉 Navigate to **Login** page using the sidebar")
    show_footer()
    st.stop()

# Get user role
user_info = st.session_state.user
user_role = user_info['role_name'].lower()

# Header section
col1, col2, col3 = st.columns([3, 1, 0.7])
with col1:
    st.title("🏭 Digital Manufacturing System")
    role_display = user_info['role_name'].title()
    
    # Role badges
    role_colors = {
        'admin': '#dc2626',
        'npi engineer': '#7c3aed',
        'manufacturing engineer': '#2563eb',
        'production manager': '#059669',
        'operator': '#f59e0b'
    }
    role_color = role_colors.get(user_role, '#6b7280')
    st.markdown(f"**Logged in as:** {user_info['username']} <span style='background-color: {role_color}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.85em;'>{role_display}</span>", unsafe_allow_html=True)

with col2:
    st.markdown("")
    st.markdown("**Status:** <span style='color: green; font-weight: bold;'>● Online</span>", unsafe_allow_html=True)

with col3:
    st.markdown("")
    if st.button("🔄 Refresh", use_container_width=True, help="Refresh data and statistics"):
        st.rerun()

st.markdown("---")

# Connect to database with error handling
try:
    db_path = os.path.join(os.path.dirname(__file__), "../../sql/manufacturing.db")
    conn = sqlite3.connect(db_path)
    
    # Query measurement data - Updated for new schema
    query = """
    SELECT 
        m.measurement_id,
        m.measured_value,
        m.is_in_spec,
        m.measurement_timestamp as event_time,
        b.batch_number as serial_number,
        b.batch_id,
        b.status as batch_status,
        s.station_name as process_step,
        s.station_id,
        es.check_name,
        es.parameter_name,
        es.lower_limit,
        es.upper_limit,
        es.target_value,
        es.unit,
        p.product_name,
        p.product_code,
        l.line_code,
        m.machine_id,
        u.username as operator_name,
        CASE WHEN m.is_in_spec = 0 THEN 1 ELSE 0 END as out_of_spec,
        m.deviation_percent
    FROM measurement_data m
    JOIN batches b ON m.batch_id = b.batch_id
    JOIN stations s ON m.station_id = s.station_id
    JOIN eng_spec es ON m.spec_id = es.spec_id
    JOIN products p ON b.product_id = p.product_id
    JOIN lines l ON m.line_id = l.line_id
    LEFT JOIN users u ON m.operator_id = u.user_id
    ORDER BY m.measurement_timestamp DESC
    LIMIT 1000
    """
    df = pd.read_sql(query, conn)
    
    # Get batch summary
    batch_query = """
    SELECT 
        b.batch_id,
        b.batch_number,
        p.product_name,
        b.status,
        b.quantity_planned,
        b.quantity_completed,
        COUNT(m.measurement_id) as total_measurements,
        SUM(CASE WHEN m.is_in_spec = 0 THEN 1 ELSE 0 END) as failures
    FROM batches b
    JOIN products p ON b.product_id = p.product_id
    LEFT JOIN measurement_data m ON b.batch_id = m.batch_id
    GROUP BY b.batch_id
    ORDER BY b.created_date DESC
    """
    batch_df = pd.read_sql(batch_query, conn)
    
    conn.close()
    
    if not df.empty:
        # Key metrics section
        st.subheader("📊 Key Performance Indicators")
        
        total_events = len(df)
        out_of_spec_count = int(df['out_of_spec'].sum())
        active_batches = len(batch_df[batch_df['status'] == 'In Progress'])
        quality_rate = round((1 - (out_of_spec_count / total_events)) * 100, 2) if total_events > 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Total Measurements",
                value=f"{total_events:,}",
                delta="Last 1000 records"
            )
        
        with col2:
            st.metric(
                label="Out of Spec",
                value=out_of_spec_count,
                delta=f"{(out_of_spec_count/total_events*100):.1f}% failure rate" if total_events > 0 else "0%",
                delta_color="inverse"
            )
        
        with col3:
            st.metric(
                label="Quality Rate",
                value=f"{quality_rate}%",
                delta="Target: 95%",
                delta_color="normal" if quality_rate >= 95 else "off"
            )
        
        with col4:
            st.metric(
                label="Active Batches",
                value=active_batches,
                delta="In production"
            )
        
        st.markdown("---")
        
        # Product & Batch Overview
        st.subheader("🏭 Production Overview")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📦 Batch Summary")
            batch_display = batch_df[['batch_number', 'product_name', 'status', 'quantity_completed', 'quantity_planned']].copy()
            if not batch_display.empty:
                batch_display['progress'] = ((batch_display['quantity_completed'] / batch_display['quantity_planned']) * 100).round(1).astype(str) + '%'
                st.dataframe(
                    batch_display[['batch_number', 'product_name', 'status', 'progress']].rename(
                        columns={'batch_number': 'Batch', 'product_name': 'Product', 'status': 'Status', 'progress': 'Progress'}
                    ),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("No batches found")
        
        with col2:
            st.markdown("#### 📊 Product Quality Summary")
            product_quality = df.groupby('product_name').agg({
                'measurement_id': 'count',
                'out_of_spec': 'sum'
            }).reset_index()
            product_quality['quality_rate'] = ((product_quality['measurement_id'] - product_quality['out_of_spec']) / product_quality['measurement_id'] * 100).round(2)
            product_quality = product_quality.rename(columns={'product_name': 'Product', 'measurement_id': 'Tests', 'out_of_spec': 'Failures', 'quality_rate': 'Quality %'})
            st.dataframe(product_quality, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        # Visualizations section
        st.subheader("📈 Performance Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Measured Values Over Time")
            fig1 = px.scatter(
                df, 
                x="event_time", 
                y="measured_value", 
                color="out_of_spec",
                hover_data=['product_name', 'process_step', 'parameter_name', 'unit'],
                title=None,
                labels={"out_of_spec": "Out of Spec", "event_time": "Time", "measured_value": "Value"},
                color_discrete_map={0: "#10b981", 1: "#ef4444"}
            )
            fig1.update_layout(
                hovermode="closest",
                height=400,
                template="plotly_white",
                margin=dict(l=0, r=0, t=0, b=0)
            )
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            st.markdown("#### Measurements by Station")
            station_data = df.groupby('process_step')['measurement_id'].count().reset_index()
            station_data.columns = ['Station', 'Measurements']
            station_data = station_data.sort_values('Measurements', ascending=False)
            
            fig2 = px.bar(
                station_data,
                x="Station",
                y="Measurements",
                title=None,
                color="Measurements",
                color_continuous_scale="Blues"
            )
            fig2.update_layout(
                height=400,
                template="plotly_white",
                showlegend=False,
                margin=dict(l=0, r=0, t=0, b=0)
            )
            st.plotly_chart(fig2, use_container_width=True)
        
        st.markdown("#### Quality Rate by Process Step")
        process_quality = df.groupby("process_step").agg({
            "out_of_spec": ["sum", "count"]
        }).reset_index()
        process_quality.columns = ["process_step", "failures", "total"]
        process_quality["quality_rate"] = ((process_quality["total"] - process_quality["failures"]) / process_quality["total"] * 100).round(2)
        
        fig3 = px.bar(
            process_quality,
            x="process_step",
            y="quality_rate",
            title=None,
            labels={"process_step": "Process Step", "quality_rate": "Quality Rate (%)"},
            color="quality_rate",
            color_continuous_scale="Greens"
        )
        fig3.update_layout(
            height=350,
            template="plotly_white",
            showlegend=False,
            margin=dict(l=0, r=0, t=0, b=0),
            yaxis=dict(
                range=[0, 100], 
                title="Quality Rate (%)",
                ticksuffix="%",
                fixedrange=True
            )
        )
        fig3.update_yaxes(range=[0, 100])
        st.plotly_chart(fig3, use_container_width=True)
        
        st.markdown("---")
        
        # Data summary section
        st.subheader("📋 Data Summary")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Process Steps Distribution**")
            st.dataframe(
                df['process_step'].value_counts().reset_index().rename(columns={"index": "Process", "process_step": "Count"}),
                use_container_width=True,
                hide_index=True
            )
        
        with col2:
            st.markdown("**Quality Metrics by Step**")
            st.dataframe(
                process_quality[["process_step", "failures", "total", "quality_rate"]].rename(
                    columns={"process_step": "Step", "failures": "Failures", "total": "Total", "quality_rate": "Quality %"}
                ),
                use_container_width=True,
                hide_index=True
            )
    else:
        st.warning("⚠️ No data available in the database.")
        
except sqlite3.OperationalError as e:
    st.error(f"🔴 Database Connection Error: {e}")
    st.info("Please check if the database file exists at the correct location.")

# Footer
show_footer()
