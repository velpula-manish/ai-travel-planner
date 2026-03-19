import streamlit as st
import os
import requests
import urllib.parse
import datetime
import re
import smtplib
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from groq import Groq
from tavily import TavilyClient
from fpdf import FPDF

GROQ_API_KEY   = st.secrets["GROQ_API_KEY"]
TAVILY_API_KEY = st.secrets["TAVILY_API_KEY"]
EMAIL_SENDER   = st.secrets.get("EMAIL_SENDER", "")
EMAIL_PASSWORD = st.secrets.get("EMAIL_PASSWORD", "")

st.set_page_config(
    page_title="AI Travel Planner ✈️",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(160deg, #0c1445, #1a237e, #283593) !important;
    min-height: 100vh;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1b2a 0%, #1b2a4a 100%) !important;
    border-right: 2px solid #38bdf8 !important;
}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] li,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div,
[data-testid="stSidebar"] label { color: #bae6fd !important; }
[data-testid="stSidebar"] strong { color: #38bdf8 !important; }
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: #7dd3fc !important; }
[data-testid="stAppViewContainer"]::before {
    content: "MANISH TRAVEL PLANNER";
    position: fixed; top: 45%; left: 55%;
    transform: translate(-50%, -50%) rotate(-30deg);
    font-size: 4.5rem; font-weight: 900;
    color: rgba(56,189,248,0.07); white-space: nowrap;
    pointer-events: none; z-index: 0;
    letter-spacing: 5px; text-transform: uppercase;
}
[data-testid="stAppViewContainer"] p,
[data-testid="stAppViewContainer"] li,
[data-testid="stAppViewContainer"] span,
[data-testid="stAppViewContainer"] div,
[data-testid="stAppViewContainer"] label { color: #e0f2fe !important; }
[data-testid="stAppViewContainer"] h1,
[data-testid="stAppViewContainer"] h2,
[data-testid="stAppViewContainer"] h3 { color: #7dd3fc !important; }
.main-title {
    text-align: center; font-size: 2.6rem; font-weight: 900;
    letter-spacing: 4px; text-transform: uppercase; padding: 15px 0 5px 0;
    background: linear-gradient(135deg, #38bdf8, #7dd3fc, #bae6fd);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
}
.subtitle {
    text-align: center; font-size: 0.9rem; text-transform: uppercase;
    letter-spacing: 3px; color: #7dd3fc; opacity: 0.85; margin-bottom: 3px;
}
.brand-tag {
    text-align: center; font-size: 0.8rem; letter-spacing: 3px;
    color: #38bdf8; font-weight: 700;
    text-transform: uppercase; margin-bottom: 10px;
}
.section-title {
    font-size: 1.05rem; font-weight: 800; text-transform: uppercase;
    letter-spacing: 2px; color: #38bdf8 !important; margin-bottom: 10px;
    border-left: 4px solid #0284c7; padding-left: 10px;
}
.weather-box {
    background: linear-gradient(135deg,rgba(2,132,199,0.3),rgba(3,105,161,0.4));
    border: 1.5px solid #38bdf8; border-radius: 12px;
    padding: 12px 16px; margin: 8px 0 12px 0;
    font-size: 0.92rem; font-weight: 600;
    color: #e0f2fe !important; line-height: 1.9;
    box-shadow: 0 4px 15px rgba(56,189,248,0.2);
}
.safety-box {
    border-radius: 14px; padding: 15px 20px; margin: 10px 0;
    font-weight: 700; line-height: 1.8;
}
.chat-user {
    background: rgba(2,132,199,0.3); border-radius: 12px 12px 4px 12px;
    padding: 10px 15px; margin: 8px 0; text-align: right;
    border: 1px solid #38bdf8; color: #e0f2fe !important;
}
.chat-bot {
    background: rgba(3,105,161,0.2); border-radius: 12px 12px 12px 4px;
    padding: 10px 15px; margin: 8px 0;
    border: 1px solid #0284c7; color: #e0f2fe !important;
}
.budget-warning {
    background: linear-gradient(135deg,rgba(239,68,68,0.2),rgba(185,28,28,0.3));
    border: 1.5px solid #ef4444; border-radius: 12px;
    padding: 12px 16px; margin: 8px 0;
    color: #fca5a5 !important; font-weight: 700;
}
.budget-ok {
    background: linear-gradient(135deg,rgba(16,185,129,0.2),rgba(5,150,105,0.3));
    border: 1.5px solid #10b981; border-radius: 12px;
    padding: 12px 16px; margin: 8px 0;
    color: #6ee7b7 !important; font-weight: 700;
}
.booking-card {
    background: linear-gradient(135deg,rgba(2,132,199,0.2),rgba(3,105,161,0.3));
    border: 1.5px solid #38bdf8; border-radius: 14px;
    padding: 15px 18px; margin: 8px 0; text-align: center;
    transition: all 0.3s ease;
}
.booking-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 25px rgba(56,189,248,0.3);
}
div[data-testid="column"] .stButton > button {
    background: linear-gradient(135deg, #0369a1, #0284c7) !important;
    color: #e0f2fe !important; font-size: 0.75rem !important;
    font-weight: 800 !important; height: 50px !important;
    min-height: 50px !important; max-height: 50px !important;
    padding: 2px 4px !important; border-radius: 10px !important;
    border: 1.5px solid #38bdf8 !important; text-transform: uppercase !important;
    letter-spacing: 0px !important; white-space: nowrap !important;
    overflow: visible !important; transition: all 0.2s !important;
    display: flex !important; align-items: center !important;
    justify-content: center !important; width: 100% !important;
    line-height: 1.2 !important; text-align: center !important;
}
div[data-testid="column"] .stButton > button:hover {
    background: linear-gradient(135deg, #0284c7, #38bdf8) !important;
    color: white !important; border-color: #7dd3fc !important;
    transform: translateY(-2px) !important;
}
.stButton > button {
    width: 100%;
    background: linear-gradient(135deg, #0369a1, #0284c7, #38bdf8) !important;
    color: white !important; font-size: 1.2rem !important;
    font-weight: 900 !important; padding: 18px 30px !important;
    border-radius: 14px !important; border: none !important;
    text-transform: uppercase !important; letter-spacing: 2px !important;
    box-shadow: 0 8px 32px rgba(56,189,248,0.4) !important;
    transition: all 0.3s !important;
}
.success-header {
    background: linear-gradient(135deg, #0369a1, #0284c7, #38bdf8);
    color: white !important; padding: 18px 25px; border-radius: 14px;
    font-size: 1.3rem; font-weight: 900; margin-bottom: 20px;
    text-align: center; text-transform: uppercase; letter-spacing: 3px;
    box-shadow: 0 8px 32px rgba(56,189,248,0.4);
}
.result-container {
    border: 1.5px solid #38bdf8; border-radius: 16px;
    padding: 25px 30px; margin-bottom: 20px;
    background: rgba(3,105,161,0.15); color: #e0f2fe !important;
}
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stNumberInput > div > div > input {
    background: rgba(3,105,161,0.3) !important;
    border: 1.5px solid #38bdf8 !important;
    border-radius: 8px !important; color: #ffffff !important;
    font-weight: 600 !important;
}
.stTextInput > div > div > input::placeholder,
.stTextArea > div > div > textarea::placeholder {
    color: #7dd3fc !important; opacity: 0.7 !important;
}
.stSelectbox > div > div {
    background: rgba(3,105,161,0.4) !important;
    border: 1.5px solid #38bdf8 !important;
    color: #ffffff !important; border-radius: 8px !important;
}
[data-baseweb="select"] ul {
    background: #0c1445 !important; border: 1px solid #38bdf8 !important;
}
[data-baseweb="select"] li {
    color: #e0f2fe !important; background: #0c1445 !important;
}
[data-baseweb="select"] li:hover {
    background: #0369a1 !important; color: white !important;
}
[data-baseweb="tag"] { background: #0284c7 !important; color: white !important; }
[data-baseweb="tag"] span { color: white !important; }
.stMultiSelect > div > div {
    background: rgba(3,105,161,0.4) !important;
    border: 1.5px solid #38bdf8 !important;
}
.stDownloadButton > button {
    background: linear-gradient(135deg, #1e40af, #2563eb) !important;
    color: white !important; font-weight: 800 !important;
    font-size: 0.95rem !important; text-transform: uppercase !important;
    border-radius: 10px !important; border: none !important;
    padding: 12px !important; width: 100% !important;
}
hr { border-color: rgba(56,189,248,0.3) !important; }
.footer { text-align: center; text-transform: uppercase; letter-spacing: 2px;
    opacity: 0.5; font-size: 0.75rem; margin-top: 5px; color: #38bdf8 !important; }
.footer-brand { text-align: center; text-transform: uppercase; letter-spacing: 3px;
    font-size: 0.7rem; color: #38bdf8 !important; opacity: 0.6; margin-top: 3px; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════
# SESSION STATE INIT
# ══════════════════════════════════════
if "selected_destination" not in st.session_state:
    st.session_state.selected_destination = ""
if "itinerary_ready" not in st.session_state:
    st.session_state.itinerary_ready = False
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "itinerary_result" not in st.session_state:
    st.session_state.itinerary_result = ""

groq_client = Groq(api_key=GROQ_API_KEY)

# ══════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════
with st.sidebar:
    st.markdown(
        "<h2 style='color:#38bdf8;text-transform:uppercase;"
        "letter-spacing:2px;font-size:1rem;'>🌍 MANISH TRAVEL PLANNER</h2>",
        unsafe_allow_html=True
    )
    st.markdown("---")
    st.markdown("### ⚡ POWERED BY")
    st.markdown("""
    - 🧠 **GROQ** — LLAMA 3.1 AI BRAIN
    - 🔍 **TAVILY** — REAL-TIME WEB SEARCH
    - 🌤️ **OPEN-METEO** — LIVE WEATHER
    - 📊 **PLOTLY** — VISUAL CHARTS
    - 🎨 **STREAMLIT** — BEAUTIFUL UI
    """)
    st.markdown("---")
    st.markdown("### 🏆 UNIQUE FEATURES")
    st.markdown("""
    - 💬 **AI CHATBOT** — Ask anything about your trip!
    - 📊 **VISUAL DASHBOARD** — Budget & timeline charts!
    - 🛡️ **SAFETY SCORE** — Real-time safety rating!
    - 🌤️ **LIVE WEATHER** — Current conditions!
    - 💰 **BUDGET GUARD** — Never overspend!
    - 🗺️ **FULL JOURNEY** — From home to back!
    - 🌐 **12 LANGUAGES** — Plan in your language!
    - 📧 **EMAIL + PDF** — Save & share!
    """)
    st.markdown("---")
    st.markdown(
        "<div style='text-align:center;color:#38bdf8;font-size:0.75rem;"
        "text-transform:uppercase;letter-spacing:2px;'>"
        "© MANISH TRAVEL PLANNER<br>ALL RIGHTS RESERVED</div>",
        unsafe_allow_html=True
    )

# ══════════════════════════════════════
# HEADER
# ══════════════════════════════════════
st.markdown('<div class="main-title">🌍 AI TRAVEL ITINERARY PLANNER</div>',
            unsafe_allow_html=True)
st.markdown('<div class="subtitle">YOUR PERSONAL AI TRAVEL AGENT — POWERED BY GROQ + TAVILY</div>',
            unsafe_allow_html=True)
st.markdown('<div class="brand-tag">— BY MANISH TRAVEL PLANNER —</div>',
            unsafe_allow_html=True)
st.markdown("---")

# ══════════════════════════════════════
# POPULAR DESTINATIONS
# ══════════════════════════════════════
st.markdown(
    '<div class="section-title">🔥 POPULAR DESTINATIONS — CLICK TO AUTO-FILL</div>',
    unsafe_allow_html=True
)
popular_destinations = [
    ("🗼","PARIS"),    ("🗽","NEW YORK"), ("🏯","TOKYO"),   ("🕌","DUBAI"),
    ("🏛️","ROME"),     ("🌴","BALI"),     ("🐘","KERALA"),  ("⛩️","RAJASTHAN"),
    ("🏔️","MANALI"),   ("🌊","GOA"),      ("🏰","LONDON"),  ("🗺️","SINGAPORE"),
]
dest_cols = st.columns(4)
for i, (emoji, city) in enumerate(popular_destinations):
    with dest_cols[i % 4]:
        if st.button(f"{emoji} {city}", key=f"dest_{i}", use_container_width=True):
            st.session_state.selected_destination = city.title()
            st.rerun()
st.markdown("---")

# ══════════════════════════════════════
# ROUTE
# ══════════════════════════════════════
st.markdown('<div class="section-title">🗺️ YOUR JOURNEY ROUTE</div>',
            unsafe_allow_html=True)
r1, r2, r3 = st.columns([5, 1, 5])
with r1:
    st.markdown("<p style='color:#38bdf8;font-weight:800;font-size:0.95rem;"
                "text-transform:uppercase;margin-bottom:4px;'>🏠 STARTING FROM</p>",
                unsafe_allow_html=True)
    from_city = st.text_input("from_lbl", placeholder="e.g. Mumbai, Delhi...",
                               label_visibility="collapsed")
with r2:
    st.markdown("<div style='text-align:center;font-size:2.5rem;padding-top:28px;'>✈️</div>",
                unsafe_allow_html=True)
with r3:
    st.markdown("<p style='color:#38bdf8;font-weight:800;font-size:0.95rem;"
                "text-transform:uppercase;margin-bottom:4px;'>📍 GOING TO</p>",
                unsafe_allow_html=True)
    to_city = st.text_input("to_lbl",
                             value=st.session_state.selected_destination,
                             placeholder="e.g. Paris, Goa, Tokyo...",
                             label_visibility="collapsed")
    if to_city != st.session_state.selected_destination:
        st.session_state.selected_destination = to_city

destination = to_city

if from_city and to_city:
    st.markdown(
        f"<div style='background:linear-gradient(135deg,rgba(2,132,199,0.25),"
        f"rgba(3,105,161,0.35));border:1.5px solid #38bdf8;border-radius:12px;"
        f"padding:12px 20px;margin:8px 0;text-align:center;font-weight:800;"
        f"font-size:1rem;color:#e0f2fe;letter-spacing:1px;'>"
        f"🗺️ ROUTE: <span style='color:#38bdf8'>{from_city.upper()}</span>"
        f" ✈️ <span style='color:#4ade80'>{to_city.upper()}</span></div>",
        unsafe_allow_html=True
    )
st.markdown("---")

# ══════════════════════════════════════
# DURATION FIRST (for date auto-fill)
# ══════════════════════════════════════
st.markdown('<div class="section-title">📝 TRIP DETAILS</div>', unsafe_allow_html=True)
duration = st.slider("📅 TRIP DURATION (DAYS)", 1, 14, 3)
st.markdown(
    f"<p style='color:#38bdf8;font-weight:700;font-size:0.85rem;'>"
    f"✅ SELECTED: {duration} DAY(S)</p>",
    unsafe_allow_html=True
)

col1, col2 = st.columns([1, 1])

with col1:
    # ── WEATHER ──
    if destination and len(destination.strip()) > 2:
        weather_ph = st.empty()
        try:
            geo = requests.get(
                "https://geocoding-api.open-meteo.com/v1/search",
                params={"name": destination, "count": 1, "language": "en", "format": "json"},
                timeout=8
            ).json()
            if geo.get("results"):
                lat  = geo["results"][0]["latitude"]
                lon  = geo["results"][0]["longitude"]
                cn   = geo["results"][0].get("name", destination)
                ctr  = geo["results"][0].get("country", "")
                wx   = requests.get(
                    "https://api.open-meteo.com/v1/forecast",
                    params={"latitude": lat, "longitude": lon,
                            "current_weather": "true",
                            "hourly": "relativehumidity_2m,precipitation_probability",
                            "timezone": "auto", "forecast_days": 1},
                    timeout=8
                ).json()
                if "current_weather" in wx:
                    cw   = wx["current_weather"]
                    temp = cw.get("temperature","—")
                    wind = cw.get("windspeed","—")
                    wc   = cw.get("weathercode", 0)
                    hum  = wx.get("hourly",{}).get("relativehumidity_2m",["—"])[0]
                    rain = wx.get("hourly",{}).get("precipitation_probability",["—"])[0]
                    codes= {0:"☀️ Clear",1:"🌤️ Mainly Clear",2:"⛅ Partly Cloudy",
                            3:"☁️ Overcast",45:"🌫️ Foggy",51:"🌦️ Drizzle",
                            61:"🌧️ Rain",80:"🌦️ Showers",95:"⛈️ Thunderstorm"}
                    cond = codes.get(wc,"🌡️ Clear")
                    weather_ph.markdown(
                        f'<div class="weather-box">'
                        f'<strong>🌤️ LIVE WEATHER — {cn.upper()}</strong><br>'
                        f'🌡️ {temp}°C &nbsp;|&nbsp; {cond}<br>'
                        f'💨 Wind: {wind}km/h &nbsp;|&nbsp; '
                        f'💧 Humidity: {hum}% &nbsp;|&nbsp; 🌧️ Rain: {rain}%'
                        f'</div>', unsafe_allow_html=True
                    )
        except Exception:
            pass

    # ══════════════════════════════════════
    # UNIQUE FEATURE 1: SAFETY SCORE
    # Real-time AI safety analysis
    # ChatGPT cannot do this automatically!
    # ══════════════════════════════════════
    if destination and len(destination.strip()) > 2:
        with st.expander("🛡️ DESTINATION SAFETY SCORE", expanded=True):
            if st.button("🔍 CHECK SAFETY SCORE", key="safety_btn",
                         use_container_width=True):
                with st.spinner("Analyzing safety..."):
                    try:
                        tavily = TavilyClient(api_key=TAVILY_API_KEY)
                        safety_res = tavily.search(
                            query=f"is {destination} safe for tourists 2025 travel advisory",
                            max_results=3, search_depth="basic"
                        )
                        safety_info = " ".join([
                            r.get("content","")[:200]
                            for r in safety_res.get("results",[])
                        ])
                        safety_resp = groq_client.chat.completions.create(
                            model="llama-3.1-8b-instant",
                            messages=[{
                                "role": "user",
                                "content": f"""Based on this info about {destination}: {safety_info}
Give a safety analysis in this EXACT format:
SAFETY_SCORE: [number 1-10]
OVERALL: [Safe/Moderate/Caution]
BEST_TIME: [best months to visit]
CROWD_LEVEL: [Low/Medium/High]
SOLO_FEMALE: [Safe/Moderate/Caution]
TOP_TIP: [one key safety tip]
Only respond in this exact format, nothing else."""
                            }],
                            max_tokens=200, temperature=0.3
                        )
                        safety_text = safety_resp.choices[0].message.content
                        lines = {}
                        for line in safety_text.strip().split("\n"):
                            if ":" in line:
                                k, v = line.split(":", 1)
                                lines[k.strip()] = v.strip()

                        score   = int(lines.get("SAFETY_SCORE","7"))
                        overall = lines.get("OVERALL","Safe")
                        color   = "#10b981" if score >= 7 else "#f59e0b" if score >= 5 else "#ef4444"
                        emoji_s = "🟢" if score >= 7 else "🟡" if score >= 5 else "🔴"

                        st.markdown(
                            f'<div class="safety-box" style="background:linear-gradient('
                            f'135deg,rgba(16,185,129,0.15),rgba(5,150,105,0.25));'
                            f'border:1.5px solid {color};">'
                            f'<strong style="font-size:1.1rem;color:{color};">'
                            f'{emoji_s} SAFETY SCORE: {score}/10 — {overall}</strong><br>'
                            f'⏰ BEST TIME: {lines.get("BEST_TIME","—")}<br>'
                            f'👥 CROWD LEVEL: {lines.get("CROWD_LEVEL","—")}<br>'
                            f'👩 SOLO FEMALE: {lines.get("SOLO_FEMALE","—")}<br>'
                            f'💡 TIP: {lines.get("TOP_TIP","—")}'
                            f'</div>',
                            unsafe_allow_html=True
                        )
                    except Exception as e:
                        st.error(f"Could not fetch safety data: {e}")

    # BUDGET
    st.markdown("##### 💰 BUDGET")
    b1, b2 = st.columns([1, 3])
    with b1:
        currency = st.selectbox("CURRENCY",
                                 ["₹ INR","$ USD","€ EUR","£ GBP"], index=0)
    with b2:
        ph_map = {"INR":("e.g. 50000","₹20k–₹2L"),
                  "USD":("e.g. 1500","$500–$10k"),
                  "EUR":("e.g. 1200","€500–€8k"),
                  "GBP":("e.g. 1000","£400–£7k")}
        curr_key      = [k for k in ph_map if k in currency][0]
        ph, hint      = ph_map[curr_key]
        budget_amount = st.text_input("AMOUNT", placeholder=ph, help=hint)

    budget_status = "unknown"
    budget_tier   = "BUDGET"

    if budget_amount:
        try:
            amt     = float(budget_amount.replace(",",""))
            per_day = amt / max(duration,1)
            min_c   = {"INR":1500,"USD":50,"EUR":45,"GBP":40}[curr_key]
            com_c   = {"INR":4000,"USD":150,"EUR":130,"GBP":110}[curr_key]
            lux_c   = {"INR":10000,"USD":300,"EUR":250,"GBP":220}[curr_key]

            if per_day < min_c:
                budget_status = "low"
                budget_tier   = "BUDGET"
                st.markdown(
                    f'<div class="budget-warning">⚠️ BUDGET TOO LOW!<br>'
                    f'Your daily: <strong>{currency} {per_day:.0f}</strong> | '
                    f'Min needed: <strong>{currency} {min_c}</strong><br>'
                    f'💡 Increase to at least <strong>{currency} {min_c*duration:.0f}</strong>'
                    f'</div>', unsafe_allow_html=True)
            elif per_day < com_c:
                budget_status = "ok"
                budget_tier   = "BUDGET"
                st.markdown(
                    f'<div class="budget-ok">✅ GOOD STUDENT BUDGET!<br>'
                    f'Daily: <strong>{currency} {per_day:.0f}/day</strong><br>'
                    f'🎒 Covers: Hostels, local food, public transport!'
                    f'</div>', unsafe_allow_html=True)
            elif per_day < lux_c:
                budget_status = "comfortable"
                budget_tier   = "MODERATE"
                st.markdown(
                    f'<div class="budget-ok">✅ COMFORTABLE BUDGET!<br>'
                    f'Daily: <strong>{currency} {per_day:.0f}/day</strong><br>'
                    f'🏨 Covers: Mid-range hotels, good restaurants!'
                    f'</div>', unsafe_allow_html=True)
            else:
                budget_status = "luxury"
                budget_tier   = "LUXURY"
                st.markdown(
                    f'<div class="budget-ok">💎 LUXURY BUDGET!<br>'
                    f'Daily: <strong>{currency} {per_day:.0f}/day</strong><br>'
                    f'🌟 Premium hotels, fine dining, exclusive experiences!'
                    f'</div>', unsafe_allow_html=True)
        except Exception:
            pass

    budget = f"{currency} {budget_amount}" if budget_amount else f"{currency} (not specified)"

with col2:
    # DATE PICKER
    st.markdown("<p style='color:#e0f2fe;font-weight:700;font-size:0.9rem;"
                "margin-bottom:4px;'>🗓️ TRAVEL DATES</p>", unsafe_allow_html=True)
    today     = datetime.date.today()
    default_s = today + datetime.timedelta(days=7)
    dc1, dc2  = st.columns(2)
    with dc1:
        start_date = st.date_input("FROM DATE ✈️", value=default_s,
                                    min_value=today, key="start_date_input")
    with dc2:
        auto_end = start_date + datetime.timedelta(days=duration)
        end_date = st.date_input("TO DATE 🏁", value=auto_end,
                                  min_value=today, key="end_date_input")

    if end_date <= start_date:
        st.warning("⚠️ TO DATE MUST BE AFTER FROM DATE!")
        travel_dates = start_date.strftime('%d %b %Y')
        trip_days    = duration
    else:
        trip_days    = (end_date - start_date).days
        travel_dates = (f"{start_date.strftime('%d %b %Y')} "
                       f"to {end_date.strftime('%d %b %Y')}")
        st.markdown(
            f"<p style='color:#38bdf8;font-weight:700;font-size:0.85rem;'>"
            f"✅ {trip_days} DAY TRIP: {start_date.strftime('%d %b')} → "
            f"{end_date.strftime('%d %b %Y')}</p>", unsafe_allow_html=True)

    travelers = st.number_input("👥 NUMBER OF TRAVELERS", 1, 20, 2)
    language  = st.selectbox("🌐 OUTPUT LANGUAGE", options=[
        "English","Hindi — हिन्दी","Tamil — தமிழ்","Telugu — తెలుగు",
        "Kannada — ಕನ್ನಡ","Malayalam — മലയാളം","Bengali — বাংলা",
        "Marathi — मराठी","French — Français","Spanish — Español",
        "Arabic — عربي","Japanese — 日本語"], index=0)
    lang_name = language.split("—")[0].strip()
    interests = st.multiselect("❤️ YOUR INTERESTS", [
        "🏛️ HISTORY & CULTURE","🍽️ FOOD & DINING","🎨 ART & MUSEUMS",
        "🌿 NATURE & OUTDOORS","🛍️ SHOPPING","🎭 NIGHTLIFE",
        "🏖️ BEACH & RELAXATION","🏔️ ADVENTURE & SPORTS",
        "📸 PHOTOGRAPHY","👨‍👩‍👧 FAMILY FRIENDLY"],
        default=["🍽️ FOOD & DINING","🎨 ART & MUSEUMS"])

special_requirements = st.text_area(
    "💬 SPECIAL REQUIREMENTS (OPTIONAL)",
    placeholder="e.g. Vegetarian food, student trip, budget-friendly only...",
    height=80
)
st.markdown("---")


# ══════════════════════════════════════
# HELPER FUNCTIONS
# ══════════════════════════════════════
def create_pdf(content, from_city, destination, duration,
               budget, travel_dates, travelers):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(2,132,199)
    pdf.rect(0,0,210,35,'F')
    pdf.set_font("Arial","B",20)
    pdf.set_text_color(255,255,255)
    pdf.cell(0,12,"AI TRAVEL ITINERARY PLANNER",ln=True,align="C")
    pdf.set_font("Arial","B",13)
    pdf.cell(0,8,"BY MANISH TRAVEL PLANNER",ln=True,align="C")
    pdf.set_font("Arial","",10)
    pdf.cell(0,8,"ai-travel-planner-h7f7ryewjbufa5tdvfewnu.streamlit.app",
             ln=True,align="C")
    pdf.set_fill_color(224,242,254)
    pdf.rect(10,40,190,35,'F')
    pdf.set_text_color(2,132,199)
    pdf.set_font("Arial","B",11)
    pdf.set_xy(12,42)
    route = f"{from_city.upper()} TO {destination.upper()}" if from_city else destination.upper()
    pdf.cell(0,6,f"ROUTE: {route}  |  {duration} DAYS  |  {travelers} TRAVELERS",ln=True)
    pdf.set_xy(12,50)
    pdf.cell(0,6,f"DATES: {travel_dates}  |  BUDGET: {budget}",ln=True)
    pdf.set_xy(10,80)
    pdf.set_text_color(30,30,30)
    pdf.set_font("Arial","",10)
    clean = re.sub(r'[^\x00-\x7F]+',' ',content)
    clean = clean.replace("##","\n").replace("**","")
    for line in clean.split('\n'):
        line = line.strip()
        if not line: pdf.ln(3); continue
        if line.startswith("###"):
            pdf.set_font("Arial","B",11); pdf.set_text_color(2,132,199)
            pdf.multi_cell(0,7,line.replace("###","").strip())
            pdf.set_font("Arial","",10); pdf.set_text_color(30,30,30)
        elif line.startswith("#"):
            pdf.set_font("Arial","B",12); pdf.set_text_color(1,63,120)
            pdf.multi_cell(0,8,line.replace("#","").strip())
            pdf.set_font("Arial","",10); pdf.set_text_color(30,30,30)
        else:
            pdf.multi_cell(0,6,line)
    pdf.set_y(-20)
    pdf.set_fill_color(2,132,199)
    pdf.rect(0,pdf.get_y(),210,20,'F')
    pdf.set_text_color(255,255,255)
    pdf.set_font("Arial","B",9)
    pdf.cell(0,8,"© MANISH TRAVEL PLANNER — ALL RIGHTS RESERVED",align="C")
    return pdf.output(dest='S').encode('latin-1')


def send_email_fn(to_email, from_city, destination, itinerary,
                  duration, travel_dates, budget):
    try:
        route = f"{from_city} → {destination}" if from_city else destination
        msg   = MIMEMultipart("alternative")
        msg["Subject"] = f"✈️ YOUR {duration}-DAY {destination.upper()} ITINERARY"
        msg["From"]    = EMAIL_SENDER
        msg["To"]      = to_email
        html = f"""<html><body style="font-family:Arial;background:#0c1445;padding:20px;">
        <div style="max-width:700px;margin:auto;background:#1a237e;border-radius:16px;overflow:hidden;">
        <div style="background:#0284c7;padding:25px;text-align:center;">
        <h1 style="color:white;margin:0;">🌍 AI TRAVEL ITINERARY PLANNER</h1>
        <p style="color:#bae6fd;margin:5px 0;">BY MANISH TRAVEL PLANNER</p></div>
        <div style="padding:20px;background:#e0f2fe;color:#0c1445;">
        <p><strong>✈️ ROUTE:</strong> {route.upper()}<br>
        <strong>📅 DATES:</strong> {travel_dates}<br>
        <strong>💰 BUDGET:</strong> {budget}</p>
        <div style="white-space:pre-wrap;font-size:14px;line-height:1.8;">{itinerary}</div>
        </div></div></body></html>"""
        msg.attach(MIMEText(html,"html"))
        with smtplib.SMTP_SSL("smtp.gmail.com",465) as s:
            s.login(EMAIL_SENDER, EMAIL_PASSWORD)
            s.sendmail(EMAIL_SENDER, to_email, msg.as_string())
        return True
    except Exception as e:
        return str(e)


def generate_itinerary(from_city, destination, duration, budget,
                        travel_dates, travelers, interests,
                        special_requirements, lang_name,
                        budget_tier, budget_status):
    tavily = TavilyClient(api_key=TAVILY_API_KEY)
    try:
        res = tavily.search(
            query=f"budget travel guide {destination} cheap hotels food transport 2025",
            max_results=3, search_depth="basic"
        )
        web_info = "\n".join([f"- {r.get('title','')}: {r.get('content','')[:300]}"
                              for r in res.get("results",[])])
    except Exception:
        web_info = "Popular destination."

    curr_symbol = budget.split()[0]
    route       = f"{from_city} to {destination}" if from_city else destination
    interests_text = ", ".join(interests) if interests else "General Sightseeing"

    if budget_status == "low":
        b_inst = f"CRITICAL: Budget {budget} is very tight. Only free/cheap options. Warn traveler clearly."
    elif budget_tier == "BUDGET":
        b_inst = f"BUDGET TRAVELER: Only hostels/guesthouses, street food, public transport. Budget: {budget}."
    elif budget_tier == "MODERATE":
        b_inst = f"MID-RANGE: Mid-range hotels, good restaurants. Budget: {budget}."
    else:
        b_inst = f"LUXURY: Premium options. Budget: {budget}."

    prompt = f"""Expert AI Travel Planner. Write in {lang_name}.
{b_inst}
Web info: {web_info}
Route: {route} | Dates: {travel_dates} | Travelers: {travelers}
Interests: {interests_text} | Notes: {special_requirements or 'None'}

## 🚀 JOURNEY OVERVIEW
## 🚌 HOW TO REACH {destination.upper()} FROM {from_city.upper() if from_city else 'YOUR CITY'}
[Flight/train/bus options with costs in {curr_symbol}]
## 🌍 DESTINATION OVERVIEW
## 📅 DAY-BY-DAY ITINERARY
### DAY 1 — ARRIVAL
[Morning: depart from {from_city if from_city else 'home'} | Afternoon: arrive & check-in | Evening: explore]
[Continue all {duration} days]
### DAY {duration} — DEPARTURE
[Morning: checkout | Afternoon: return to {from_city if from_city else 'home'}]
## 🏨 ACCOMMODATION [{budget_tier} OPTIONS ONLY]
## 🍽️ WHERE TO EAT [BUDGET-MATCHED]
## 💰 COMPLETE BUDGET BREAKDOWN
[Include transport to/from {destination}, accommodation {duration} nights, food, activities]
[TOTAL must be within {budget}]
## 💡 MONEY-SAVING TIPS
## 🚗 LOCAL TRANSPORT
## 🎒 PACKING LIST [10 essentials]"""

    resp = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role":"system","content":f"Expert travel planner in {lang_name}. Strict budget: {budget}."},
            {"role":"user","content":prompt}
        ],
        max_tokens=3000, temperature=0.7
    )
    return resp.choices[0].message.content


# ══════════════════════════════════════
# GENERATE BUTTON
# ══════════════════════════════════════
generate_btn = st.button("🚀 GENERATE MY COMPLETE TRAVEL PLAN!", use_container_width=True)

if generate_btn:
    if not destination:
        st.error("⚠️ PLEASE ENTER YOUR DESTINATION!")
    elif end_date <= start_date:
        st.error("⚠️ PLEASE SELECT VALID TRAVEL DATES!")
    elif not budget_amount:
        st.error("⚠️ PLEASE ENTER YOUR BUDGET AMOUNT!")
    else:
        with st.spinner("🔍 AI IS PLANNING YOUR COMPLETE JOURNEY... ⏳"):
            try:
                result = generate_itinerary(
                    from_city, destination, trip_days, budget,
                    travel_dates, travelers, interests,
                    special_requirements, lang_name,
                    budget_tier, budget_status
                )
                st.session_state.itinerary_result = result
                st.session_state.itinerary_dest   = destination
                st.session_state.itinerary_from   = from_city
                st.session_state.itinerary_ready  = True
                st.session_state.chat_history     = []
            except Exception as e:
                st.error(f"❌ ERROR: {str(e)}")


# ══════════════════════════════════════
# RESULTS SECTION
# ══════════════════════════════════════
if st.session_state.get("itinerary_ready"):
    result      = st.session_state.itinerary_result
    destination = st.session_state.itinerary_dest
    from_city   = st.session_state.get("itinerary_from","")

    st.markdown("---")
    st.markdown('<div class="success-header">✅ YOUR COMPLETE TRAVEL PLAN IS READY!</div>',
                unsafe_allow_html=True)

    # ══════════════════════════════════════
    # TABS — Unique feature! Organized view
    # ══════════════════════════════════════
    tab1, tab2, tab3 = st.tabs([
        "📋 FULL ITINERARY",
        "📊 VISUAL DASHBOARD",
        "💬 AI TRAVEL CHATBOT"
    ])

    # ── TAB 1: ITINERARY ──
    with tab1:
        st.markdown('<div class="result-container">', unsafe_allow_html=True)
        st.markdown(result)
        st.markdown('</div>', unsafe_allow_html=True)

    # ══════════════════════════════════════
    # TAB 2: VISUAL DASHBOARD
    # ChatGPT CANNOT show charts!
    # ══════════════════════════════════════
    with tab2:
        st.markdown('<div class="section-title">📊 VISUAL TRIP DASHBOARD</div>',
                    unsafe_allow_html=True)

        try:
            import plotly.graph_objects as go
            import plotly.express as px

            # ── Budget Pie Chart ──
            st.markdown("#### 💰 BUDGET BREAKDOWN CHART")
            if budget_amount:
                try:
                    total = float(budget_amount.replace(",",""))
                    # Estimate breakdown percentages
                    if budget_tier == "BUDGET":
                        breakdown = {
                            "🏨 Accommodation": total * 0.30,
                            "🍽️ Food":          total * 0.25,
                            "🚗 Transport":     total * 0.25,
                            "🎭 Activities":    total * 0.12,
                            "🛒 Shopping":      total * 0.08,
                        }
                    elif budget_tier == "MODERATE":
                        breakdown = {
                            "🏨 Accommodation": total * 0.35,
                            "🍽️ Food":          total * 0.22,
                            "🚗 Transport":     total * 0.20,
                            "🎭 Activities":    total * 0.15,
                            "🛒 Shopping":      total * 0.08,
                        }
                    else:
                        breakdown = {
                            "🏨 Accommodation": total * 0.40,
                            "🍽️ Food":          total * 0.20,
                            "🚗 Transport":     total * 0.15,
                            "🎭 Activities":    total * 0.18,
                            "🛒 Shopping":      total * 0.07,
                        }

                    fig_pie = go.Figure(data=[go.Pie(
                        labels=list(breakdown.keys()),
                        values=[round(v,0) for v in breakdown.values()],
                        hole=0.4,
                        marker=dict(colors=[
                            "#38bdf8","#4ade80","#f59e0b","#a78bfa","#f87171"
                        ])
                    )])
                    fig_pie.update_layout(
                        title=f"Budget Distribution — {currency} {budget_amount}",
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        font=dict(color="#e0f2fe"),
                        legend=dict(bgcolor="rgba(0,0,0,0)")
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)
                except Exception:
                    st.info("Enter budget amount to see chart")

            # ── Day-by-Day Timeline ──
            st.markdown("#### 📅 TRIP TIMELINE")
            days      = [f"Day {i+1}" for i in range(trip_days)]
            activities = ["Arrival & Explore"] + \
                        [f"Sightseeing Day {i}" for i in range(1, trip_days-1)] + \
                        ["Departure"]
            if len(activities) < trip_days:
                activities = activities[:trip_days]
            elif len(activities) > trip_days:
                activities = activities[:trip_days]

            fig_bar = go.Figure(go.Bar(
                x=days[:len(activities)],
                y=[8]*len(activities),
                text=activities[:len(days)],
                textposition="inside",
                marker_color=["#38bdf8","#4ade80","#f59e0b",
                              "#a78bfa","#f87171","#34d399",
                              "#60a5fa","#fb923c","#e879f9",
                              "#a3e635","#2dd4bf","#fbbf24",
                              "#c084fc","#f43f5e"][:trip_days]
            ))
            fig_bar.update_layout(
                title="Your Trip Day-by-Day Timeline",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#e0f2fe"),
                yaxis=dict(visible=False),
                xaxis=dict(color="#e0f2fe")
            )
            st.plotly_chart(fig_bar, use_container_width=True)

            # ── Trip Stats ──
            st.markdown("#### 📈 TRIP SUMMARY STATS")
            s1, s2, s3, s4 = st.columns(4)
            stats = [
                (s1, "📅 TOTAL DAYS",    f"{trip_days}",                "days"),
                (s2, "👥 TRAVELERS",      f"{travelers}",                "people"),
                (s3, "💰 TOTAL BUDGET",   f"{currency} {budget_amount}", ""),
                (s4, "📍 DESTINATION",    destination.upper(),           ""),
            ]
            for col, title, value, unit in stats:
                with col:
                    col.markdown(
                        f'<div style="background:rgba(2,132,199,0.2);'
                        f'border:1px solid #38bdf8;border-radius:12px;'
                        f'padding:15px;text-align:center;">'
                        f'<div style="color:#7dd3fc;font-size:0.8rem;'
                        f'text-transform:uppercase;">{title}</div>'
                        f'<div style="color:#38bdf8;font-size:1.4rem;'
                        f'font-weight:900;">{value}</div>'
                        f'<div style="color:#bae6fd;font-size:0.75rem;">{unit}</div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
        except ImportError:
            st.info("Install plotly: add 'plotly' to requirements.txt")

    # ══════════════════════════════════════
    # TAB 3: AI TRAVEL CHATBOT
    # ChatGPT resets — OURS REMEMBERS!
    # ══════════════════════════════════════
    with tab3:
        st.markdown('<div class="section-title">💬 ASK YOUR AI TRAVEL ASSISTANT</div>',
                    unsafe_allow_html=True)
        st.markdown(
            "<p style='color:#bae6fd;font-size:0.9rem;'>"
            "🤖 Your AI assistant knows your full itinerary! Ask anything about your trip.</p>",
            unsafe_allow_html=True
        )

        # Quick question buttons
        st.markdown("**⚡ QUICK QUESTIONS:**")
        q_cols = st.columns(3)
        quick_questions = [
            "Is it safe for solo travel?",
            "What should I pack?",
            "Give cheaper hotel options",
            "Best local street food?",
            "How to save more money?",
            "What to avoid there?"
        ]
        for i, q in enumerate(quick_questions):
            with q_cols[i % 3]:
                if st.button(q, key=f"quick_{i}", use_container_width=True):
                    st.session_state.chat_history.append({
                        "role": "user", "content": q
                    })
                    with st.spinner("🤔 Thinking..."):
                        chat_resp = groq_client.chat.completions.create(
                            model="llama-3.1-8b-instant",
                            messages=[
                                {"role": "system", "content":
                                    f"You are a helpful travel assistant. "
                                    f"The user has planned a {trip_days}-day trip to "
                                    f"{destination} from {from_city if from_city else 'their city'}. "
                                    f"Budget: {budget}. Here is their itinerary: "
                                    f"{result[:1500]}. Answer concisely and helpfully."},
                                *st.session_state.chat_history
                            ],
                            max_tokens=500, temperature=0.7
                        )
                        answer = chat_resp.choices[0].message.content
                        st.session_state.chat_history.append({
                            "role": "assistant", "content": answer
                        })
                    st.rerun()

        st.markdown("---")

        # Show chat history
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(
                    f'<div class="chat-user">👤 <strong>YOU:</strong> {msg["content"]}</div>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f'<div class="chat-bot">🤖 <strong>AI ASSISTANT:</strong><br>'
                    f'{msg["content"]}</div>',
                    unsafe_allow_html=True
                )

        # Custom question input
        st.markdown("---")
        user_q = st.text_input(
            "💬 ASK YOUR OWN QUESTION",
            placeholder="e.g. Is monsoon season good for visiting? What are hidden gems?",
            key="chat_input"
        )
        ask_col1, ask_col2 = st.columns([4, 1])
        with ask_col2:
            if st.button("SEND 📤", key="send_chat", use_container_width=True):
                if user_q:
                    st.session_state.chat_history.append({
                        "role": "user", "content": user_q
                    })
                    with st.spinner("🤔 Thinking..."):
                        chat_resp = groq_client.chat.completions.create(
                            model="llama-3.1-8b-instant",
                            messages=[
                                {"role": "system", "content":
                                    f"Helpful travel assistant. Trip: {trip_days} days to "
                                    f"{destination}. Budget: {budget}. "
                                    f"Itinerary: {result[:1500]}. Be concise and helpful."},
                                *st.session_state.chat_history
                            ],
                            max_tokens=500, temperature=0.7
                        )
                        answer = chat_resp.choices[0].message.content
                        st.session_state.chat_history.append({
                            "role": "assistant", "content": answer
                        })
                    st.rerun()

        if st.button("🗑️ CLEAR CHAT HISTORY", key="clear_chat"):
            st.session_state.chat_history = []
            st.rerun()

    # ══════════════════════════════════════
    # BOOKING LINKS
    # ══════════════════════════════════════
    st.markdown("---")
    st.markdown('<div class="section-title">✈️ BOOK YOUR JOURNEY</div>',
                unsafe_allow_html=True)
    dest_enc = urllib.parse.quote(destination)
    from_enc = urllib.parse.quote(from_city) if from_city else ""
    bk1,bk2,bk3,bk4,bk5 = st.columns(5)
    blinks = [
        (bk1,"✈️","SKYSCANNER","FLIGHTS",
         f"https://www.skyscanner.co.in/transport/flights/{from_enc}/{dest_enc}/"
         if from_enc else f"https://www.skyscanner.co.in/"),
        (bk2,"🛫","MAKEMYTRIP","FLIGHTS+HOTELS","https://www.makemytrip.com/flights/"),
        (bk3,"🚂","IRCTC","TRAINS","https://www.irctc.co.in/nget/train-search"),
        (bk4,"🚌","REDBUS","BUS",f"https://www.redbus.in/bus-tickets/{dest_enc}"),
        (bk5,"🏨","BOOKING","HOTELS",
         f"https://www.booking.com/searchresults.html?ss={dest_enc}"),
    ]
    for col,emoji,name,sub,url in blinks:
        with col:
            col.markdown(
                f'<a href="{url}" target="_blank" style="text-decoration:none;">'
                f'<div class="booking-card"><div style="font-size:1.8rem;">{emoji}</div>'
                f'<div style="color:#38bdf8;font-weight:800;font-size:0.8rem;">{name}</div>'
                f'<div style="color:#bae6fd;font-size:0.7rem;">{sub}</div>'
                f'</div></a>', unsafe_allow_html=True)

    # GOOGLE MAPS
    st.markdown("---")
    st.markdown('<div class="section-title">🗺️ EXPLORE ON GOOGLE MAPS</div>',
                unsafe_allow_html=True)
    m1,m2,m3 = st.columns(3)
    for col,emoji,label,url in [
        (m1,"🏛️","ATTRACTIONS",f"https://www.google.com/maps/search/{dest_enc}+tourist+attractions"),
        (m2,"🏨","BUDGET HOTELS",f"https://www.google.com/maps/search/budget+hotels+{dest_enc}"),
        (m3,"🍽️","RESTAURANTS",f"https://www.google.com/maps/search/local+food+{dest_enc}"),
    ]:
        with col:
            col.markdown(
                f'<a href="{url}" target="_blank" style="text-decoration:none;">'
                f'<div class="booking-card" style="padding:18px 10px;">'
                f'<div style="font-size:2rem;">{emoji}</div>'
                f'<div style="color:#38bdf8;font-weight:800;font-size:0.85rem;'
                f'text-transform:uppercase;margin-top:8px;">{label}</div>'
                f'<div style="color:#7dd3fc;font-size:0.75rem;">OPEN IN MAPS</div>'
                f'</div></a>', unsafe_allow_html=True)

    # SAVE & SHARE
    st.markdown("---")
    st.markdown('<div class="section-title">📤 SAVE OR SHARE</div>', unsafe_allow_html=True)
    c1,c2,c3 = st.columns(3)

    with c1:
        try:
            pdf_b = create_pdf(result, from_city, destination,
                               trip_days, budget, travel_dates, travelers)
            st.download_button("📄 DOWNLOAD PDF", data=pdf_b,
                file_name=f"MANISH_{destination.replace(' ','_').upper()}_TRIP.pdf",
                mime="application/pdf", use_container_width=True)
        except Exception:
            st.download_button("📥 DOWNLOAD TEXT", data=result,
                file_name=f"MANISH_{destination.replace(' ','_').upper()}_TRIP.txt",
                mime="text/plain", use_container_width=True)

    with c2:
        route_s = (f"{from_city.upper()} → {destination.upper()}"
                  if from_city else destination.upper())
        share   = (f"✈️ *{trip_days}-DAY TRIP: {route_s}*\n"
                  f"📅 {travel_dates}\n👥 {travelers} travelers\n💰 {budget}\n\n"
                  f"{result[:400]}...\n\n"
                  f"🌍 Plan free: https://ai-travel-planner-h7f7ryewjbufa5tdvfewnu.streamlit.app")
        wa_url  = f"https://wa.me/?text={urllib.parse.quote(share)}"
        st.markdown(
            f'<a href="{wa_url}" target="_blank" style="text-decoration:none;">'
            f'<div style="background:linear-gradient(135deg,#15803d,#22c55e);'
            f'color:white;padding:13px;border-radius:10px;font-weight:900;'
            f'font-size:0.9rem;text-transform:uppercase;text-align:center;'
            f'box-shadow:0 4px 15px rgba(34,197,94,0.4);">📱 SHARE ON WHATSAPP</div></a>',
            unsafe_allow_html=True)

    with c3:
        with st.expander("📧 EMAIL ITINERARY"):
            user_email = st.text_input("EMAIL", placeholder="you@gmail.com",
                                       key="email_input")
            if st.button("📧 SEND EMAIL", key="send_email", use_container_width=True):
                if not user_email or "@" not in user_email:
                    st.error("⚠️ ENTER VALID EMAIL!")
                elif not EMAIL_SENDER:
                    st.warning("⚠️ EMAIL NOT CONFIGURED IN SECRETS!")
                else:
                    with st.spinner("Sending..."):
                        r = send_email_fn(user_email, from_city, destination,
                                         result, trip_days, travel_dates, budget)
                        if r is True: st.success(f"✅ SENT TO {user_email}!")
                        else: st.error(f"❌ FAILED: {r}")

# FOOTER
st.markdown("---")
st.markdown('<div class="footer">BUILT WITH ❤️ USING GROQ AI + TAVILY + STREAMLIT</div>',
            unsafe_allow_html=True)
st.markdown('<div class="footer-brand">© 2025 MANISH TRAVEL ITINERARY PLANNER — ALL RIGHTS RESERVED</div>',
            unsafe_allow_html=True)
