import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from fpdf import FPDF

# --- CONFIGURATION & BRANDING ---
st.set_page_config(page_title="Azeez Horizon Hub", page_icon="🎓", layout="wide")

# Custom CSS for that "Premium EdTech" look
st.markdown("""
    <style>
    .main {background-color: #F5F5F5;}
    h1 {color: #2E86C1;}
    .stButton>button {background-color: #2E86C1; color: white; border-radius: 8px;}
    .stTabs [data-baseweb="tab-list"] {gap: 10px;}
    .stTabs [data-baseweb="tab"] {background-color: #FFFFFF; border-radius: 4px; padding: 10px 20px;}
    .stTabs [data-baseweb="tab"][aria-selected="true"] {background-color: #2E86C1; color: white;}
    </style>
    """, unsafe_allow_html=True)

# --- BACKEND: GOOGLE SHEETS (Keep your existing setup) ---
def save_to_sheet(name, phone, score, service_interest):
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        if "gcp_service_account" in st.secrets:
            creds_dict = st.secrets["gcp_service_account"]
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
            client = gspread.authorize(creds)
            sheet = client.open("Azeez_Leads").sheet1
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sheet.append_row([name, phone, str(score), service_interest, current_time])
            return True
        return False
    except:
        return False

# --- FEATURE: SMART PDF GENERATOR ---
def create_pro_pdf(name, score, hours, weak_subject, advice):
    pdf = FPDF()
    pdf.add_page()
    
    # 1. HEADER
    pdf.set_font("Arial", 'B', 20)
    pdf.set_text_color(46, 134, 193) # Brand Blue
    pdf.cell(0, 10, "Azeez Horizon: Student Success Report", 0, 1, 'C')
    pdf.line(10, 25, 200, 25)
    
    # 2. STUDENT DETAILS
    pdf.ln(20)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(100, 10, f"Student Name: {name}", 0, 0)
    pdf.cell(90, 10, f"Date: {datetime.now().strftime('%d-%b-%Y')}", 0, 1, 'R')
    
    # 3. SCORE & ADVICE
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 16)
    color = (0, 128, 0) if score > 70 else (255, 0, 0)
    pdf.set_text_color(*color)
    pdf.cell(0, 10, f"AI Predicted Score: {score}%", 0, 1, 'C')
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 8, txt=f"\nPersonalized Advice: {advice}\nFocus Area: You need to give 40% of your time to {weak_subject}.")
    
    # 4. BRANDING & SERVICES (The Marketing Part)
    pdf.ln(20)
    pdf.set_fill_color(240, 240, 240)
    pdf.rect(10, pdf.get_y(), 190, 110, 'F') # Light grey background box
    
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "  Our Premium Services (Azeez Horizon)", 0, 1)
    
    pdf.set_font("Arial", size=10)
    services_text = """
    1. Home Tuition (Class 1 to 10)
       - Qualified tutors | Result-oriented | Safe & reliable
       
    2. Online Educational Form Filling
       - Admission forms | Scholarships | Govt schemes | Exam forms
       
    3. Student Mentorship
       - Career guidance | Discipline | Mindset building | Study planning
       
    4. Azeez Library
       - Separate area for girls | Full-day study space | Silent & premium environment
       
    5. Azeez Classes (CBSE / ICSE)
       - Class 6 to 10 Coaching | Concept-based teaching | Personalized support
    """
    pdf.multi_cell(0, 7, services_text)
    
    pdf.set_y(-20)
    pdf.set_font("Arial", 'I', 8)
    pdf.cell(0, 10, "Visit Azeez Library & Classes for more details.", 0, 0, 'C')
    
    return pdf.output(dest='S').encode('latin-1')

# --- LOGIC: SCHEDULE MAKER ---
def make_schedule(hours, weak_sub):
    # Logic: 40% time to weak subject, rest divided
    slot_duration = 60 # minutes
    start_time = datetime.strptime("16:00", "%H:%M") # Start at 4 PM
    
    schedule_data = []
    
    # Add Weak Subject First
    weak_time = max(1, int(hours * 0.4))
    for i in range(weak_time):
        end_time = start_time + timedelta(minutes=60)
        schedule_data.append({
            "Time Slot": f"{start_time.strftime('%I:%M %p')} - {end_time.strftime('%I:%M %p')}",
            "Subject": f"{weak_sub} (Priority Focus)",
            "Activity": "Concept Reading & Notes"
        })
        start_time = end_time

    # Add Other Subjects
    remaining = int(hours - weak_time)
    subjects = ["Maths", "Science", "English", "SST"]
    subjects = [s for s in subjects if s != weak_sub] # Remove weak sub from list
    
    for i in range(remaining):
        sub = subjects[i % len(subjects)]
        end_time = start_time + timedelta(minutes=60)
        schedule_data.append({
            "Time Slot": f"{start_time.strftime('%I:%M %p')} - {end_time.strftime('%I:%M %p')}",
            "Subject": sub,
            "Activity": "Practice Questions / Homework"
        })
        start_time = end_time
        
    return pd.DataFrame(schedule_data)

