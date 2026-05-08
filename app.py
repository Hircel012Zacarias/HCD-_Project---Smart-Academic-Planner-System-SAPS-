from datetime import datetime, date
import streamlit as st
import pickle
import numpy as np
import pandas as pd
import os

# LOAD MODEL
model = pickle.load(open("model.pkl", "rb"))

# PAGE CONFIG
st.set_page_config(page_title="Student AI Advisor", layout="centered")

# TITLE
st.title("🎓 Student Academic Planner System")
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

    # EMAIL SIMULATION
    st.subheader("📧 Reminder System")

    email = st.text_input("Enter Email")

    if st.button("Save Email"):
        st.session_state.email = email
        st.success("Email saved!")

    if st.button("Send Reminder"):
        if "email" in st.session_state:
            st.success(f"Reminder sent to {st.session_state.email} for {selected_task}")
            st.toast("Notification sent!")
        else:
            st.warning("Save email first")

else:
    st.info("No tasks added yet")