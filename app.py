from datetime import datetime, date
import streamlit as st
import pickle
import numpy as np
import pandas as pd
import os
import smtplib
from email.mime.text import MIMEText

# LOGIN SYSTEM 
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

        # 🔍 DEBUG (TEMPORARY - REMOVE AFTER TEST)
        st.write("EMAIL:", sender_email)
        st.write("PASS LENGTH:", len(app_password))

        server.login(sender_email, app_password)
        server.sendmail(sender_email, user_email, msg.as_string())
        server.quit()

        return True

    except Exception as e:
        st.error(f"Email error: {e}")
        return False


#LOGIN PAGE 
if not st.session_state.logged_in:

    st.title("🔐 Smart Academic Planner System (SAPS) Login")

    username = st.text_input("Username or email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username and password:
            st.session_state.logged_in = True
            st.session_state.user = username
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Enter username and password")

    st.stop()

#APP START
st.set_page_config(page_title="SAPS System", layout="centered")

st.title(f"📚 SAPS Dashboard - {st.session_state.user}")

user = st.session_state.user

#MODEL 
model_path = os.path.join(os.path.dirname(__file__), "model.pkl")
model = pickle.load(open(model_path, "rb"))

#INPUTS 
study_hours = st.slider("Study Hours per Day", 0, 12, 3)
sleep_hours = st.slider("Sleep Hours per Night", 0, 12, 6)
attendance = st.slider("Attendance (%)", 0, 100, 75)
screen_time = st.slider("Screen Time (hours/day)", 0, 12, 4)
extracurricular = st.slider("Extracurricular (hours/week)", 0, 10, 2)
previous_score = st.slider("Previous SGPA", 0, 10, 6)

#TASKS PER USER
if user not in st.session_state.tasks:
    st.session_state.tasks[user] = []

FILE = "tasks.csv"

#ADD TASK 
st.header("📅 Academic Smart Planner")

task_name = st.text_input("Task Name")
task_date = st.date_input("Select Date", value=date.today())
priority = st.selectbox("Priority", ["High", "Medium", "Low"])

if st.button("➕ Add Task"):
    if task_name.strip():
        st.session_state.tasks[user].append({
            "Task": task_name,
            "Date": task_date,
            "Priority": priority,
            "Status": "Pending"
        })
        pd.DataFrame(st.session_state.tasks[user]).to_csv(FILE, index=False)
        st.success("Task added!")
    else:
        st.error("Enter task name")

#DISPLAY TASKS
today = datetime.today().date()

if len(st.session_state.tasks[user]) > 0:

    df = pd.DataFrame(st.session_state.tasks[user])
    df = df.sort_values(by=["Date"])

    st.subheader("📋 Your Tasks")
    st.dataframe(df, use_container_width=True)

    selected_task = st.selectbox("Select Task", df["Task"])

    # COMPLETE TASK
    if st.button("✅ Complete Task"):
        for t in st.session_state.tasks[user]:
            if t["Task"] == selected_task:
                t["Status"] = "Done"
        st.success("Task completed!")

    # DELETE TASK
    if st.button("🗑 Delete Task"):
        st.session_state.tasks[user] = [
            t for t in st.session_state.tasks[user]
            if t["Task"] != selected_task
        ]
        st.warning("Task deleted!")

#ALERTS
st.subheader("🚨 Smart Alerts")

for task in st.session_state.tasks[user]:
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

#EMAIL ----------------
st.divider()
st.subheader("📧 Reminder System")

email = st.text_input("Enter your email")
if "user_email" not in st.session_state:
    st.session_state.user_email = ""

if st.button("Save Email"):
    st.session_state.user_email = email
    st.success("Email saved!")

if st.button("Send Reminder"):

    if st.session_state.user_email == "":
        st.warning("Save email first")

    elif not st.session_state.tasks[user]:
        st.warning("No tasks found")

    else:
        selected_row = df[df["Task"] == selected_task].iloc[0]

        days_left = (pd.to_datetime(selected_row["Date"]).date() - today).days

        success = send_email(
            st.session_state.user_email,
            selected_task,
            days_left
        )

        if success:
            st.success("Email sent!")
        else:
            st.error("Failed to send email")