# --- ML MODEL INIT ---
# (Using dummy data for instant start)
data = {'Study_Hours': [2, 4, 6, 8, 10, 3, 5, 7, 9, 12], 'Prev_Marks': [50, 60, 75, 85, 95, 55, 70, 80, 90, 98], 'Sleep_Hours': [9, 8, 7, 7, 8, 8, 7, 6, 8, 8], 'Final_Score': [55, 65, 82, 88, 98, 58, 72, 85, 93, 99]}
model = LinearRegression()
model.fit(pd.DataFrame(data)[['Study_Hours', 'Prev_Marks', 'Sleep_Hours']], pd.DataFrame(data)['Final_Score'])

# ================= UI STARTS HERE =================
st.title("🚀 Azeez Horizon: Student Hub")

# Create Tabs
tab1, tab2, tab3, tab4 = st.tabs(["🔮 Predict Score", "📅 My Schedule", "📚 Resources", "🏢 About Us"])

# --- TAB 1: PREDICTION ---
with tab1:
    st.subheader("Check your Exam Readiness")
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Student Name")
        prev = st.number_input("Last Class Percentage", 0, 100, 60)
        weak_sub = st.selectbox("Weakest Subject?", ["Maths", "Science", "SST", "English", "Hindi"])
    with col2:
        hours = st.slider("Daily Self Study (Hours)", 1, 12, 4)
        sleep = st.slider("Sleep Hours", 4, 12, 7)

    if st.button("Analyze & Generate Report", key="predict"):
        if name:
            # Prediction
            pred = model.predict([[hours, prev, sleep]])[0]
            final_score = min(99.9, max(0, round(pred, 1)))
            
            # Advice Logic
            if final_score > 90:
                advice = "Excellent! Maintain consistency. Focus on solving previous year papers."
                color = "green"
            elif final_score > 70:
                advice = f"Good! But you need to improve {weak_sub}. Spend 1 extra hour on it."
                color = "blue"
            else:
                advice = "Critical! Your current routine is not enough. You need professional guidance immediately."
                color = "red"

            # Display
            st.markdown("---")
            st.markdown(f"<h1 style='text-align: center; color: {color};'>{final_score}%</h1>", unsafe_allow_html=True)
            st.info(f"💡 **Azeez Sir Says:** {advice}")

            # PDF Download
            pdf_data = create_pro_pdf(name, final_score, hours, weak_sub, advice)
            st.download_button("📄 Download Full Report (PDF)", pdf_data, file_name=f"{name}_Azeez_Report.pdf", mime="application/pdf")
            
            # Save to session for Schedule Tab
            st.session_state['run_schedule'] = True
            st.session_state['user_hours'] = hours
            st.session_state['user_weak'] = weak_sub
            
            # Lead Gen Form
            if final_score < 85:
                st.warning("⚠️ Score is below target. Book a free counselling session.")
                with st.form("lead_gen"):
                    phone = st.text_input("Phone Number")
                    if st.form_submit_button("Request Call Back"):
                        save_to_sheet(name, phone, final_score, "Coaching Enquiry")
                        st.success("We will call you shortly!")

# --- TAB 2: SCHEDULER ---
with tab2:
    st.header("📅 Your AI Generated Schedule")
    if 'run_schedule' in st.session_state:
        st.write(f"Based on **{st.session_state['user_hours']} hours** of study, focusing on **{st.session_state['user_weak']}**:")
        df_schedule = make_schedule(st.session_state['user_hours'], st.session_state['user_weak'])
        st.table(df_schedule)
        st.caption("Tip: Take a 10-minute break after every slot.")
    else:
        st.info("Please run the Prediction in Tab 1 first to generate your schedule.")

# --- TAB 3: RESOURCES ---
with tab3:
    st.header("📚 Study Materials")
    st.write("Handpicked resources by Azeez Horizon.")
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### 📘 Class 9 & 10")
        st.link_button("Download NCERT Books", "https://ncert.nic.in/textbook.php")
        st.link_button("CBSE Sample Papers", "https://cbseacademic.nic.in/")
    with c2:
        st.markdown("### 📝 Notes & Forms")
        st.info("Contact Azeez Library for printed notes and form filling assistance.")

# --- TAB 4: ABOUT AZEEZ HORIZON ---
with tab4:
    st.image("azeez_banner.jpg", use_container_width=True)
    
    st.markdown("### 🌟 Our Services")
    
    st.markdown("""
    **1️⃣ Home Tuition (Class 1 to 10)**
    * Qualified tutors • Result-oriented • Safe & reliable

    **2️⃣ Online Educational Form Filling**
    * Admission forms • Scholarships • Government schemes • Exam forms

    **3️⃣ Student Mentorship**
    * Career guidance • Discipline • Mindset building • Study planning

    **4️⃣ Azeez Library**
    * Separate area for girls • Full-day study space • Silent & premium environment

    **5️⃣ Azeez Classes**
    * CBSE / ICSE • Class 6 to 10 Coaching Classes
    * Concept-based teaching • Discipline • Personalized support
    """)
    
    st.success("📍 Visit us at: [Behind IRFAN BTI House, Malik Tahir Pura, Mau U.P. 275101]")