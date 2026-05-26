import pandas as pd
import pickle
from sklearn.linear_model import LogisticRegression

data = pd.read_csv("students.csv")

X = data[['Study_Hours', 'Attendance', 'Previous_Marks', 'Assignments', 'Internal_Marks']]
y = data['Final_Result']

model = LogisticRegression()
model.fit(X, y)

pickle.dump(model, open("model.pkl", "wb"))

print("Model trained successfully!")