import streamlit as st
import sqlite3
import os

# Page configuration
st.set_page_config(
    page_title="Login - Manufacturing Dashboard",
    page_icon="🔐",
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

# Check if user is already logged in
if 'user' in st.session_state and st.session_state.user:
    st.success(f"✅ Already logged in as **{st.session_state.user['username']}** ({st.session_state.user['role_name'].title()})")
    st.info("👉 Navigate to **Dashboard** or **Database Browser** using the sidebar")
    
    if st.button("🚪 Logout"):
        st.session_state.user = None
        st.session_state.user_role = None
        st.rerun()
    
    show_footer()
    st.stop()

# Login page content
st.markdown("")
st.markdown("")
st.markdown("")

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown("""
    <div style="text-align: center;">
        <h1>🔐 User Login</h1>
        <p style="color: #718096; margin-bottom: 2rem;">Enter your details to login or register</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get roles from database
    try:
        db_path = os.path.join(os.path.dirname(__file__), "../../sql/manufacturing.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Fetch available roles
        cursor.execute("""
            SELECT role_id, role_name, description
            FROM roles
            ORDER BY role_id
        """)
        roles = cursor.fetchall()
        conn.close()
        
        # Create role options
        role_options = {}
        for role_id, role_name, description in roles:
            display_text = f"{role_name.title()}"
            if description:
                display_text += f" - {description}"
            role_options[display_text] = (role_id, role_name)
        
        # Login form
        with st.form("login_form"):
            st.markdown("### Enter Your Information")
            
            username = st.text_input(
                "Username *",
                placeholder="Enter your username",
                help="Required: Your username for identification"
            )
            
            email = st.text_input(
                "Email (Optional)",
                placeholder="your.email@company.com",
                help="Optional: Your email address"
            )
            
            selected_role = st.selectbox(
                "Select Role *",
                options=list(role_options.keys()),
                help="Required: Choose your role in the organization"
            )
            
            st.markdown("")
            submit_button = st.form_submit_button("Login / Register →", use_container_width=True, type="primary")
        
        if submit_button:
            # Validate username
            if not username or username.strip() == "":
                st.error("❌ Username is required!")
            else:
                username = username.strip()
                email = email.strip() if email else None
                role_id, role_name = role_options[selected_role]
                
                try:
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()
                    
                    # Check if user with same username and role already exists
                    cursor.execute("""
                        SELECT user_id, username, email, role_id
                        FROM users
                        WHERE username = ? AND role_id = ?
                    """, (username, role_id))
                    existing_user = cursor.fetchone()
                    
                    if existing_user:
                        # User exists - just log in
                        user_id, db_username, db_email, db_role_id = existing_user
                        st.session_state.user = {
                            'user_id': user_id,
                            'username': db_username,
                            'email': db_email,
                            'role_id': db_role_id,
                            'role_name': role_name
                        }
                        st.session_state.user_role = role_name
                        st.success(f"✅ Welcome back, **{db_username}**!")
                        st.info("👉 Navigate to **Dashboard** or **Database Browser** using the sidebar")
                        conn.close()
                        st.rerun()
                    else:
                        # New user - create account
                        cursor.execute("""
                            INSERT INTO users (username, email, role_id)
                            VALUES (?, ?, ?)
                        """, (username, email, role_id))
                        conn.commit()
                        
                        # Get the newly created user
                        new_user_id = cursor.lastrowid
                        st.session_state.user = {
                            'user_id': new_user_id,
                            'username': username,
                            'email': email,
                            'role_id': role_id,
                            'role_name': role_name
                        }
                        st.session_state.user_role = role_name
                        conn.close()
                        
                        st.success(f"✅ Account created! Welcome, **{username}**!")
                        st.info("👉 Navigate to **Dashboard** or **Database Browser** using the sidebar")
                        st.rerun()
                        
                except sqlite3.IntegrityError as e:
                    st.error(f"❌ Username already exists with a different role. Please choose a different username or select the correct role.")
                    conn.close()
                except sqlite3.Error as e:
                    st.error(f"❌ Database error: {e}")
                    conn.close()
        
        st.markdown("")
        st.info("ℹ️ **Note:** If your username and role combination exists, you'll be logged in. Otherwise, a new account will be created.")
                
    except sqlite3.Error as e:
        st.error(f"❌ Database connection error: {e}")
        st.warning("Please ensure the database is initialized. Run `database/init_db.py` and `database/seed_data.py` first.")

# Footer
show_footer()
