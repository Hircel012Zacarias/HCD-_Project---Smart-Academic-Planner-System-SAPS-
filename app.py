from datetime import datetime, date
import streamlit as st
import pickle
import numpy as np
import pandas as pd
import os
import smtplib
from email.mime.text import MIMEText


# INIT SESSION STATE
if "users" not in st.session_state:
    st.session_state.users = {} 

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = ""

if "tasks" not in st.session_state:
    st.session_state.tasks = {} 

# EMAIL FUNCTION
def send_email(user_email, task, days_left):

    sender_email = st.secrets["EMAIL"]
    app_password = st.secrets["PASSWORD"]

    subject = "📅 SAPS Smart Reminder"

    if days_left < 0:
        message = f"Your task '{task}' is OVERDUE. Please complete it immediately."
    elif days_left == 0:
        message = f"Your task '{task}' is due TODAY."
    elif days_left == 1:
        message = f"You have 1 day left to complete '{task}'."
    else:
        message = f"You have {days_left} days left to complete '{task}'."

    body = f"""
Hello Student,

This is a reminder from SAPS (Smart Academic Planner System).

{message}

- SAPS Team
"""

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = user_email

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, app_password)
        server.sendmail(sender_email, user_email, msg.as_string())
        server.quit()
        return True

    except Exception as e:
        st.error(f"Email error: {e}")
        return False

# AUTH SYSTEM (REGISTER + LOGIN)
st.title("📚 SAPS - Smart Academic Planner System")

menu = st.radio("Choose Option", ["Login", "Register"])

# REGISTER
if menu == "Register":

    new_user = st.text_input("Username")
    new_pass = st.text_input("Password", type="password")
    new_email = st.text_input("Email")

    if st.button("Register"):

        if new_user in st.session_state.users:
            st.error("User already exists")
        else:
            st.session_state.users[new_user] = {
                "password": new_pass,
                "email": new_email
            }
            st.success("Registered successfully!")

# LOGIN
elif menu == "Login":

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        if username in st.session_state.users and \
           st.session_state.users[username]["password"] == password:

            st.session_state.logged_in = True
            st.session_state.user = username

            if username not in st.session_state.tasks:
                st.session_state.tasks[username] = []

            st.success("Login successful!")
            st.rerun()

        else:
            st.error("Invalid credentials")

st.stop() if not st.session_state.logged_in else None

# DASHBOARD
user = st.session_state.user

st.title(f"📊 Welcome {user}")

# ensure task list exists
if user not in st.session_state.tasks:
    st.session_state.tasks[user] = []


# INPUTS 
study_hours = st.slider("Study Hours", 0, 12, 3)
sleep_hours = st.slider("Sleep Hours", 0, 12, 6)
attendance = st.slider("Attendance (%)", 0, 100, 75)
screen_time = st.slider("Screen Time", 0, 12, 4)
extracurricular = st.slider("Extracurricular", 0, 10, 2)


# TASK INPUT
st.header("📅 Tasks")

task_name = st.text_input("Task Name")
task_date = st.date_input("Date", value=date.today())
priority = st.selectbox("Priority", ["High", "Medium", "Low"])

if st.button("➕ Add Task"):

    if task_name.strip():

        st.session_state.tasks[user].append({
            "Task": task_name,
            "Date": task_date,
            "Priority": priority,
            "Status": "Pending"
        })

        st.success("Task added!")

    else:
        st.error("Enter task name")


# DISPLAY TASKS
today = datetime.today().date()

tasks = st.session_state.tasks[user]

if len(tasks) > 0:

    df = pd.DataFrame(tasks)
    df = df.sort_values(by="Date")

    st.subheader("📋 Your Tasks")
    st.dataframe(df, use_container_width=True)

    selected_task = st.selectbox("Select Task", df["Task"])

    if st.button("✅ Complete Task"):
        for t in tasks:
            if t["Task"] == selected_task:
                t["Status"] = "Done"
        st.success("Task completed!")

    if st.button("🗑 Delete Task"):
        st.session_state.tasks[user] = [
            t for t in tasks if t["Task"] != selected_task
        ]
        st.warning("Task deleted!")

# ALERTS
st.subheader("🚨 Smart Alerts")

for task in tasks:

    days_left = (pd.to_datetime(task["Date"]).date() - today).days

    if task["Status"] == "Pending":

        if days_left < 0:
            st.error(f"OVERDUE: {task['Task']}")
        elif days_left == 0:
            st.error(f"TODAY: {task['Task']}")
        elif days_left <= 3:
            st.warning(f"{task['Task']} due in {days_left} days")
        elif days_left <= 7:
            st.info(f"Upcoming: {task['Task']} in {days_left} days")

# EMAIL SYSTEM
st.divider()
st.subheader("📧 Reminder System")

user_email = st.session_state.users[user]["email"]

if st.button("Send Reminder"):

    if len(tasks) == 0:
        st.warning("No tasks found")

    else:
        selected_row = df[df["Task"] == selected_task].iloc[0]

        days_left = (pd.to_datetime(selected_row["Date"]).date() - today).days

        success = send_email(
            user_email,
            selected_task,
            days_left
        )

        if success:
            st.success("Email sent successfully!")
        else:
            st.error("Failed to send email")