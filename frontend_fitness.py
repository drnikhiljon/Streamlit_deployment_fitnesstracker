# frontend/app.py

import streamlit as st
import datetime
from backend_fitness import create_user, get_user_id, log_exercise, get_weekly_report

# --- Streamlit UI ---

st.set_page_config(page_title="Fitness Tracker", page_icon="💪")
st.title("💪 Simple Fitness Tracker")

# User login/creation
with st.sidebar:
    st.header("User Access")
    username = st.text_input("Enter your username")
    if st.button("Log In / Create Account"):
        if username:
            user_id = get_user_id(username)
            if not user_id:
                user_id = create_user(username)
                if user_id:
                    st.success(f"Welcome, new user: {username}!")
            st.session_state['user_id'] = user_id
            st.session_state['username'] = username
        else:
            st.error("Please enter a username.")

if 'user_id' not in st.session_state:
    st.info("Please log in or create an account from the sidebar to continue.")
else:
    st.header(f"Welcome, {st.session_state['username']}!")

    # Tabbed interface for different functionalities
    tab1, tab2 = st.tabs(["Log Exercise", "View Weekly Progress"])
    
    with tab1:
        st.subheader("Log Your Exercise")
        with st.form(key='exercise_form'):
            exercise_date = st.date_input("Date of exercise", value=datetime.date.today())
            duration = st.number_input("Duration (minutes)", min_value=1, step=1)
            submit_button = st.form_submit_button(label='Log Exercise')

            if submit_button:
                log_exercise(st.session_state['user_id'], exercise_date, duration)
    
    with tab2:
        st.subheader("Your Weekly Progress")
        report_data = get_weekly_report(st.session_state['user_id'])
        
        if report_data:
            total_duration = sum(row[1] for row in report_data)
            st.metric("Total Exercise This Week (minutes)", total_duration)

            st.write("---")
            st.subheader("Exercise Log")
            for date, duration in report_data:
                st.write(f"**Date:** {date.strftime('%A, %B %d')}")
                st.write(f"**Duration:** {duration} minutes")
                st.write("")
        else:
            st.info("No exercise logged for the current week yet.")