import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from fpdf import FPDF
import plotly.graph_objects as go
import plotly.express as px

# --- CONFIGURATION & BRANDING ---
st.set_page_config(
    page_title="Azeez Horizon Hub", 
    page_icon="🎓", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS STYLING (Fixed for Dark Mode) ---
st.markdown("""
    <style>
    /* Force main background color */
    .stApp {
        background-color: #0E1117;
        color: white;
    }
    
    /* Fix Tab Text Colors for Dark Mode */
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1.2rem;
        font-weight: bold;
    }
    
    /* Active Tab Text Color */
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: #2E86C1 !important;
        color: white !important;
    }
    
    /* Inactive Tab Text Color (Make it readable) */
    .stTabs [data-baseweb="tab"] {
        background-color: #262730; 
        color: #FAFAFA;
    }

    /* Buttons */
    .stButton>button {
        background-color: #2E86C1; 
        color: white; 
        border-radius: 8px; 
        width: 100%;
        border: none;
    }
    
    /* Metrics Box */
    div[data-testid="metric-container"] {
        background-color: #262730;
        border: 1px solid #4F4F4F;
        padding: 10px;
        border-radius: 5px;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# --- BACKEND MANAGER (Google Sheets) ---
def get_google_sheet():
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        if "gcp_service_account" in st.secrets:
            creds_dict = st.secrets["gcp_service_account"]
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
            client = gspread.authorize(creds)
            return client.open("Azeez_Leads").sheet1
        return None
    except Exception as e:
        return None

def save_lead(name, phone, score, interest):
    sheet = get_google_sheet()
    if sheet:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sheet.append_row([name, phone, str(score), interest, current_time])
        return True
    return False

def get_all_leads():
    sheet = get_google_sheet()
    if sheet:
        return sheet.get_all_records()
    return []

# --- PDF GENERATOR ---
def create_pdf(name, score, hours, weak_subject, advice):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 20)
    pdf.set_text_color(46, 134, 193)
    pdf.cell(0, 10, "Azeez Horizon: Official Report", 0, 1, 'C')
    pdf.line(10, 25, 200, 25)
    pdf.ln(15)
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f"Name: {name} | Date: {datetime.now().strftime('%d-%b-%Y')}", 0, 1)
    
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 25)
    color = (0, 128, 0) if score > 75 else (200, 50, 50)
    pdf.set_text_color(*color)
    pdf.cell(0, 15, f"Predicted Score: {score}%", 0, 1, 'C')
    
    pdf.ln(10)
    pdf.set_text_color(0)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 8, f"Evaluation: {advice}\n\nFocus Strategy: Since {weak_subject} is your weak point, we have allocated 40% of your study time to it in the schedule.")
    
    # Footer Services
    pdf.set_y(-70)
    pdf.set_font("Arial", 'B', 10)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(0, 10, "  Powered by Azeez Horizon Services:", 1, 1, 'L', fill=True)
    pdf.set_font("Arial", size=9)
    pdf.multi_cell(0, 6, "1. Home Tuition (Class 1-10)\n2. Azeez Library (Premium Study Space)\n3. Azeez Classes (CBSE/ICSE Coaching)\n4. Student Mentorship & Career Guidance\n\nAddress: Behind IRFAN BTI House, Malik Tahir Pura, Mau U.P. 275101")
    
    return pdf.output(dest='S').encode('latin-1')

# --- ML ENGINE (Hidden) ---
data = {'Study_Hours': [2, 4, 6, 8, 10, 3, 5, 7, 9, 12], 'Prev_Marks': [50, 60, 75, 85, 95, 55, 70, 80, 90, 98], 'Sleep_Hours': [9, 8, 7, 7, 8, 8, 7, 6, 8, 8], 'Final_Score': [55, 65, 82, 88, 98, 58, 72, 85, 93, 99]}
model = LinearRegression()
model.fit(pd.DataFrame(data)[['Study_Hours', 'Prev_Marks', 'Sleep_Hours']], pd.DataFrame(data)['Final_Score'])

# ================== MAIN APP NAVIGATION ==================

# Sidebar Navigation
with st.sidebar:
    st.title("Azeez Horizon")
    try:
        st.image("azeez_banner.jpg", use_container_width=True)
    except:
        st.write("🎓 **Student Success Hub**")
        
    st.markdown("---")
    page = st.radio("Go to:", ["🏠 Student Hub", "📊 Admin Dashboard"])
    st.markdown("---")
    # --- FIX 1: FULL ADDRESS ---
    st.info("📍 **Behind IRFAN BTI House, Malik Tahir Pura, Mau U.P. 275101**")

# ================== PAGE 1: STUDENT HUB ==================
if page == "🏠 Student Hub":
    # --- FIX 3: NEW TITLE ---
    st.title("🚀 Let's predict your % with Azeez Library & Classes")
    st.write("Welcome to the future of learning. Predict your marks, get a schedule, and access resources.")
    
    # --- FIX 2: TABS (Colors fixed in CSS above) ---
    tab1, tab2, tab3, tab4 = st.tabs(["🔮 AI Predictor", "📅 Smart Schedule", "📚 Resources", "🏢 About Us"])
    
    # --- PREDICTOR TAB ---
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name")
            prev = st.number_input("Last Class %", 0, 100, 60)
            weak_sub = st.selectbox("Weak Subject", ["Maths", "Science", "SST", "English"])
        with col2:
            hours = st.slider("Study Hours/Day", 1, 14, 4)
            sleep = st.slider("Sleep Hours", 4, 12, 7)
            
        if st.button("Analyze Performance 🚀"):
            if name:
                pred = min(99.9, max(0, round(model.predict([[hours, prev, sleep]])[0], 1)))
                
                # Interactive Gauge Chart
                fig = go.Figure(go.Indicator(
                    mode = "gauge+number",
                    value = pred,
                    title = {'text': "Predicted Score", 'font': {'color': 'white'}}, # White text for dark mode
                    number = {'font': {'color': 'white'}},
                    gauge = {'axis': {'range': [0, 100], 'tickcolor': "white"}, 
                             'bar': {'color': "#2E86C1"},
                             'steps': [{'range': [0, 50], 'color': "#444"}, {'range': [50, 85], 'color': "#666"}]}
                ))
                fig.update_layout(paper_bgcolor = "rgba(0,0,0,0)", font = {'color': "white"})
                st.plotly_chart(fig, use_container_width=True)
                
                # Logic
                if pred > 85: advice = "Outstanding! You are on the Topper Track."
                elif pred > 60: advice = "Good, but consistency is key. Don't slack off."
                else: advice = "Critical Warning: You need immediate academic support."
                
                st.info(f"**Mentor's Note:** {advice}")
                
                # Save state
                st.session_state['run'] = True
                st.session_state['hours'] = hours
                st.session_state['weak'] = weak_sub
                st.session_state['name'] = name
                st.session_state['score'] = pred

                # Lead Capture
                if pred < 70:
                    st.warning("⚠️ Score Risk! We recommend joining Azeez Classes.")
                    with st.form("risk_form"):
                        ph = st.text_input("Enter Parent's Phone for Free Counselling")
                        if st.form_submit_button("Request Call"):
                            save_lead(name, ph, pred, "Low Score Alert")
                            st.success("Request Sent!")
                            
                # PDF Download
                pdf_bytes = create_pdf(name, pred, hours, weak_sub, advice)
                st.download_button("📥 Download Report Card", pdf_bytes, file_name=f"{name}_Report.pdf", mime="application/pdf")

    # --- SCHEDULE TAB ---
    with tab2:
        if 'run' in st.session_state:
            st.subheader(f"🗓️ Daily Plan for {st.session_state['name']}")
            subjects = ["Maths", "Science", "English", "SST"]
            if st.session_state['weak'] in subjects: subjects.remove(st.session_state['weak'])
            
            schedule = []
            schedule.append({"Time": "4:00 PM - 5:00 PM", "Subject": f"{st.session_state['weak']} (Priority)", "Type": "Concept Learning"})
            for i in range(int(st.session_state['hours']) - 1):
                t = 5 + i
                if t > 12: t = t - 12
                sub = subjects[i % len(subjects)]
                schedule.append({"Time": f"{t}:00 - {t+1}:00", "Subject": sub, "Type": "Practice"})
            
            df_sch = pd.DataFrame(schedule)
            st.table(df_sch)
        else:
            st.info("Please run the prediction first.")

    # --- RESOURCES TAB ---
    with tab3:
        st.header("🎯 Targeted Resources")
        selected_sub = st.selectbox("Select Subject", ["Maths", "Science", "SST", "English"])
        st.write(f"Showing resources for: **{selected_sub}**")
        st.info("Contact Azeez Library for full printed notes.")

    # --- TAB 4: ABOUT US ---
    with tab4:
        st.header("🏢 About Azeez Horizon")
        try:
            st.image("azeez_banner.jpg", use_container_width=True)
        except:
            pass

        st.markdown("### 🌟 Our Services")
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.markdown("""
            **1️⃣ Home Tuition (Class 1-10)**
            * Qualified tutors • Safe & reliable
            
            **2️⃣ Azeez Library**
            * Separate area for girls • Full-day study space
            """)
            
        with col_b:
            st.markdown("""
            **3️⃣ Azeez Classes (CBSE/ICSE)**
            * Class 6-10 • Concept-based teaching
            
            **4️⃣ Online Form Filling**
            * Admission forms • Scholarships
            """)

        st.markdown("---")
        st.success("📍 Visit us at: Behind IRFAN BTI House, Malik Tahir Pura, Mau U.P. 275101")

# ================== PAGE 2: ADMIN DASHBOARD ==================
elif page == "📊 Admin Dashboard":
    st.title("🔒 Restricted Access")
    pwd = st.text_input("Enter Admin Password", type="password")
    
    if pwd == "azeez2025":
        st.success("Login Successful!")
        data = get_all_leads()
        
        if data:
            df = pd.DataFrame(data)
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Leads", len(df))
            c2.metric("Avg Student Score", f"{round(pd.to_numeric(df['Score'], errors='coerce').mean(), 1)}%")
            c3.metric("Recent Enquiry", df.iloc[-1]['Name'] if len(df)>0 else "N/A")
            
            st.markdown("---")
            
            g1, g2 = st.columns(2)
            with g1:
                fig_pie = px.pie(df, names='Interest', title='Lead Categories')
                fig_pie.update_layout(paper_bgcolor = "rgba(0,0,0,0)", font = {'color': "white"})
                st.plotly_chart(fig_pie, use_container_width=True)
            with g2:
                fig_bar = px.bar(df, x='Name', y='Score', title='Student Score Analysis')
                fig_bar.update_layout(paper_bgcolor = "rgba(0,0,0,0)", font = {'color': "white"})
                st.plotly_chart(fig_bar, use_container_width=True)
            
            st.subheader("📋 Lead Database")
            st.dataframe(df)
            
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Excel/CSV", csv, "leads.csv", "text/csv")
        else:
            st.warning("No data found in Google Sheets yet.")