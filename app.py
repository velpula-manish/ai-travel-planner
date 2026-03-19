import streamlit as st
import os
import requests
import urllib.parse
import datetime
import re
import smtplib
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
.route-box {
    background: linear-gradient(135deg,rgba(2,132,199,0.25),rgba(3,105,161,0.35));
    border: 1.5px solid #38bdf8; border-radius: 14px;
    padding: 15px 20px; margin: 10px 0;
    box-shadow: 0 4px 15px rgba(56,189,248,0.15);
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
    box-shadow: 0 6px 20px rgba(56,189,248,0.4) !important;
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
.stButton > button:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 14px 40px rgba(56,189,248,0.6) !important;
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
.stSelectbox > div > div > div { color: #ffffff !important; }
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
    letter-spacing: 1px !important; border-radius: 10px !important;
    border: none !important; padding: 12px !important;
    box-shadow: 0 4px 15px rgba(37,99,235,0.4) !important;
    width: 100% !important;
}
hr { border-color: rgba(56,189,248,0.3) !important; }
.footer {
    text-align: center; text-transform: uppercase; letter-spacing: 2px;
    opacity: 0.5; font-size: 0.75rem; margin-top: 5px;
    color: #38bdf8 !important;
}
.footer-brand {
    text-align: center; text-transform: uppercase; letter-spacing: 3px;
    font-size: 0.7rem; color: #38bdf8 !important;
    opacity: 0.6; margin-top: 3px;
}
</style>
""", unsafe_allow_html=True)

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
    - 🎨 **STREAMLIT** — BEAUTIFUL UI
    """)
    st.markdown("---")
    st.markdown("### 📌 HOW TO USE")
    st.markdown("""
    1. ENTER **FROM & TO CITIES**
    2. CLICK A **POPULAR DESTINATION**
    3. SET **TRIP DURATION**
    4. CHOOSE **CURRENCY & BUDGET**
    5. SELECT **TRAVEL DATES**
    6. PICK YOUR **INTERESTS**
    7. CLICK **GENERATE** AND WAIT!
    8. **BOOK TICKETS** OR **SHARE**!
    """)
    st.markdown("---")
    st.markdown("### ✈️ FEATURES")
    st.markdown("""
    - 🗺️ FULL JOURNEY PLANNING
    - 🌤️ LIVE WEATHER INFO
    - 🌐 MULTI-LANGUAGE SUPPORT
    - 💰 STRICT BUDGET PLANNER
    - 🏨 BUDGET-MATCHED HOTELS
    - 🍽️ AFFORDABLE RESTAURANTS
    - 🗺️ GOOGLE MAPS LINKS
    - ✈️ FLIGHT/TRAIN/BUS BOOKING
    - 📧 EMAIL ITINERARY
    - 📄 PDF DOWNLOAD
    - 📱 WHATSAPP SHARING
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
st.markdown(
    '<div class="subtitle">YOUR PERSONAL AI TRAVEL AGENT'
    ' — POWERED BY GROQ + TAVILY</div>',
    unsafe_allow_html=True
)
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

if "selected_destination" not in st.session_state:
    st.session_state.selected_destination = ""
if "itinerary_ready" not in st.session_state:
    st.session_state.itinerary_ready = False

popular_destinations = [
    ("🗼","PARIS"),    ("🗽","NEW YORK"), ("🏯","TOKYO"),   ("🕌","DUBAI"),
    ("🏛️","ROME"),     ("🌴","BALI"),     ("🐘","KERALA"),  ("⛩️","RAJASTHAN"),
    ("🏔️","MANALI"),   ("🌊","GOA"),      ("🏰","LONDON"),  ("🗺️","SINGAPORE"),
]

dest_cols = st.columns(4)
for i, (emoji, city) in enumerate(popular_destinations):
    with dest_cols[i % 4]:
        if st.button(f"{emoji} {city}", key=f"dest_{i}",
                     use_container_width=True):
            st.session_state.selected_destination = city.title()
            st.rerun()

st.markdown("---")

# ══════════════════════════════════════
# ROUTE SECTION — FROM & TO
# ══════════════════════════════════════
st.markdown(
    '<div class="section-title">🗺️ YOUR JOURNEY ROUTE</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="route-box">',
    unsafe_allow_html=True
)
r1, r2, r3 = st.columns([2, 1, 2])
with r1:
    from_city = st.text_input(
        "🏠 STARTING FROM",
        placeholder="e.g. Mumbai, Delhi, Chennai..."
    )
with r2:
    st.markdown(
        "<div style='text-align:center;font-size:2rem;"
        "padding-top:25px;'>✈️</div>",
        unsafe_allow_html=True
    )
with r3:
    to_city = st.text_input(
        "📍 GOING TO",
        value=st.session_state.selected_destination,
        placeholder="e.g. Paris, Goa, Tokyo..."
    )
    if to_city != st.session_state.selected_destination:
        st.session_state.selected_destination = to_city

st.markdown('</div>', unsafe_allow_html=True)

# Use to_city as destination
destination = to_city

st.markdown("---")

# ══════════════════════════════════════
# DURATION SLIDER — RENDERED FIRST
# so auto-fill date works correctly
# ══════════════════════════════════════
st.markdown(
    '<div class="section-title">📝 TRIP DETAILS</div>',
    unsafe_allow_html=True
)

duration = st.slider("📅 TRIP DURATION (DAYS)", 1, 14, 3)
st.markdown(
    f"<p style='color:#38bdf8;font-weight:700;font-size:0.85rem;'>"
    f"✅ SELECTED: {duration} DAY(S)</p>",
    unsafe_allow_html=True
)

col1, col2 = st.columns(2)

with col1:
    # ══════════════════════════════════════
    # WEATHER
    # ══════════════════════════════════════
    if destination and len(destination.strip()) > 2:
        weather_placeholder = st.empty()
        try:
            geo = requests.get(
                "https://geocoding-api.open-meteo.com/v1/search",
                params={"name": destination, "count": 1,
                        "language": "en", "format": "json"},
                timeout=8
            ).json()

            if geo.get("results"):
                lat     = geo["results"][0]["latitude"]
                lon     = geo["results"][0]["longitude"]
                city_n  = geo["results"][0].get("name", destination)
                country = geo["results"][0].get("country", "")

                wx = requests.get(
                    "https://api.open-meteo.com/v1/forecast",
                    params={
                        "latitude": lat, "longitude": lon,
                        "current_weather": "true",
                        "hourly": "relativehumidity_2m,precipitation_probability",
                        "timezone": "auto", "forecast_days": 1
                    },
                    timeout=8
                ).json()

                if "current_weather" in wx:
                    cw    = wx["current_weather"]
                    temp  = cw.get("temperature", "—")
                    wind  = cw.get("windspeed", "—")
                    wcode = cw.get("weathercode", 0)
                    hum   = wx.get("hourly", {}).get(
                        "relativehumidity_2m", ["—"])[0]
                    rain  = wx.get("hourly", {}).get(
                        "precipitation_probability", ["—"])[0]
                    codes = {
                        0:"☀️ Clear Sky",1:"🌤️ Mainly Clear",
                        2:"⛅ Partly Cloudy",3:"☁️ Overcast",
                        45:"🌫️ Foggy",51:"🌦️ Drizzle",
                        61:"🌧️ Light Rain",63:"🌧️ Moderate Rain",
                        65:"🌧️ Heavy Rain",71:"🌨️ Snow",
                        80:"🌦️ Showers",95:"⛈️ Thunderstorm",
                    }
                    cond = codes.get(wcode, "🌡️ Clear")
                    weather_placeholder.markdown(
                        f'<div class="weather-box">'
                        f'<strong>🌤️ LIVE WEATHER'
                        f' — {city_n.upper()}, {country.upper()}</strong><br>'
                        f'🌡️ TEMP: <strong>{temp}°C</strong>'
                        f' &nbsp;|&nbsp; {cond}<br>'
                        f'💨 WIND: {wind} km/h'
                        f' &nbsp;|&nbsp; 💧 HUMIDITY: {hum}%'
                        f' &nbsp;|&nbsp; 🌧️ RAIN: {rain}%'
                        f'</div>',
                        unsafe_allow_html=True
                    )
        except Exception:
            pass

    # ══════════════════════════════════════
    # BUDGET — WITH SMART ANALYSIS
    # ══════════════════════════════════════
    st.markdown("##### 💰 BUDGET")
    b1, b2 = st.columns([1, 2])
    with b1:
        currency = st.selectbox(
            "CURRENCY",
            ["₹ INR", "$ USD", "€ EUR", "£ GBP"],
            index=0
        )
    with b2:
        ph_map = {
            "INR": ("e.g. 50000", "₹20,000–₹2,00,000"),
            "USD": ("e.g. 1500",  "$500–$10,000"),
            "EUR": ("e.g. 1200",  "€500–€8,000"),
            "GBP": ("e.g. 1000",  "£400–£7,000"),
        }
        curr_key      = [k for k in ph_map if k in currency][0]
        ph, hint      = ph_map[curr_key]
        budget_amount = st.text_input("AMOUNT", placeholder=ph, help=hint)

    # ══════════════════════════════════════
    # SMART BUDGET ANALYSIS
    # ══════════════════════════════════════
    budget_status = "unknown"
    budget_tier   = ""

    if budget_amount:
        try:
            amt     = float(budget_amount.replace(",", ""))
            per_day = amt / max(duration, 1)

            # Min cost per day estimates
            min_costs = {
                "INR": 1500,   # ₹1500/day minimum
                "USD": 50,     # $50/day minimum
                "EUR": 45,     # €45/day minimum
                "GBP": 40,     # £40/day minimum
            }
            comfort_costs = {
                "INR": 4000,
                "USD": 150,
                "EUR": 130,
                "GBP": 110,
            }
            luxury_costs = {
                "INR": 10000,
                "USD": 300,
                "EUR": 250,
                "GBP": 220,
            }

            min_c     = min_costs[curr_key]
            comfort_c = comfort_costs[curr_key]
            luxury_c  = luxury_costs[curr_key]

            if per_day < min_c:
                budget_status = "low"
                budget_tier   = "BUDGET"
                st.markdown(
                    f'<div class="budget-warning">'
                    f'⚠️ BUDGET MAY BE TOO LOW!<br>'
                    f'Your daily budget: <strong>{currency} {per_day:.0f}/day</strong><br>'
                    f'Minimum needed: <strong>{currency} {min_c}/day</strong><br>'
                    f'💡 RECOMMENDATION: Increase to at least '
                    f'<strong>{currency} {min_c * duration:.0f}</strong> '
                    f'for a basic {duration}-day trip. '
                    f'AI will still plan with your budget but options will be very limited!'
                    f'</div>',
                    unsafe_allow_html=True
                )
            elif per_day < comfort_c:
                budget_status = "ok"
                budget_tier   = "BUDGET"
                st.markdown(
                    f'<div class="budget-ok">'
                    f'✅ BUDGET LOOKS GOOD FOR A STUDENT TRIP!<br>'
                    f'Daily budget: <strong>{currency} {per_day:.0f}/day</strong><br>'
                    f'🎒 This covers: Budget hotels, local food, public transport & key attractions!'
                    f'</div>',
                    unsafe_allow_html=True
                )
            elif per_day < luxury_c:
                budget_status = "comfortable"
                budget_tier   = "MODERATE"
                st.markdown(
                    f'<div class="budget-ok">'
                    f'✅ COMFORTABLE BUDGET!<br>'
                    f'Daily budget: <strong>{currency} {per_day:.0f}/day</strong><br>'
                    f'🏨 This covers: Mid-range hotels, good restaurants & most attractions!'
                    f'</div>',
                    unsafe_allow_html=True
                )
            else:
                budget_status = "luxury"
                budget_tier   = "LUXURY"
                st.markdown(
                    f'<div class="budget-ok">'
                    f'💎 LUXURY BUDGET!<br>'
                    f'Daily budget: <strong>{currency} {per_day:.0f}/day</strong><br>'
                    f'🌟 This covers: Premium hotels, fine dining & exclusive experiences!'
                    f'</div>',
                    unsafe_allow_html=True
                )
        except Exception:
            pass

    budget = (f"{currency} {budget_amount}"
              if budget_amount else f"{currency} (not specified)")

with col2:
    # ══════════════════════════════════════
    # DATE PICKER — AUTO-FILL FIXED
    # ══════════════════════════════════════
    st.markdown(
        "<p style='color:#e0f2fe;font-weight:700;"
        "font-size:0.9rem;margin-bottom:4px;'>🗓️ TRAVEL DATES</p>",
        unsafe_allow_html=True
    )

    today     = datetime.date.today()
    default_s = today + datetime.timedelta(days=7)

    dc1, dc2  = st.columns(2)
    with dc1:
        start_date = st.date_input(
            "FROM DATE ✈️",
            value=default_s,
            min_value=today,
            key="start_date_input"
        )
    with dc2:
        # ✅ AUTO-FILL: To Date = From Date + duration
        auto_end = start_date + datetime.timedelta(days=duration)
        end_date = st.date_input(
            "TO DATE 🏁",
            value=auto_end,
            min_value=today,
            key="end_date_input"
        )

    if end_date <= start_date:
        st.warning("⚠️ TO DATE MUST BE AFTER FROM DATE!")
        travel_dates = start_date.strftime('%d %b %Y')
        trip_days    = duration
    else:
        trip_days    = (end_date - start_date).days
        travel_dates = (
            f"{start_date.strftime('%d %b %Y')} "
            f"to {end_date.strftime('%d %b %Y')}"
        )
        st.markdown(
            f"<p style='color:#38bdf8;font-weight:700;font-size:0.85rem;'>"
            f"✅ {trip_days} DAY TRIP: "
            f"{start_date.strftime('%d %b')} → "
            f"{end_date.strftime('%d %b %Y')}</p>",
            unsafe_allow_html=True
        )

    travelers = st.number_input("👥 NUMBER OF TRAVELERS", 1, 20, 2)

    language = st.selectbox(
        "🌐 OUTPUT LANGUAGE",
        options=[
            "English",
            "Hindi — हिन्दी",
            "Tamil — தமிழ்",
            "Telugu — తెలుగు",
            "Kannada — ಕನ್ನಡ",
            "Malayalam — മലയാളം",
            "Bengali — বাংলা",
            "Marathi — मराठी",
            "French — Français",
            "Spanish — Español",
            "Arabic — عربي",
            "Japanese — 日本語",
        ],
        index=0,
        help="AI WILL WRITE YOUR ITINERARY IN THIS LANGUAGE!"
    )
    lang_name = language.split("—")[0].strip()

    interests = st.multiselect(
        "❤️ YOUR INTERESTS",
        [
            "🏛️ HISTORY & CULTURE",  "🍽️ FOOD & DINING",
            "🎨 ART & MUSEUMS",       "🌿 NATURE & OUTDOORS",
            "🛍️ SHOPPING",            "🎭 NIGHTLIFE",
            "🏖️ BEACH & RELAXATION",  "🏔️ ADVENTURE & SPORTS",
            "📸 PHOTOGRAPHY",         "👨‍👩‍👧 FAMILY FRIENDLY"
        ],
        default=["🍽️ FOOD & DINING", "🎨 ART & MUSEUMS"]
    )

special_requirements = st.text_area(
    "💬 SPECIAL REQUIREMENTS (OPTIONAL)",
    placeholder="e.g. Vegetarian food, student trip, budget-friendly only...",
    height=80
)
st.markdown("---")


# ══════════════════════════════════════
# PDF GENERATOR
# ══════════════════════════════════════
def create_pdf(content, from_city, destination, duration,
               budget, travel_dates, travelers):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(2, 132, 199)
    pdf.rect(0, 0, 210, 35, 'F')
    pdf.set_font("Arial", "B", 20)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 12, "AI TRAVEL ITINERARY PLANNER", ln=True, align="C")
    pdf.set_font("Arial", "B", 13)
    pdf.cell(0, 8, "BY MANISH TRAVEL PLANNER", ln=True, align="C")
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 8,
             "ai-travel-planner-h7f7ryewjbufa5tdvfewnu.streamlit.app",
             ln=True, align="C")
    pdf.set_fill_color(224, 242, 254)
    pdf.rect(10, 40, 190, 35, 'F')
    pdf.set_text_color(2, 132, 199)
    pdf.set_font("Arial", "B", 11)
    pdf.set_xy(12, 42)
    route = f"{from_city.upper()} → {destination.upper()}" if from_city else destination.upper()
    pdf.cell(0, 6, f"ROUTE: {route}  |  DURATION: {duration} DAYS  |  TRAVELERS: {travelers}", ln=True)
    pdf.set_xy(12, 50)
    pdf.cell(0, 6, f"DATES: {travel_dates}  |  BUDGET: {budget}", ln=True)
    pdf.set_xy(10, 80)
    pdf.set_text_color(30, 30, 30)
    pdf.set_font("Arial", "", 10)
    clean = re.sub(r'[^\x00-\x7F]+', '', content)
    clean = clean.replace("##", "\n").replace("**", "")
    for line in clean.split('\n'):
        line = line.strip()
        if not line:
            pdf.ln(3)
            continue
        if line.startswith("###"):
            pdf.set_font("Arial", "B", 11)
            pdf.set_text_color(2, 132, 199)
            pdf.multi_cell(0, 7, line.replace("###", "").strip())
            pdf.set_font("Arial", "", 10)
            pdf.set_text_color(30, 30, 30)
        elif line.startswith("#"):
            pdf.set_font("Arial", "B", 12)
            pdf.set_text_color(1, 63, 120)
            pdf.multi_cell(0, 8, line.replace("#", "").strip())
            pdf.set_font("Arial", "", 10)
            pdf.set_text_color(30, 30, 30)
        else:
            pdf.multi_cell(0, 6, line)
    pdf.set_y(-20)
    pdf.set_fill_color(2, 132, 199)
    pdf.rect(0, pdf.get_y(), 210, 20, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 9)
    pdf.cell(0, 8, "© MANISH TRAVEL PLANNER — ALL RIGHTS RESERVED", align="C")
    return pdf.output(dest='S').encode('latin-1')


# ══════════════════════════════════════
# EMAIL SENDER
# ══════════════════════════════════════
def send_email(to_email, from_city, destination, itinerary,
               duration, travel_dates, budget):
    try:
        route = f"{from_city} → {destination}" if from_city else destination
        msg   = MIMEMultipart("alternative")
        msg["Subject"] = f"✈️ YOUR {duration}-DAY {destination.upper()} TRAVEL ITINERARY"
        msg["From"]    = EMAIL_SENDER
        msg["To"]      = to_email
        html_body = f"""
        <html><body style="font-family:Arial;background:#0c1445;color:#e0f2fe;padding:20px;">
        <div style="max-width:700px;margin:auto;background:#1a237e;border-radius:16px;overflow:hidden;">
            <div style="background:#0284c7;padding:25px;text-align:center;">
                <h1 style="color:white;text-transform:uppercase;letter-spacing:3px;margin:0;">
                    🌍 AI TRAVEL ITINERARY PLANNER
                </h1>
                <p style="color:#bae6fd;text-transform:uppercase;letter-spacing:2px;margin:5px 0;">
                    BY MANISH TRAVEL PLANNER
                </p>
            </div>
            <div style="padding:20px;background:#e0f2fe;color:#0c1445;">
                <table style="width:100%;background:#bae6fd;border-radius:10px;padding:15px;margin-bottom:20px;">
                    <tr>
                        <td><strong>✈️ ROUTE:</strong> {route.upper()}</td>
                        <td><strong>📅 DURATION:</strong> {duration} DAYS</td>
                    </tr>
                    <tr>
                        <td><strong>🗓️ DATES:</strong> {travel_dates}</td>
                        <td><strong>💰 BUDGET:</strong> {budget}</td>
                    </tr>
                </table>
                <div style="white-space:pre-wrap;font-size:14px;line-height:1.8;color:#1a237e;">
                    {itinerary}
                </div>
            </div>
            <div style="background:#0284c7;padding:15px;text-align:center;">
                <p style="color:white;font-size:12px;margin:0;text-transform:uppercase;letter-spacing:1px;">
                    © MANISH TRAVEL PLANNER — ALL RIGHTS RESERVED<br>
                    <a href="https://ai-travel-planner-h7f7ryewjbufa5tdvfewnu.streamlit.app"
                       style="color:#bae6fd;">PLAN MORE TRIPS FOR FREE</a>
                </p>
            </div>
        </div>
        </body></html>
        """
        msg.attach(MIMEText(html_body, "html"))
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, to_email, msg.as_string())
        return True
    except Exception as e:
        return str(e)


# ══════════════════════════════════════
# ITINERARY GENERATOR
# ══════════════════════════════════════
def generate_itinerary(from_city, destination, duration, budget,
                        travel_dates, travelers, interests,
                        special_requirements, lang_name,
                        budget_tier, budget_status):
    tavily = TavilyClient(api_key=TAVILY_API_KEY)
    try:
        res = tavily.search(
            query=f"budget travel guide {destination} cheap hotels food transport",
            max_results=3, search_depth="basic"
        )
        web_info = "\n".join([
            f"- {r.get('title','')}: {r.get('content','')[:300]}"
            for r in res.get("results", [])
        ])
    except Exception:
        web_info = "Popular destination."

    groq_client    = Groq(api_key=GROQ_API_KEY)
    interests_text = ", ".join(interests) if interests else "General Sightseeing"
    special_text   = special_requirements or "None"
    curr_symbol    = budget.split()[0]
    route          = f"{from_city} to {destination}" if from_city else destination

    # Budget instructions for AI
    if budget_status == "low":
        budget_instruction = f"""
CRITICAL BUDGET ALERT:
The traveler has a VERY LIMITED budget of {budget} for {duration} days.
Daily budget is below minimum recommended.
YOU MUST:
- Only suggest FREE or very cheap attractions
- Only suggest dormitory/hostel/budget guesthouses under {curr_symbol} 500/night
- Only suggest street food, local dhabas, cheap eateries
- Clearly warn at the start: "⚠️ BUDGET WARNING: YOUR BUDGET IS VERY TIGHT..."
- Give money-saving tips throughout
- Be honest if certain activities are not affordable
"""
    elif budget_tier == "BUDGET":
        budget_instruction = f"""
BUDGET TYPE: STUDENT/BUDGET TRAVELER
Budget: {budget} for {duration} days.
YOU MUST STRICTLY:
- Only suggest budget hotels (hostels, guesthouses, budget hotels)
- Only suggest affordable local restaurants and street food
- Suggest free or low-cost attractions
- Use public transport only (no private taxis unless necessary)
- Give student discounts and money saving tips
- NEVER suggest luxury hotels, fine dining, or expensive activities
- All recommendations MUST fit within the total budget of {budget}
"""
    elif budget_tier == "MODERATE":
        budget_instruction = f"""
BUDGET TYPE: MODERATE/MID-RANGE
Budget: {budget} for {duration} days.
Suggest mid-range hotels, good restaurants, mix of paid and free attractions.
Avoid luxury options. Focus on value for money.
"""
    else:
        budget_instruction = f"""
BUDGET TYPE: LUXURY
Budget: {budget} for {duration} days.
Suggest premium hotels, fine dining, exclusive experiences.
"""

    prompt = f"""You are an expert AI Travel Planner with 20 years experience.
IMPORTANT: Write the ENTIRE response in {lang_name} language only.

Real-time info about {destination}: {web_info}

{budget_instruction}

Create a COMPLETE journey plan from {route}:
- Full Route: {route}
- Travel Dates: {travel_dates}
- Total Budget: {budget} (STRICT — do not exceed this!)
- Travelers: {travelers}
- Interests: {interests_text}
- Notes: {special_text}

## 🚀 JOURNEY OVERVIEW
[Briefly describe the full journey from {from_city if from_city else "starting point"} to {destination}]

## 🚌 HOW TO REACH {destination.upper()} FROM {from_city.upper() if from_city else "YOUR CITY"}
[Give transport options: flight/train/bus with approximate costs in {curr_symbol}]
[Include booking tips and which option suits the budget]

## 🌍 DESTINATION OVERVIEW
[4 sentences about {destination}]

## 📅 DAY-BY-DAY ITINERARY
### DAY 1 — ARRIVAL & CHECK-IN
- **MORNING:** [Travel from {from_city if from_city else "home city"} — departure details]
- **AFTERNOON:** [Arrival, check-in at budget accommodation]
- **EVENING:** [First evening activity + dinner]

[Continue Day 2 to Day {duration}, each with unique theme]

### DAY {duration} — DEPARTURE
- **MORNING:** [Check-out + last activity]
- **AFTERNOON:** [Return journey to {from_city if from_city else "home"}]
- **EVENING:** [Arrival back home]

## 🏨 ACCOMMODATION RECOMMENDATIONS
[STRICTLY match to {budget_tier} budget — {budget} total]
1. **[NAME]** — [{curr_symbol}/night] — [budget-appropriate description]
2. **[NAME]** — [{curr_symbol}/night] — [budget-appropriate description]
3. **[NAME]** — [{curr_symbol}/night] — [budget-appropriate description]

## 🍽️ WHERE TO EAT (BUDGET-FRIENDLY)
1. **[NAME]** — [cuisine] — [dish] — [cost in {curr_symbol}]
2. **[NAME]** — [cuisine] — [dish] — [cost in {curr_symbol}]
3. **[NAME]** — [cuisine] — [dish] — [cost in {curr_symbol}]
4. **[NAME]** — [cuisine] — [dish] — [cost in {curr_symbol}]
5. **[NAME]** — [cuisine] — [dish] — [cost in {curr_symbol}]

## 💰 COMPLETE BUDGET BREAKDOWN
- **TRANSPORT TO/FROM {destination.upper()}:** [{curr_symbol}]
- **LOCAL TRANSPORT:** [{curr_symbol}] total
- **ACCOMMODATION:** [{curr_symbol}/night × {duration} nights]
- **FOOD:** [{curr_symbol}/day × {duration} days]
- **ACTIVITIES/ENTRY FEES:** [{curr_symbol}] total
- **MISCELLANEOUS:** [{curr_symbol}]
- **TOTAL SPENT: [{curr_symbol}]**
- **REMAINING FROM BUDGET: [{curr_symbol}]** (from total {budget})

## 💡 MONEY-SAVING TIPS
1. [tip] 2. [tip] 3. [tip] 4. [tip] 5. [tip]

## 🚗 LOCAL TRANSPORT IN {destination.upper()}
[Options with costs — prefer budget options]

## 🎒 PACKING LIST
[10 essential items for this trip]
"""

    resp = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system",
             "content": (
                 f"Expert travel planner. Write entirely in {lang_name}. "
                 f"STRICTLY plan within the budget of {budget}. "
                 "Never suggest options that exceed the given budget."
             )},
            {"role": "user", "content": prompt}
        ],
        max_tokens=3000,
        temperature=0.7
    )
    return resp.choices[0].message.content


# ══════════════════════════════════════
# GENERATE BUTTON
# ══════════════════════════════════════
generate_btn = st.button(
    "🚀 GENERATE MY COMPLETE TRAVEL PLAN!",
    use_container_width=True
)

if generate_btn:
    if not destination:
        st.error("⚠️ PLEASE ENTER YOUR DESTINATION (GOING TO)!")
    elif end_date <= start_date:
        st.error("⚠️ PLEASE SELECT VALID TRAVEL DATES!")
    elif not budget_amount:
        st.error("⚠️ PLEASE ENTER YOUR BUDGET AMOUNT!")
    else:
        with st.spinner(
            "🔍 AI IS PLANNING YOUR COMPLETE JOURNEY... ⏳"
        ):
            try:
                result = generate_itinerary(
                    from_city, destination, trip_days,
                    budget, travel_dates, travelers,
                    interests, special_requirements,
                    lang_name, budget_tier, budget_status
                )
                st.session_state.itinerary_result    = result
                st.session_state.itinerary_dest      = destination
                st.session_state.itinerary_from      = from_city
                st.session_state.itinerary_ready     = True
            except Exception as e:
                st.error(f"❌ ERROR: {str(e)}")
                st.info("💡 PLEASE TRY AGAIN IN A FEW SECONDS!")


# ══════════════════════════════════════
# SHOW RESULTS
# ══════════════════════════════════════
if st.session_state.get("itinerary_ready"):
    result      = st.session_state.itinerary_result
    destination = st.session_state.itinerary_dest
    from_city   = st.session_state.get("itinerary_from", "")

    st.markdown("---")
    st.markdown(
        '<div class="success-header">✅ YOUR COMPLETE TRAVEL PLAN IS READY!</div>',
        unsafe_allow_html=True
    )
    st.markdown('<div class="result-container">', unsafe_allow_html=True)
    st.markdown(result)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("---")

    # ══════════════════════════════════════
    # BOOKING LINKS
    # ══════════════════════════════════════
    st.markdown(
        '<div class="section-title">✈️ BOOK YOUR JOURNEY</div>',
        unsafe_allow_html=True
    )
    dest_enc = urllib.parse.quote(destination)
    from_enc = urllib.parse.quote(from_city) if from_city else ""

    bk1, bk2, bk3, bk4, bk5 = st.columns(5)
    booking_links = [
        (bk1,"✈️","SKYSCANNER","FLIGHTS",
         f"https://www.skyscanner.co.in/transport/flights/{from_enc}/{dest_enc}/"
         if from_enc else
         f"https://www.skyscanner.co.in/transport/flights/{dest_enc}/"),
        (bk2,"🛫","MAKEMYTRIP","FLIGHTS + HOTELS",
         "https://www.makemytrip.com/flights/"),
        (bk3,"🚂","IRCTC","TRAIN TICKETS",
         "https://www.irctc.co.in/nget/train-search"),
        (bk4,"🚌","REDBUS","BUS TICKETS",
         f"https://www.redbus.in/bus-tickets/{dest_enc}"),
        (bk5,"🏨","BOOKING.COM","HOTELS",
         f"https://www.booking.com/searchresults.html?ss={dest_enc}"),
    ]
    for col, emoji, name, sub, url in booking_links:
        with col:
            col.markdown(
                f'<a href="{url}" target="_blank" style="text-decoration:none;">'
                f'<div class="booking-card">'
                f'<div style="font-size:1.8rem;">{emoji}</div>'
                f'<div style="color:#38bdf8;font-weight:800;'
                f'font-size:0.8rem;text-transform:uppercase;margin-top:5px;">{name}</div>'
                f'<div style="color:#bae6fd;font-size:0.7rem;">{sub}</div>'
                f'</div></a>',
                unsafe_allow_html=True
            )

    # ══════════════════════════════════════
    # GOOGLE MAPS
    # ══════════════════════════════════════
    st.markdown("---")
    st.markdown(
        '<div class="section-title">🗺️ EXPLORE ON GOOGLE MAPS</div>',
        unsafe_allow_html=True
    )
    m1, m2, m3 = st.columns(3)
    maps_links = [
        (m1,"🏛️","TOURIST ATTRACTIONS",
         f"https://www.google.com/maps/search/{dest_enc}+tourist+attractions"),
        (m2,"🏨","BUDGET HOTELS",
         f"https://www.google.com/maps/search/budget+hotels+in+{dest_enc}"),
        (m3,"🍽️","LOCAL RESTAURANTS",
         f"https://www.google.com/maps/search/local+restaurants+in+{dest_enc}"),
    ]
    for col, emoji, label, url in maps_links:
        with col:
            col.markdown(
                f'<a href="{url}" target="_blank" style="text-decoration:none;">'
                f'<div class="booking-card" style="padding:18px 10px;">'
                f'<div style="font-size:2rem;">{emoji}</div>'
                f'<div style="color:#38bdf8;font-weight:800;font-size:0.85rem;'
                f'text-transform:uppercase;margin-top:8px;">{label}</div>'
                f'<div style="color:#7dd3fc;font-size:0.75rem;margin-top:3px;">'
                f'OPEN IN GOOGLE MAPS</div>'
                f'</div></a>',
                unsafe_allow_html=True
            )

    # ══════════════════════════════════════
    # SAVE & SHARE
    # ══════════════════════════════════════
    st.markdown("---")
    st.markdown(
        '<div class="section-title">📤 SAVE OR SHARE YOUR PLAN</div>',
        unsafe_allow_html=True
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        try:
            pdf_b = create_pdf(
                result, from_city, destination,
                trip_days, budget, travel_dates, travelers
            )
            route_name = (f"{from_city}_TO_{destination}".replace(' ','_').upper()
                         if from_city else destination.replace(' ','_').upper())
            st.download_button(
                label="📄 DOWNLOAD AS PDF",
                data=pdf_b,
                file_name=f"MANISH_{route_name}_TRIP.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except Exception:
            st.download_button(
                label="📥 DOWNLOAD AS TEXT",
                data=result,
                file_name=f"MANISH_{destination.replace(' ','_').upper()}_TRIP.txt",
                mime="text/plain",
                use_container_width=True
            )

    with c2:
        route_str = (f"{from_city.upper()} → {destination.upper()}"
                    if from_city else destination.upper())
        share_msg = (
            f"✈️ *{trip_days}-DAY TRIP: {route_str}*\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"📅 DATES: {travel_dates}\n"
            f"👥 TRAVELERS: {travelers}\n"
            f"💰 BUDGET: {budget}\n"
            f"🌐 LANGUAGE: {lang_name}\n"
            f"━━━━━━━━━━━━━━━━━━\n\n"
            f"{result[:500]}...\n\n"
            f"🌍 PLAN YOUR FREE TRIP:\n"
            f"https://ai-travel-planner-h7f7ryewjbufa5tdvfewnu.streamlit.app\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"_BY MANISH TRAVEL PLANNER_ 🗺️"
        )
        wa_url = f"https://wa.me/?text={urllib.parse.quote(share_msg)}"
        st.markdown(
            f'<a href="{wa_url}" target="_blank" style="text-decoration:none;">'
            f'<div style="background:linear-gradient(135deg,#15803d,#22c55e);'
            f'color:white;padding:13px;border-radius:10px;font-weight:900;'
            f'font-size:0.9rem;text-transform:uppercase;letter-spacing:1px;'
            f'text-align:center;cursor:pointer;'
            f'box-shadow:0 4px 15px rgba(34,197,94,0.4);">'
            f'📱 SHARE ON WHATSAPP'
            f'</div></a>',
            unsafe_allow_html=True
        )

    with c3:
        with st.expander("📧 EMAIL ITINERARY", expanded=False):
            user_email = st.text_input(
                "YOUR EMAIL ADDRESS",
                placeholder="yourname@gmail.com",
                key="email_input"
            )
            if st.button("📧 SEND TO MY EMAIL",
                         key="send_email",
                         use_container_width=True):
                if not user_email or "@" not in user_email:
                    st.error("⚠️ PLEASE ENTER VALID EMAIL!")
                elif not EMAIL_SENDER:
                    st.warning("⚠️ EMAIL NOT CONFIGURED IN SECRETS!")
                else:
                    with st.spinner("📧 SENDING..."):
                        r = send_email(
                            user_email, from_city,
                            destination, result,
                            trip_days, travel_dates, budget
                        )
                        if r is True:
                            st.success(f"✅ SENT TO {user_email}!")
                        else:
                            st.error(f"❌ FAILED: {r}")

# ══════════════════════════════════════
# FOOTER
# ══════════════════════════════════════
st.markdown("---")
st.markdown(
    '<div class="footer">'
    'BUILT WITH ❤️ USING GROQ AI + TAVILY + STREAMLIT'
    '</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="footer-brand">'
    '© 2025 MANISH TRAVEL ITINERARY PLANNER — ALL RIGHTS RESERVED'
    '</div>',
    unsafe_allow_html=True
)
