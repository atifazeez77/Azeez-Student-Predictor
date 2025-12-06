import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# --- Page Configuration ---
st.set_page_config(page_title="Azeez Edu-Predictor", page_icon="📚")

# --- FUNCTION: Save to Google Sheet ---
def save_to_sheet(name, phone, score):
    try:
        # Define the scope (permissions)
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        
        # Load credentials from Streamlit Secrets (Cloud)
        creds_dict = st.secrets["gcp_service_account"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        
        client = gspread.authorize(creds)
        
        # Open the sheet
        sheet = client.open("Azeez_Leads").sheet1
        
        # Get current date
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Append row
        sheet.append_row([name, phone, str(score), current_time])
        return True
    except Exception as e:
        st.error(f"Database Error: {e}")
        return False

# --- Title ---
st.title("🚀 Azeez Horizon: Student Success Predictor")

# --- ML Setup (Same as before) ---
data = {
    'Study_Hours': [2, 4, 6, 8, 10, 3, 5, 7, 9, 1],
    'Prev_Marks': [50, 60, 75, 85, 95, 55, 70, 80, 90, 45],
    'Sleep_Hours': [9, 8, 7, 7, 8, 8, 7, 6, 8, 10],
    'Final_Score': [55, 65, 82, 88, 98, 58, 72, 85, 93, 48]
}
df = pd.DataFrame(data)
X = df[['Study_Hours', 'Prev_Marks', 'Sleep_Hours']]
y = df['Final_Score']
model = LinearRegression()
model.fit(X, y)

# --- Sidebar Inputs ---
st.sidebar.header("Student Details")
name = st.sidebar.text_input("Enter Student Name")
hours = st.sidebar.slider("Daily Self Study (Hours)", 0, 12, 4)
prev = st.sidebar.number_input("Last Class Percentage", 0, 100, 60)
sleep = st.sidebar.slider("Daily Sleep (Hours)", 4, 12, 7)

# --- Main Logic ---
if st.button("Predict Score 🔮"):
    if name:
        with st.spinner("AI is calculating..."):
            time.sleep(1)
            user_data = np.array([[hours, prev, sleep]])
            prediction = model.predict(user_data)[0]
            final_score = round(prediction, 2)
            if final_score > 100: final_score = 99.9

            st.markdown("---")
            st.subheader(f"Hello {name}, your predicted score is:")
            st.metric(label="Expected Percentage", value=f"{final_score}%")
            
            # --- Save the score in session state so we can use it in the form below ---
            st.session_state['last_score'] = final_score
            st.session_state['last_name'] = name

            # --- Advice ---
            if final_score > 90:
                st.success("Great Job! Keep it up.")
            elif final_score < 60:
                st.error("Critical! You need immediate guidance.")

    else:
        st.warning("Please enter your name first!")

# --- CONTACT FORM (Lead Generation) ---
# This section appears if a score has been calculated
if 'last_score' in st.session_state:
    st.markdown("---")
    st.subheader("📞 Need Help Improving This Score?")
    st.write("Join **Azeez Classes** for a personalized study plan.")
    
    with st.form("contact_form"):
        st.write(f"Student: **{st.session_state['last_name']}** | Score: **{st.session_state['last_score']}%**")
        phone = st.text_input("Enter Parent's Phone Number", placeholder="9876543210")
        
        submitted = st.form_submit_button("Request Call Back")
        
        if submitted:
            if len(phone) == 10:
                with st.spinner("Saving details..."):
                    success = save_to_sheet(st.session_state['last_name'], phone, st.session_state['last_score'])
                    if success:
                        st.balloons()
                        st.success("Details sent to Azeez Sir! We will call you shortly.")
            else:
                st.warning("Please enter a valid 10-digit number.")

st.markdown("---")
st.caption("Azeez Library & Classes Project")