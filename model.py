import pickle

print("STUDENT PERFORMANCE PREDICTOR")

# Load model
model = pickle.load(open("model.pkl", "rb"))

try:
    study = float(input("Study hours: "))
    sleep = float(input("Sleep hours: "))
    attendance = float(input("Attendance (%): "))
    screen = float(input("Screen time: "))
    extra = float(input("Extracurricular hours: "))

    # Prediction
    result = model.predict([[study, sleep, attendance, screen, extra]])
    value = result[0]

    print("\nPredicted Performance:", round(value, 2))

    # Classification
    if value < 50:
        print("Low Performance")
    elif value < 75:
        print("Average Performance")
    else:
        print("High Performance")

except ValueError:
    print("Invalid input. Please enter numeric values.")