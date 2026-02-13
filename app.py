import streamlit as st
import pandas as pd
import joblib
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import streamlit_authenticator as stauth
import sqlite3
from datetime import datetime
import os

# --- 1. DATABASE & SESSION INITIALIZATION ---
def init_db():
    conn = sqlite3.connect('academic_data.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (username TEXT PRIMARY KEY, name TEXT, password TEXT, role TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS history 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, timestamp TEXT, 
                  score REAL, risk TEXT, study_h REAL, attendance REAL)''')
    conn.commit()
    conn.close()

init_db()

# --- 2. LAYOUT CONFIGURATION ---
st.set_page_config(page_title="EduPredict AI Pro", layout="wide")

st.markdown("""
    <style>
    .stMetric { border: 1px solid #e0e0e0; padding: 15px; border-radius: 10px; background-color: white; }
    .report-card { background-color: #ffffff; padding: 20px; border-radius: 15px; border-left: 5px solid #4A90E2; box-shadow: 2px 2px 10px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- 3. AUTHENTICATION PREP ---
def get_auth_config():
    conn = sqlite3.connect('academic_data.db')
    df = pd.read_sql_query("SELECT * FROM users", conn)
    conn.close()
    
    credentials = {'usernames': {}}
    for _, row in df.iterrows():
        credentials['usernames'][row['username']] = {
            'name': row['name'], 
            'password': row['password']
        }
    return credentials

credentials = get_auth_config()

# Initialize the Authenticator
authenticator = stauth.Authenticate(
    credentials,
    "student_pro_cookie",
    "auth_key_secure_123",
    cookie_expiry_days=30
)

# --- 4. SIDEBAR NAVIGATION ---
st.sidebar.title("🎓 EduPredict AI")
menu = st.sidebar.radio("Navigation", ["Login", "Register Account"])

if menu == "Register Account":
    st.title("📝 Staff Registration")
    with st.form("signup_form"):
        new_name = st.text_input("Full Name")
        new_user = st.text_input("Username")
        new_pw = st.text_input("Password", type="password")
        role = st.selectbox("Role", ["Teacher", "Counselor", "Parent"])
        submit = st.form_submit_button("Create Account")
        
        if submit:
            if new_user and new_pw:
                # FIXED: Using the most compatible hashing method for v0.3+
                hashed_pw = stauth.Hasher.hash(new_pw)
                try:
                    conn = sqlite3.connect('academic_data.db')
                    c = conn.cursor()
                    c.execute("INSERT INTO users VALUES (?,?,?,?)", (new_user, new_name, hashed_pw, role))
                    conn.commit()
                    st.success("Account created! Please switch to 'Login' in the sidebar.")
                    # Update credentials in memory immediately
                    credentials['usernames'][new_user] = {'name': new_name, 'password': hashed_pw}
                except sqlite3.IntegrityError:
                    st.error("Username already exists. Please choose a different one.")
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.warning("Please fill in all fields.")

elif menu == "Login":
    # Handles session state automatically
    authenticator.login(location='main')

    if st.session_state["authentication_status"]:
        # --- SUCCESSFUL LOGIN: DASHBOARD START ---
        @st.cache_resource
        def load_assets():
            return joblib.load('student_model_v1.pkl')

        try:
            assets = load_assets()
            reg_model, class_model, scaler = assets['regressor'], assets['classifier'], assets['scaler']
            le_risk, le_gender, le_parent = assets['le_risk'], assets['le_gender'], assets['le_parent']
        except:
            st.error("Model assets not found. Ensure 'student_model_v1.pkl' is present.")
            st.stop()

        st.sidebar.success(f"Welcome, {st.session_state['name']}")
        authenticator.logout("Logout", "sidebar")

        st.title("🔬 Academic Diagnostic Dashboard")
        
        tab1, tab2 = st.tabs(["🎯 Prediction Tool", "📜 Analytics History"])

        with tab1:
            col_in, col_out = st.columns([1, 2])
            
            with col_in:
                st.subheader("📋 Student Data")
                gender = st.selectbox("Gender", le_gender.classes_)
                parent_edu = st.selectbox("Parent Education", le_parent.classes_)
                attendance = st.slider("Attendance %", 0, 100, 85)
                study_h = st.slider("Study Hours", 0.0, 15.0, 5.0)
                social_h = st.slider("Social Media", 0.0, 12.0, 2.0)
                sleep_h = st.slider("Sleep Duration", 4.0, 10.0, 7.0)
                deadlines = st.selectbox("Missed Deadlines", [0, 1, 2, 3, 4])
                
                # Inference Logic
                g_enc = le_gender.transform([gender])[0]
                p_enc = le_parent.transform([parent_edu])[0]
                feat_df = pd.DataFrame({'G':[g_enc],'P':[p_enc],'St':[study_h],'So':[social_h],'Sl':[sleep_h],'At':[attendance],'D':[deadlines]})
                X_sc = scaler.transform(feat_df.values)
                
                p_grade = reg_model.predict(X_sc)[0]
                p_risk = le_risk.classes_[np.argmax(class_model.predict_proba(X_sc)[0])]

                if st.button("💾 Save to Database"):
                    conn = sqlite3.connect('academic_data.db')
                    c = conn.cursor()
                    c.execute("INSERT INTO history (username, timestamp, score, risk, study_h, attendance) VALUES (?,?,?,?,?,?)",
                              (st.session_state["username"], datetime.now().strftime("%Y-%m-%d %H:%M"), p_grade, p_risk, study_h, attendance))
                    conn.commit()
                    st.toast("Record successfully saved!")

            with col_out:
                m1, m2, m3 = st.columns(3)
                m1.metric("Predicted Score", f"{p_grade:.1f}%")
                m2.metric("Risk Status", p_risk)
                m3.metric("Digital Balance", f"{(study_h/(social_h+0.5)):.1f}x")

                
                vals = [study_h/12, attendance/100, sleep_h/10, (12-social_h)/12, (5-deadlines)/5]
                cats = ['Study', 'Attendance', 'Sleep', 'Digital Ctrl', 'Deadlines']
                fig_radar = go.Figure(data=go.Scatterpolar(r=vals, theta=cats, fill='toself'))
                fig_radar.update_layout(polar=dict(radialaxis=dict(visible=False, range=[0, 1])), height=350)
                st.plotly_chart(fig_radar, use_container_width=True)

            st.divider()

            # --- WHAT-IF SIMULATOR ---
            st.subheader("🧪 Prescriptive Simulation")
            sc1, sc2 = st.columns(2)
            with sc1:
                st.write("What if the student changes their habits?")
                add_st = st.slider("Additional Study (Hrs)", 0, 5, 1)
                add_at = st.slider("Attendance Boost (%)", 0, 20, 5)
            
            with sc2:
                sim_feat = feat_df.copy()
                sim_feat.iloc[0, 2] += add_st
                sim_feat.iloc[0, 5] = min(100, sim_feat.iloc[0, 5] + add_at)
                sim_res = reg_model.predict(scaler.transform(sim_feat.values))[0]
                st.metric("New Predicted Outcome", f"{sim_res:.1f}%", delta=f"{sim_res - p_grade:.1f}% Improvement")
                st.progress(min(sim_res/100, 1.0))

        with tab2:
            st.subheader("📊 Institutional Trends")
            conn = sqlite3.connect('academic_data.db')
            h_df = pd.read_sql_query(f"SELECT timestamp, score, risk, study_h FROM history WHERE username='{st.session_state['username']}'", conn)
            if not h_df.empty:
                st.dataframe(h_df, use_container_width=True)
                fig_line = px.line(h_df, x='timestamp', y='score', markers=True, title="Performance Log")
                st.plotly_chart(fig_line, use_container_width=True)
            else:
                st.info("No records found in the database for this account.")

    elif st.session_state["authentication_status"] is False:
        st.error("Username/password is incorrect")
    elif st.session_state["authentication_status"] is None:
        st.info("Please login or register to access the student AI diagnostic system.")

st.sidebar.caption("v4.2 | Secured SQLite | Advanced Analytics")