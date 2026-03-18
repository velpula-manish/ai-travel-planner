import streamlit as st
import os
import requests
import urllib.parse
from groq import Groq
from tavily import TavilyClient
from fpdf import FPDF
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re

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
    position: fixed;
    top: 45%; left: 55%;
    transform: translate(-50%, -50%) rotate(-30deg);
    font-size: 4.5rem; font-weight: 900;
    color: rgba(56,189,248,0.07);
    white-space: nowrap; pointer-events: none;
    z-index: 0; letter-spacing: 5px; text-transform: uppercase;
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
    color: #38bdf8; font-weight: 700; text-transform: uppercase; margin-bottom: 10px;
}
.section-title {
    font-size: 1.05rem; font-weight: 800; text-transform: uppercase;
    letter-spacing: 2px; color: #38bdf8 !important; margin-bottom: 10px;
    border-left: 4px solid #0284c7; padding-left: 10px;
}
.weather-box {
    background: linear-gradient(135deg, rgba(2,132,199,0.3), rgba(3,105,161,0.4));
    border: 1.5px solid #38bdf8; border-radius: 12px;
    padding: 12px 16px; margin: 8px 0 12px 0;
    font-size: 0.92rem; font-weight: 600;
    color: #e0f2fe !important; line-height: 1.9;
    box-shadow: 0 4px 15px rgba(56,189,248,0.2);
}
.booking-card {
    background: linear-gradient(135deg, rgba(2,132,199,0.2), rgba(3,105,161,0.3));
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
    color: #e0f2fe !important;
    font-size: 0.75rem !important; font-weight: 800 !important;
    height: 50px !important; min-height: 50px !important;
    max-height: 50px !important; padding: 2px 4px !important;
    border-radius: 10px !important; border: 1.5px solid #38bdf8 !important;
    text-transform: uppercase !important; letter-spacing: 0px !important;
    white-space: nowrap !important; overflow: visible !important;
    transition: all 0.2s !important; display: flex !important;
    align-items: center !important; justify-content: center !important;
    width: 100% !important; line-height: 1.2 !important; text-align: center !important;
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
    box-shadow: 0 4px 15px rgba(37,99,235,0.4) !important; width: 100% !important;
}
hr { border-color: rgba(56,189,248,0.3) !important; }
.footer {
    text-align: center; text-transform: uppercase; letter-spacing: 2px;
    opacity: 0.5; font-size: 0.75rem; margin-top: 5px; color: #38bdf8 !important;
}
.footer-brand {
    text-align: center; text-transform: uppercase; letter-spacing: 3px;
    font-size: 0.7rem; color: #38bdf8 !important; opacity: 0.6; margin-top: 3px;
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
    - 🌤️ **WTTR.IN** — LIVE WEATHER DATA
    - 🎨 **STREAMLIT** — BEAUTIFUL UI
    """)
    st.markdown("---")
    st.markdown("### 📌 HOW TO USE")
    st.markdown("""
    1. CLICK A **POPULAR DESTINATION**
    2. SET YOUR **TRIP DURATION**
    3. CHOOSE **CURRENCY & BUDGET**
    4. PICK YOUR **LANGUAGE**
    5. ENTER **TRAVEL DATES**
    6. PICK YOUR **INTERESTS**
    7. CLICK **GENERATE** AND WAIT!
    8. **BOOK TICKETS** OR **SHARE**!
    """)
    st.markdown("---")
    st.markdown("### ✈️ FEATURES")
    st.markdown("""
    - 🗺️ DAY-BY-DAY ITINERARY
    - 🌤️ LIVE WEATHER INFO
    - 🌐 MULTI-LANGUAGE SUPPORT
    - 🏨 HOTEL RECOMMENDATIONS
    - 🍽️ RESTAURANT PICKS
    - 💰 MULTI-CURRENCY BUDGET
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
st.markdown('<div class="subtitle">YOUR PERSONAL AI TRAVEL AGENT — POWERED BY GROQ + TAVILY</div>',
            unsafe_allow_html=True)
st.markdown('<div class="brand-tag">— BY MANISH TRAVEL PLANNER —</div>',
            unsafe_allow_html=True)
st.markdown("---")

# ══════════════════════════════════════
# POPULAR DESTINATIONS — 4 COLUMNS
# ══════════════════════════════════════
st.markdown('<div class="section-title">🔥 POPULAR DESTINATIONS — CLICK TO AUTO-FILL</div>',
            unsafe_allow_html=True)

if "selected_destination" not in st.session_state:
    st.session_state.selected_destination = ""
if "itinerary_ready" not in st.session_state:
    st.session_state.itinerary_ready = False

popular_destinations = [
    ("🗼", "PARIS"),      ("🗽", "NEW YORK"),
    ("🏯", "TOKYO"),      ("🕌", "DUBAI"),
    ("🏛️", "ROME"),       ("🌴", "BALI"),
    ("🐘", "KERALA"),     ("⛩️", "RAJASTHAN"),
    ("🏔️", "MANALI"),     ("🌊", "GOA"),
    ("🏰", "LONDON"),     ("🗺️", "SINGAPORE"),
]

# ✅ 4 COLUMNS — buttons fit perfectly
dest_cols = st.columns(4)
for i, (emoji, city) in enumerate(popular_destinations):
    with dest_cols[i % 4]:
        if st.button(
            f"{emoji} {city}",
            key=f"dest_{i}",
            use_container_width=True
        ):
            st.session_state.selected_destination = city.title()
            st.rerun()

st.markdown("---")

# ══════════════════════════════════════
# INPUT FORM
# ══════════════════════════════════════
st.markdown('<div class="section-title">📝 TELL US ABOUT YOUR DREAM TRIP</div>',
            unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    destination = st.text_input(
        "🗺️ DESTINATION",
        value=st.session_state.selected_destination,
        placeholder="TYPE A CITY OR CLICK ABOVE!"
    )
    if destination != st.session_state.selected_destination:
        st.session_state.selected_destination = destination

   # ══════════════════════════════════════
    # WEATHER WIDGET — OPEN-METEO (Free, No blocks!)
    # ══════════════════════════════════════
    if destination and len(destination.strip()) > 2:
        weather_box = st.empty()
        try:
            # Step 1: Get coordinates of city using geocoding API
            geo_url = (
                f"https://geocoding-api.open-meteo.com/v1/search"
                f"?name={urllib.parse.quote(destination)}&count=1&language=en&format=json"
            )
            geo_resp = requests.get(geo_url, timeout=8)
            geo_data = geo_resp.json()

            if geo_data.get("results"):
                lat  = geo_data["results"][0]["latitude"]
                lon  = geo_data["results"][0]["longitude"]
                city = geo_data["results"][0].get("name", destination)
                country = geo_data["results"][0].get("country", "")

                # Step 2: Get weather from Open-Meteo (100% free, no API key!)
                weather_url = (
                    f"https://api.open-meteo.com/v1/forecast"
                    f"?latitude={lat}&longitude={lon}"
                    f"&current_weather=true"
                    f"&hourly=relativehumidity_2m,precipitation_probability"
                    f"&timezone=auto&forecast_days=1"
                )
                w_resp = requests.get(weather_url, timeout=8)
                w_data = w_resp.json()

                if "current_weather" in w_data:
                    cw       = w_data["current_weather"]
                    temp     = cw.get("temperature", "—")
                    wind     = cw.get("windspeed", "—")
                    wcode    = cw.get("weathercode", 0)
                    humidity = w_data.get("hourly", {}).get(
                        "relativehumidity_2m", [None]
                    )[0]
                    precip   = w_data.get("hourly", {}).get(
                        "precipitation_probability", [None]
                    )[0]

                    # Weather code to description
                    weather_codes = {
                        0:"☀️ Clear Sky", 1:"🌤️ Mainly Clear",
                        2:"⛅ Partly Cloudy", 3:"☁️ Overcast",
                        45:"🌫️ Foggy", 48:"🌫️ Icy Fog",
                        51:"🌦️ Light Drizzle", 61:"🌧️ Light Rain",
                        63:"🌧️ Moderate Rain", 65:"🌧️ Heavy Rain",
                        71:"🌨️ Light Snow", 73:"❄️ Moderate Snow",
                        75:"❄️ Heavy Snow", 80:"🌦️ Rain Showers",
                        95:"⛈️ Thunderstorm", 96:"⛈️ Heavy Thunderstorm",
                    }
                    condition = weather_codes.get(wcode, "🌡️ Unknown")

                    weather_box.markdown(
                        f'<div class="weather-box">'
                        f'<strong>🌤️ LIVE WEATHER — {city.upper()}, {country.upper()}</strong><br>'
                        f'🌡️ TEMPERATURE: <strong>{temp}°C</strong> &nbsp;|&nbsp; {condition}<br>'
                        f'💨 WIND SPEED: {wind} km/h &nbsp;|&nbsp; '
                        f'💧 HUMIDITY: {humidity}% &nbsp;|&nbsp; '
                        f'🌧️ RAIN CHANCE: {precip}%'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                else:
                    weather_box.markdown(
                        f'<div class="weather-box">'
                        f'🌤️ WEATHER DATA UNAVAILABLE FOR {destination.upper()}'
                        f'</div>',
                        unsafe_allow_html=True
                    )
            else:
                weather_box.markdown(
                    f'<div class="weather-box">'
                    f'🌤️ CITY NOT FOUND — TRY FULL CITY NAME (e.g. "New York" not "NY")'
                    f'</div>',
                    unsafe_allow_html=True
                )
        except Exception:
            weather_box.markdown(
                '<div class="weather-box">'
                '🌤️ WEATHER TEMPORARILY UNAVAILABLE'
                '</div>',
                unsafe_allow_html=True
            )
            if r1.status_code == 200 and len(r1.text.strip()) > 3:
                weather_box.markdown(
                    f'<div class="weather-box">'
                    f'<strong>🌤️ LIVE WEATHER — {destination.upper()}</strong><br>'
                    f'📍 {r1.text.strip()}<br>'
                    f'🌡️ CONDITIONS: {r2.text.strip() if r2.status_code==200 else "—"}<br>'
                    f'💧 {r3.text.strip() if r3.status_code==200 else "—"}'
                    f'</div>',
                    unsafe_allow_html=True
                )
            else:
                weather_box.markdown(
                    f'<div class="weather-box">'
                    f'🌤️ WEATHER FOR {destination.upper()} — '
                    f'ENTER FULL CITY NAME FOR ACCURATE WEATHER'
                    f'</div>',
                    unsafe_allow_html=True
                )
        except Exception:
            weather_box.markdown(
                '<div class="weather-box">'
                '🌤️ WEATHER SERVICE TEMPORARILY UNAVAILABLE'
                '</div>',
                unsafe_allow_html=True
            )

    duration = st.slider("📅 TRIP DURATION (DAYS)", 1, 14, 3)
    st.markdown(
        f"<p style='color:#38bdf8;font-weight:700;font-size:0.85rem;'>"
        f"✅ SELECTED: {duration} DAY(S)</p>",
        unsafe_allow_html=True
    )

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

    if budget_amount:
        try:
            amt = float(budget_amount.replace(",", ""))
            tiers = {
                "INR": [(30000,"🟢 BUDGET"),(80000,"🟡 MODERATE"),(150000,"🟠 COMFORTABLE")],
                "USD": [(800,  "🟢 BUDGET"),(2500, "🟡 MODERATE"),(5000,  "🟠 COMFORTABLE")],
                "EUR": [(700,  "🟢 BUDGET"),(2000, "🟡 MODERATE"),(4000,  "🟠 COMFORTABLE")],
                "GBP": [(600,  "🟢 BUDGET"),(1800, "🟡 MODERATE"),(3500,  "🟠 COMFORTABLE")],
            }
            tier = "🔴 LUXURY TRIP"
            for limit, label in tiers[curr_key]:
                if amt < limit:
                    tier = f"{label} TRIP"
                    break
            st.markdown(
                f"<p style='color:#38bdf8;font-weight:700;font-size:0.85rem;'>{tier}</p>",
                unsafe_allow_html=True
            )
        except Exception:
            pass

    budget = f"{currency} {budget_amount}" if budget_amount else f"{currency} (not specified)"

with col2:
    # ── DATE PICKER ──
    st.markdown("🗓️ **TRAVEL DATES**")
    import datetime
    date_col1, date_col2 = st.columns(2)
    with date_col1:
        start_date = st.date_input(
            "FROM DATE",
            value=datetime.date.today() + datetime.timedelta(days=7),
            min_value=datetime.date.today(),
            format="DD/MM/YYYY"
        )
    with date_col2:
        end_date = st.date_input(
            "TO DATE",
            value=datetime.date.today() + datetime.timedelta(days=7 + duration),
            min_value=start_date,
            format="DD/MM/YYYY"
        )

    # Calculate trip days
    trip_days    = (end_date - start_date).days
    travel_dates = f"{start_date.strftime('%d %b %Y')} to {end_date.strftime('%d %b %Y')}"

    if trip_days > 0:
        st.markdown(
            f"<p style='color:#38bdf8;font-weight:700;font-size:0.85rem;'>"
            f"✅ TRIP LENGTH: {trip_days} DAY(S) — "
            f"{start_date.strftime('%d %b')} TO {end_date.strftime('%d %b %Y')}"
            f"</p>",
            unsafe_allow_html=True
        )
    elif trip_days == 0:
        st.warning("⚠️ END DATE MUST BE AFTER START DATE!")
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
    placeholder="e.g. Vegetarian food, travelling with friends...",
    height=80
)
st.markdown("---")


# ══════════════════════════════════════
# PDF GENERATOR
# ══════════════════════════════════════
def create_pdf(content, destination, duration, budget, travel_dates, travelers):
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
    pdf.cell(0, 8, "ai-travel-planner-h7f7ryewjbufa5tdvfewnu.streamlit.app",
             ln=True, align="C")
    pdf.set_fill_color(224, 242, 254)
    pdf.rect(10, 40, 190, 30, 'F')
    pdf.set_text_color(2, 132, 199)
    pdf.set_font("Arial", "B", 11)
    pdf.set_xy(12, 42)
    pdf.cell(0, 6,
             f"DESTINATION: {destination.upper()}  |  DURATION: {duration} DAYS  |  TRAVELERS: {travelers}",
             ln=True)
    pdf.set_xy(12, 50)
    pdf.cell(0, 6, f"DATES: {travel_dates}  |  BUDGET: {budget}", ln=True)
    pdf.set_xy(10, 75)
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
def send_email(to_email, destination, itinerary, duration, travel_dates, budget):
    try:
        msg            = MIMEMultipart("alternative")
        msg["Subject"] = f"✈️ YOUR {duration}-DAY {destination.upper()} TRAVEL ITINERARY"
        msg["From"]    = EMAIL_SENDER
        msg["To"]      = to_email
        html_body = f"""
        <html><body style="font-family:Arial;background:#0c1445;
                           color:#e0f2fe;padding:20px;">
        <div style="max-width:700px;margin:auto;background:#1a237e;
                    border-radius:16px;overflow:hidden;">
            <div style="background:#0284c7;padding:25px;text-align:center;">
                <h1 style="color:white;text-transform:uppercase;
                           letter-spacing:3px;margin:0;">
                    🌍 AI TRAVEL ITINERARY PLANNER
                </h1>
                <p style="color:#bae6fd;text-transform:uppercase;
                          letter-spacing:2px;margin:5px 0;">
                    BY MANISH TRAVEL PLANNER
                </p>
            </div>
            <div style="padding:20px;background:#e0f2fe;color:#0c1445;">
                <table style="width:100%;background:#bae6fd;border-radius:10px;
                              padding:15px;margin-bottom:20px;">
                    <tr>
                        <td><strong>📍 DESTINATION:</strong> {destination.upper()}</td>
                        <td><strong>📅 DURATION:</strong> {duration} DAYS</td>
                    </tr>
                    <tr>
                        <td><strong>🗓️ DATES:</strong> {travel_dates}</td>
                        <td><strong>💰 BUDGET:</strong> {budget}</td>
                    </tr>
                </table>
                <div style="white-space:pre-wrap;font-size:14px;
                            line-height:1.8;color:#1a237e;">
                    {itinerary}
                </div>
            </div>
            <div style="background:#0284c7;padding:15px;text-align:center;">
                <p style="color:white;font-size:12px;margin:0;
                          text-transform:uppercase;letter-spacing:1px;">
                    © MANISH TRAVEL PLANNER — ALL RIGHTS RESERVED<br>
                    <a href="https://ai-travel-planner-h7f7ryewjbufa5tdvfewnu.streamlit.app"
                       style="color:#bae6fd;">
                        PLAN MORE TRIPS FOR FREE
                    </a>
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
def generate_itinerary(destination, duration, budget, travel_dates,
                        travelers, interests, special_requirements, lang_name):
    tavily = TavilyClient(api_key=TAVILY_API_KEY)
    try:
        res = tavily.search(
            query=f"best things to do hotels restaurants {destination} travel guide",
            max_results=3,
            search_depth="basic"
        )
        web_info = "\n".join([
            f"- {r.get('title','')}: {r.get('content','')[:300]}"
            for r in res.get("results", [])
        ])
    except Exception:
        web_info = "Amazing destination with great attractions."

    groq_client    = Groq(api_key=GROQ_API_KEY)
    interests_text = ", ".join(interests) if interests else "General Sightseeing"
    special_text   = special_requirements or "None"
    curr_symbol    = budget.split()[0]

    prompt = f"""You are an expert AI Travel Planner with 20 years experience.
IMPORTANT: Write the ENTIRE response in {lang_name} language only.

Real-time web info about {destination}: {web_info}

Create a detailed {duration}-day itinerary:
- Destination: {destination}
- Dates: {travel_dates}
- Budget: {budget}
- Travelers: {travelers}
- Interests: {interests_text}
- Notes: {special_text}

Show ALL prices in {curr_symbol} AND USD equivalent.

## 🌍 DESTINATION OVERVIEW
[4 sentences about destination]

## 📅 DAY-BY-DAY ITINERARY
### DAY 1 — [THEME]
- **MORNING:** [activity + detail]
- **AFTERNOON:** [activity + detail]
- **EVENING:** [dinner + detail]
[All {duration} days with unique themes]

## 🏨 HOTEL RECOMMENDATIONS
1. **[HOTEL]** — [{curr_symbol}/USD price] — [why great]
2. **[HOTEL]** — [{curr_symbol}/USD price] — [why great]
3. **[HOTEL]** — [{curr_symbol}/USD price] — [why great]

## 🍽️ MUST-TRY RESTAURANTS
1. **[NAME]** — [cuisine] — [dish] — [{curr_symbol} cost]
2. **[NAME]** — [cuisine] — [dish] — [{curr_symbol} cost]
3. **[NAME]** — [cuisine] — [dish] — [{curr_symbol} cost]
4. **[NAME]** — [cuisine] — [dish] — [{curr_symbol} cost]
5. **[NAME]** — [cuisine] — [dish] — [{curr_symbol} cost]

## 💰 BUDGET BREAKDOWN
- **ACCOMMODATION:** [{curr_symbol}] per night
- **FOOD:** [{curr_symbol}] per day
- **ACTIVITIES:** [{curr_symbol}] total
- **TRANSPORT:** [{curr_symbol}] total
- **TOTAL: [{curr_symbol}] for {travelers} TRAVELER(S)**

## 💡 TOP TRAVEL TIPS
1. [local tip]  2. [attraction tip]
3. [cultural tip]  4. [safety tip]  5. [money saving tip]

## 🚗 GETTING AROUND
[Transport options with costs in {curr_symbol}]
"""

    resp = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system",
             "content": f"Expert travel planner. Write entirely in {lang_name}. "
                        "Detailed itineraries with accurate local prices."},
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
    "🚀 GENERATE MY TRAVEL ITINERARY!",
    use_container_width=True
)

if generate_btn:
    if not destination:
        st.error("⚠️ PLEASE ENTER A DESTINATION OR CLICK A POPULAR ONE!")
    elif not travel_dates:
        st.error("⚠️ PLEASE ENTER YOUR TRAVEL DATES!")
    elif not budget_amount:
        st.error("⚠️ PLEASE ENTER YOUR BUDGET AMOUNT!")
    else:
        with st.spinner("🔍 AI IS SEARCHING & CRAFTING YOUR PERFECT TRIP... ⏳"):
            try:
                result = generate_itinerary(
                    destination, duration, budget,
                    travel_dates, travelers,
                    interests, special_requirements, lang_name
                )
                st.session_state.itinerary_result = result
                st.session_state.itinerary_dest   = destination
                st.session_state.itinerary_ready  = True
            except Exception as e:
                st.error(f"❌ ERROR: {str(e)}")
                st.info("💡 PLEASE TRY AGAIN IN A FEW SECONDS!")


# ══════════════════════════════════════
# SHOW RESULTS
# ══════════════════════════════════════
if st.session_state.get("itinerary_ready"):
    result      = st.session_state.itinerary_result
    destination = st.session_state.itinerary_dest

    st.markdown("---")
    st.markdown(
        '<div class="success-header">✅ YOUR PERSONALIZED ITINERARY IS READY!</div>',
        unsafe_allow_html=True
    )
    st.markdown('<div class="result-container">', unsafe_allow_html=True)
    st.markdown(result)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("---")

    # ══════════════════════════════════════
    # BOOKING LINKS
    # ══════════════════════════════════════
    st.markdown('<div class="section-title">✈️ BOOK YOUR TRIP</div>',
                unsafe_allow_html=True)
    st.caption("CLICK ANY BUTTON TO OPEN BOOKING WEBSITE!")

    dest_encoded = urllib.parse.quote(destination)
    bk1, bk2, bk3, bk4, bk5 = st.columns(5)

    booking_links = [
        (bk1, "✈️", "SKYSCANNER", "FLIGHTS",
         f"https://www.skyscanner.co.in/transport/flights/{dest_encoded}/"),
        (bk2, "🛫", "MAKEMYTRIP", "FLIGHTS + HOTELS",
         "https://www.makemytrip.com/flights/"),
        (bk3, "🚂", "IRCTC", "TRAIN TICKETS",
         "https://www.irctc.co.in/nget/train-search"),
        (bk4, "🚌", "REDBUS", "BUS TICKETS",
         f"https://www.redbus.in/bus-tickets/{dest_encoded}"),
        (bk5, "🏨", "BOOKING.COM", "HOTELS",
         f"https://www.booking.com/searchresults.html?ss={dest_encoded}"),
    ]

    for col, emoji, name, sub, url in booking_links:
        with col:
            col.markdown(
                f'<a href="{url}" target="_blank" style="text-decoration:none;">'
                f'<div class="booking-card">'
                f'<div style="font-size:1.8rem;">{emoji}</div>'
                f'<div style="color:#38bdf8;font-weight:800;font-size:0.8rem;'
                f'text-transform:uppercase;margin-top:5px;">{name}</div>'
                f'<div style="color:#bae6fd;font-size:0.7rem;">{sub}</div>'
                f'</div></a>',
                unsafe_allow_html=True
            )

    # ══════════════════════════════════════
    # GOOGLE MAPS
    # ══════════════════════════════════════
    st.markdown("---")
    st.markdown('<div class="section-title">🗺️ EXPLORE ON GOOGLE MAPS</div>',
                unsafe_allow_html=True)

    m1, m2, m3 = st.columns(3)
    maps_links = [
        (m1, "🏛️", "TOURIST ATTRACTIONS",
         f"https://www.google.com/maps/search/{dest_encoded}+tourist+attractions"),
        (m2, "🏨", "HOTELS NEARBY",
         f"https://www.google.com/maps/search/hotels+in+{dest_encoded}"),
        (m3, "🍽️", "RESTAURANTS",
         f"https://www.google.com/maps/search/restaurants+in+{dest_encoded}"),
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
    st.markdown('<div class="section-title">📤 SAVE OR SHARE YOUR ITINERARY</div>',
                unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)

    # PDF DOWNLOAD
    with c1:
        try:
            pdf_bytes = create_pdf(
                result, destination, duration,
                budget, travel_dates, travelers
            )
            st.download_button(
                label="📄 DOWNLOAD AS PDF",
                data=pdf_bytes,
                file_name=f"MANISH_{destination.replace(' ','_').upper()}_ITINERARY.pdf",
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

    # WHATSAPP
    with c2:
        share_msg = (
            f"✈️ *{duration}-DAY {destination.upper()} TRIP*\n"
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
            f'text-align:center;cursor:pointer;margin-top:0px;'
            f'box-shadow:0 4px 15px rgba(34,197,94,0.4);">'
            f'📱 SHARE ON WHATSAPP'
            f'</div></a>',
            unsafe_allow_html=True
        )

    # EMAIL
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
                    st.warning(
                        "⚠️ EMAIL NOT CONFIGURED!\n\n"
                        "ADD TO STREAMLIT SECRETS:\n"
                        "EMAIL_SENDER = 'your@gmail.com'\n"
                        "EMAIL_PASSWORD = 'your_app_password'"
                    )
                else:
                    with st.spinner("📧 SENDING EMAIL..."):
                        result_send = send_email(
                            user_email, destination,
                            result, duration, travel_dates, budget
                        )
                        if result_send is True:
                            st.success(f"✅ ITINERARY SENT TO {user_email}!")
                        else:
                            st.error(f"❌ EMAIL FAILED: {result_send}")

# ══════════════════════════════════════
# FOOTER
# ══════════════════════════════════════
st.markdown("---")
st.markdown(
    '<div class="footer">BUILT WITH ❤️ USING GROQ AI + TAVILY + STREAMLIT</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="footer-brand">'
    '© 2025 MANISH TRAVEL ITINERARY PLANNER — ALL RIGHTS RESERVED'
    '</div>',
    unsafe_allow_html=True
)
