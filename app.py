from datetime import datetime, date
import streamlit as st
import pickle
import numpy as np
import pandas as pd
import os

import smtplib
from email.mime.text import MIMEText

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

Stay productive!

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
# LOAD MODEL
model_path = os.path.join(os.path.dirname(__file__), "model.pkl")
model = pickle.load(open(model_path, "rb"))

# PAGE CONFIG
st.set_page_config(page_title="Student AI Advisor", layout="centered")

# TITLE
st.title("Student Academic Planner System")
st.write("Predict your academic performance and get personalized improvement insights")

# INPUTS
study_hours = st.slider("Study Hours per Day", 0.0, 12.0, 3.0)
sleep_hours = st.slider("Sleep Hours per Night", 0.0, 12.0, 6.0)
attendance = st.slider("Attendance (%)", 0.0, 100.0, 75.0)
screen_time = st.slider("Screen Time (hours/day)", 0.0, 12.0, 4.0)
extracurricular = st.slider("Extracurricular Activities (hours/week)", 0.0, 10.0, 2.0)

# SGPA
previous_score = st.slider("Previous SGPA", 0.0, 10.0, 6.0)

# INPUT SUMMARY
st.subheader("Your Input Summary")
st.write({
    "Study Hours": study_hours,
    "Sleep Hours": sleep_hours,
    "Attendance": attendance,
    "Screen Time": screen_time,
    "Extracurricular": extracurricular,
    "Previous SGPA": previous_score
})

# SMART RECOMMENDATIONS (always active)
st.subheader("Smart Recommendations")

if study_hours < 3:
    st.warning("Increase study hours")

if sleep_hours < 6:
    st.warning("Sleep more (7–8 hours recommended)")

if screen_time > 6:
    st.warning("Reduce screen time")

if attendance < 70:
    st.warning("Improve attendance")

# PREDICTION
if st.button("Predict Performance"):

    data = np.array([[study_hours, sleep_hours, attendance, screen_time, extracurricular]])
    pred = model.predict(data)[0]

    pred_sgpa = max(0, min(10, pred / 10))

    st.subheader(f"Predicted SGPA: {pred_sgpa:.2f}")
    st.progress(int(pred))

    # Performance level
    if pred > 80:
        st.success("Excellent Performance")
    elif pred > 60:
        st.warning("Moderate Performance")
    else:
        st.error("Low Performance")

    # Comparison
    st.subheader("Performance Comparison")

    if pred_sgpa > previous_score:
        st.success("You are improving compared to last semester!")
    elif pred_sgpa == previous_score:
        st.info("Your performance is stable.")
    else:
        st.warning("Your performance is below your previous results")

# PERSONAL INSIGHT
st.subheader("Personal Insight")

if study_hours > 7 and sleep_hours < 5:
    st.info("You study a lot but lack sleep — reduces efficiency")
elif screen_time > study_hours:
    st.info("You spend more time on screens than studying")
else:
    st.info("Your lifestyle is relatively balanced")

# IMPACT
st.subheader("What Influences Your Score")
st.write("""
- Study hours → strong positive impact  
- Attendance → very strong positive impact  
- Sleep → moderate positive impact  
- Screen time → negative impact  
- Extracurricular → slight positive impact  
""")

# PLAN
if st.checkbox("📅 Show Improvement Plan"):
    st.subheader("Your Suggested Plan")
    st.write("✔ Study 5–7 hours daily")
    st.write("✔ Sleep at least 7 hours")
    st.write("✔ Keep attendance above 80%")
    st.write("✔ Limit screen time to 3–4 hours")
    st.write("✔ Engage in extracurricular activities")
    
# TASK PLANNER
st.divider()
st.header("📅 Academic Smart Planner")

FILE = "tasks.csv"

# LOAD TASKS
if os.path.exists(FILE):
    df_saved = pd.read_csv(FILE)
    st.session_state.tasks = df_saved.to_dict("records")
else:
    if "tasks" not in st.session_state:
        st.session_state.tasks = []

# INPUTS
task_name = st.text_input("Task Name")
task_date = st.date_input("Select Date", value=date.today())
priority = st.selectbox("Priority", ["High", "Medium", "Low"])

# ADD TASK
if st.button("➕ Add Task"):
    if task_name.strip() != "":
        st.session_state.tasks.append({
            "Task": task_name,
            "Date": task_date,
            "Priority": priority,
            "Status": "Pending"
        })
        pd.DataFrame(st.session_state.tasks).to_csv(FILE, index=False)
        st.success("Task added!")
    else:
        st.error("Enter task name")

# ALERTS
today = datetime.today().date()

if len(st.session_state.tasks) > 0:

    st.subheader("🚨 Smart Alerts")

    for task in st.session_state.tasks:
        days_left = (pd.to_datetime(task["Date"]).date() - today).days

        if task["Status"] == "Pending":
            if days_left < 0:
                st.error(f"😔OVERDUE: {task['Task']}")
            elif days_left == 0:
                st.error(f"😃TODAY: {task['Task']}")
                st.toast(f"Task TODAY: {task['Task']}")
            elif days_left <= 3:
                st.warning(f" {task['Task']} due in {days_left} days")
            elif days_left <= 7:
                st.info(f"Upcoming: {task['Task']} in {days_left} days")

# DISPLAY
if len(st.session_state.tasks) > 0:

    df = pd.DataFrame(st.session_state.tasks)
    df = df.sort_values(by=["Date"])

    st.subheader("📋 Your Tasks")
    st.dataframe(df, use_container_width=True)

    selected_task = st.selectbox("Select Task", df["Task"])

    # COMPLETE
    if st.button("✅ Complete Task"):
        for task in st.session_state.tasks:
            if task["Task"] == selected_task:
                task["Status"] = "Done"
        pd.DataFrame(st.session_state.tasks).to_csv(FILE, index=False)
        st.success("Task completed!")

    # DELETE
    if st.button("🗑 Delete Task"):
        st.session_state.tasks = [t for t in st.session_state.tasks if t["Task"] != selected_task]
        pd.DataFrame(st.session_state.tasks).to_csv(FILE, index=False)
        st.warning("Task deleted!")

    # EMAIL SECTION
st.subheader("📧 Reminder System")

email = st.text_input("Enter your email")

if "user_email" not in st.session_state:
    st.session_state.user_email = ""

if st.button("Save Email"):
    if email.strip() == "":
        st.warning("Please enter email first")
    else:
        st.session_state.user_email = email
        st.success("Email saved!")
    # SEND REMINDER
if st.button("Send Reminder"):

    if st.session_state.user_email == "":
        st.warning("Please save email first")

    else:
        selected_row = df[df["Task"] == selected_task].iloc[0]

        days_left = (pd.to_datetime(selected_row["Date"]).date() - today).days

        success = send_email(
            st.session_state.user_email,
            selected_task,
            days_left
        )

        if success:
            st.success("Email sent successfully!")
            st.toast("Reminder sent!")
        else:
            st.error("Failed to send email")