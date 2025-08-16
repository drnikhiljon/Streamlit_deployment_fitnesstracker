# backend/database.py

import psycopg2
import os
import datetime
import streamlit as st # Streamlit is used here to display messages

def get_db_connection():
    """Establishes and returns a database connection using environment variables."""
    conn = psycopg2.connect(
        host=os.environ.get("DB_HOST"),
        database=os.environ.get("DB_NAME"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD"),
        port=os.environ.get("DB_PORT", 5432)
    )
    return conn

def create_user(username):
    """Creates a new user in the database and returns their ID."""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO users (username) VALUES (%s) RETURNING user_id;", (username,))
        user_id = cur.fetchone()[0]
        conn.commit()
        return user_id
    except psycopg2.errors.UniqueViolation:
        st.error(f"Username '{username}' already exists. Please choose a different one.")
        return None
    finally:
        cur.close()
        conn.close()

def get_user_id(username):
    """Retrieves the user ID for a given username."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM users WHERE username = %s;", (username,))
    user_id = cur.fetchone()
    cur.close()
    conn.close()
    return user_id[0] if user_id else None

def log_exercise(user_id, exercise_date, duration):
    """Logs a new exercise entry for a user."""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO exercise_logs (user_id, exercise_date, duration_minutes) VALUES (%s, %s, %s);",
            (user_id, exercise_date, duration)
        )
        conn.commit()
        st.success(f"Successfully logged {duration} minutes of exercise on {exercise_date}.")
    except psycopg2.errors.UniqueViolation:
        st.error("You have already logged exercise for this date. Please update or delete the existing entry.")
    finally:
        cur.close()
        conn.close()

def get_weekly_report(user_id):
    """Generates a weekly report of exercise duration for a user."""
    conn = get_db_connection()
    cur = conn.cursor()
    today = datetime.date.today()
    
    # Calculate the start of the current week (Sunday)
    start_of_week = today - datetime.timedelta(days=today.weekday() + 1)
    
    cur.execute(
        "SELECT exercise_date, duration_minutes FROM exercise_logs WHERE user_id = %s AND exercise_date >= %s ORDER BY exercise_date;",
        (user_id, start_of_week)
    )
    results = cur.fetchall()
    cur.close()
    conn.close()
    return results