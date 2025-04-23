import streamlit as st
from firebase_config import auth, db
import datetime

# Page config
st.set_page_config(page_title="LoopList", page_icon="🔁", layout="centered")

# CSS Styling
st.markdown(
    """
    <style>
        .stTextInput>div>div>input {
            background-color: #f2f2f2;
            padding: 10px;
            border-radius: 10px;
            color: black !important;
            caret-color: black !important;  /* Added this line to change cursor color */
        }
        .stButton>button {
            background-color: #6c63ff;
            color: white;
            border: none;
            padding: 8px 20px;
            border-radius: 10px;
            font-weight: 600;
        }
        .stButton>button:hover {
            background-color: #574b90;
            transition: 0.3s ease;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Session init
if 'user' not in st.session_state:
    st.session_state['user'] = None

# Auth UI
def login_ui():
    st.markdown("## 🔁 Welcome to LoopList")
    tab1, tab2 = st.tabs(["🔐 Login", "🆕 Register"])

    with tab1:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            try:
                if not email or not password:
                    st.error("Please enter both email and password.")
                    return

                with st.spinner('Logging in...'):
                    user = auth.sign_in_with_email_and_password(email, password)
                    
                    if user:
                        # Update session state
                        st.session_state['user'] = user
                        st.session_state['user_email'] = email
                        st.session_state['login_time'] = str(datetime.datetime.now())
                        
                        # Update query params
                        st.query_params['login'] = 'success'
                        
                        # Show success message
                        st.success("Logged in successfully!")
                        
                        # Force a rerun to refresh the page
                        st.rerun()
            
            except Exception as e:
                error_message = str(e)
                print(f"Login error: {error_message}")  # Debug print
                
                if "INVALID_PASSWORD" in error_message:
                    st.error("Invalid password. Please try again.")
                elif "EMAIL_NOT_FOUND" in error_message:
                    st.error("Email not found. Please register first.")
                else:
                    st.error("Login failed. Please check your credentials and try again.")

    with tab2:
        email = st.text_input("New Email")
        password = st.text_input("New Password", type="password")
        if st.button("Register"):
            try:
                # Validate email format
                if not email or '@' not in email:
                    st.error("Please enter a valid email address.")
                    return
                
                # Validate password length
                if len(password) < 6:
                    st.error("Password must be at least 6 characters long.")
                    return
                
                auth.create_user_with_email_and_password(email, password)
                st.success("Registration successful! Please login.")
            except Exception as e:
                error_message = str(e)
                if "CONFIGURATION_NOT_FOUND" in error_message:
                    st.error("Firebase configuration error. Please check your setup.")
                elif "EMAIL_EXISTS" in error_message:
                    st.error("Email already exists. Please use a different email.")
                elif "INVALID_EMAIL" in error_message:
                    st.error("Invalid email format.")
                elif "WEAK_PASSWORD" in error_message:
                    st.error("Password is too weak. Use at least 6 characters.")
                else:
                    st.error(f"Account creation failed: {error_message}")

# Dashboard UI
def dashboard_ui():
    st.markdown("<h2 style='text-align: center;'>🌀 Your Task Loop</h2>", unsafe_allow_html=True)

    user_id = st.session_state['user']['localId']
    user_email = st.session_state['user_email']

    # Add task
    st.markdown("### ➕ Add a new task")
    with st.form("task_form", clear_on_submit=True):
        task = st.text_input("Task", placeholder="e.g., Finish project report 📝")
        submitted = st.form_submit_button("Add to Loop")
        if submitted and task:
            db.child("common_todos").push({
                "task": task,
                "user_id": user_id,
                "user_email": user_email,
                "timestamp": str(datetime.datetime.now())
            })
            st.rerun()

    # Task list
    st.markdown("---")
    st.markdown("### ✅ All Tasks")
    tasks = db.child("common_todos").get()
    if tasks.each():
        for t in tasks.each():
            with st.container():
                task_data = t.val()
                task_text = task_data['task']
                task_user = task_data['user_email']
                col1, col2, col3 = st.columns([8, 2, 1])
                with col1:
                    st.markdown(f"<div style='padding:10px 0;font-size:17px;'>• {task_text}</div>", unsafe_allow_html=True)
                with col2:
                    st.markdown(f"<div style='padding:10px 0;font-size:12px;color:gray;'>by {task_user}</div>", unsafe_allow_html=True)
                with col3:
                    if task_data['user_id'] == user_id:  # Only allow deletion of own tasks
                        if st.button("❌", key=t.key()):
                            db.child("common_todos").child(t.key()).remove()
                            st.rerun()
    else:
        st.info("No tasks yet. Add one above!")

    st.markdown("---")
    st.button("🚪 Logout", on_click=logout)

def logout():
    st.session_state['user'] = None

# App logic
if st.session_state['user']:
    dashboard_ui()
else:
    login_ui()