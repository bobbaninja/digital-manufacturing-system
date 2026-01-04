import streamlit as st
import sqlite3
import pandas as pd
import os
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Admin Panel - Manufacturing Dashboard",
    page_icon="🔧",
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

# Check if user is logged in and is admin
if 'user' not in st.session_state or st.session_state.user is None:
    st.warning("⚠️ Please log in to access this page")
    st.info("👉 Navigate to **Login** page using the sidebar")
    show_footer()
    st.stop()

if st.session_state.user['role_name'].lower() != 'admin':
    st.error("🚫 Access Denied: Admin privileges required")
    st.info("👉 This page is only accessible to users with the Admin role")
    st.warning(f"Your current role: **{st.session_state.user['role_name'].title()}**")
    show_footer()
    st.stop()

# Header section
st.title("🗄️ Database Admin Panel")
st.markdown("**System administration and database management**")
st.markdown("---")

# Connect to database
try:
    db_path = os.path.join(os.path.dirname(__file__), "../../sql/manufacturing.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all table names (excluding sqlite internal tables)
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name NOT LIKE 'sqlite_%'
        ORDER BY name
    """)
    tables = [row[0] for row in cursor.fetchall()]
    
    st.subheader(f"📋 Database Tables ({len(tables)} total)")
    
    # Table selector
    selected_table = st.selectbox("Select a table to view:", tables)
    
    if selected_table:
        st.markdown(f"### 📊 Table: `{selected_table}`")
        
        # Get table info
        cursor.execute(f"PRAGMA table_info({selected_table})")
        columns_info = cursor.fetchall()
        
        # Display table schema
        with st.expander("🔍 View Table Schema"):
            schema_df = pd.DataFrame(columns_info, columns=['ID', 'Name', 'Type', 'NotNull', 'DefaultValue', 'PrimaryKey'])
            st.dataframe(schema_df, use_container_width=True, hide_index=True)
        
        # Get row count
        cursor.execute(f"SELECT COUNT(*) FROM {selected_table}")
        row_count = cursor.fetchone()[0]
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Rows", f"{row_count:,}")
        with col2:
            st.metric("Columns", len(columns_info))
        with col3:
            # Get size estimate (not exact in SQLite)
            st.metric("Status", "✅ Active")
        
        st.markdown("---")
        
        # Data viewer with pagination
        st.markdown("#### 📄 Table Data")
        
        # Limit selector
        col1, col2 = st.columns([1, 3])
        with col1:
            limit = st.selectbox("Rows to display:", [10, 25, 50, 100, 500, "All"], index=1)
        
        # Query data
        if limit == "All":
            query = f"SELECT * FROM {selected_table}"
        else:
            query = f"SELECT * FROM {selected_table} LIMIT {limit}"
        
        df = pd.read_sql(query, conn)
        
        if not df.empty:
            st.dataframe(df, use_container_width=True, height=400)
            
            # Export option
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 1, 2])
            with col1:
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name=f"{selected_table}_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        else:
            st.info(f"Table `{selected_table}` is empty")
    
    # Database statistics
    st.markdown("---")
    st.subheader("📊 Database Statistics")
    
    stats_cols = st.columns(4)
    
    for idx, table in enumerate(tables[:4]):
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        with stats_cols[idx]:
            st.metric(table, f"{count:,}")
    
    # Show all table counts
    if len(tables) > 4:
        with st.expander("📈 View All Table Counts"):
            all_stats = []
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                all_stats.append({'Table': table, 'Row Count': count})
            
            stats_df = pd.DataFrame(all_stats)
            st.dataframe(stats_df, use_container_width=True, hide_index=True)
    
    conn.close()
    
except sqlite3.Error as e:
    st.error(f"🔴 Database Error: {e}")
    st.warning("Please ensure the database is initialized. Run `database/init_db.py` and `database/seed_data.py` first.")

# Footer
show_footer()
