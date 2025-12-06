import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import time

# --- Page Configuration ---
st.set_page_config(page_title="Azeez Edu-Predictor", page_icon="📚")

# --- Title and Branding ---
st.title("🚀 Azeez Horizon: Student Success Predictor")
st.write("Welcome to **Azeez Library & Classes**. Let's use AI to check your exam readiness!")

# --- 1. CREATE DUMMY DATA (To train our ML Model instantly) ---
# In a real project, you would load this from a CSV file.
# Data: [Study Hours, Previous Marks, Sleep Hours]
data = {
    'Study_Hours': [2, 4, 6, 8, 10, 3, 5, 7, 9, 1],
    'Prev_Marks': [50, 60, 75, 85, 95, 55, 70, 80, 90, 45],
    'Sleep_Hours': [9, 8, 7, 7, 8, 8, 7, 6, 8, 10],
    'Final_Score': [55, 65, 82, 88, 98, 58, 72, 85, 93, 48] # The Target
}

df = pd.DataFrame(data)

# --- 2. TRAIN THE MACHINE LEARNING MODEL ---
# Features (Inputs) -> X, Target (Output) -> y
X = df[['Study_Hours', 'Prev_Marks', 'Sleep_Hours']]
y = df['Final_Score']

model = LinearRegression()
model.fit(X, y) # The robot is learning here!

# --- 3. USER INPUT (Sidebar) ---
st.sidebar.header("Student Details")
name = st.sidebar.text_input("Enter Student Name")
hours = st.sidebar.slider("Daily Self Study (Hours)", 0, 12, 4)
prev = st.sidebar.number_input("Last Class Percentage", 0, 100, 60)
sleep = st.sidebar.slider("Daily Sleep (Hours)", 4, 12, 7)

# --- 4. PREDICTION LOGIC ---
if st.button("Predict Score 🔮"):
    if name:
        with st.spinner("AI is calculating..."):
            time.sleep(1) # Fake loading effect
            
            # Make prediction
            user_data = np.array([[hours, prev, sleep]])
            prediction = model.predict(user_data)[0]
            final_score = round(prediction, 2)
            
            # Cap the score at 100
            if final_score > 100: final_score = 99.9

            st.markdown("---")
            st.subheader(f"Hello {name}, your predicted score is:")
            st.metric(label="Expected Percentage", value=f"{final_score}%")

            # --- 5. ADVICE IN HINGLISH ---
            st.subheader("💡 Azeez Sir's Advice:")
            
            if final_score > 90:
                st.success("Great Job! Aapki preparation solid hai. Bas overconfidence me mat aana, revision karte raho!")
            elif final_score > 75:
                st.info("Good going! Aap thoda aur effort daaloge to 90+ pakka hai. Focus on weak topics.")
            elif final_score > 50:
                st.warning("Warning! Aapko study hours badhane honge. Library join karlo aur phone kam use karo.")
            else:
                st.error("Critical Condition! Parents ko leke aao. We need to make a strict plan immediately.")
                
    else:
        st.warning("Please enter your name first!")

# --- Footer ---
st.markdown("---")
st.caption("Developed by Er. Atif Azeez | Powered by Python & ML")