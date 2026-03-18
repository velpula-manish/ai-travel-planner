import streamlit as st
import os
import requests
import urllib.parse
from groq import Groq
from tavily import TavilyClient

GROQ_API_KEY   = st.secrets["GROQ_API_KEY"]
TAVILY_API_KEY = st.secrets["TAVILY_API_KEY"]

st.set_page_config(
    page_title="AI Travel Planner ✈️",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
/* ══════════════════════════════════
   BACKGROUND
══════════════════════════════════ */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(160deg, #052e16, #14532d, #166534) !important;
    min-height: 100vh;
}

/* ══════════════════════════════════
   SIDEBAR — ALWAYS VISIBLE
══════════════════════════════════ */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #052e16 0%, #14532d 100%) !important;
    border-right: 2px solid #16a34a !important;
}
[data-testid="stSidebar"] * {
    color: #bbf7d0 !important;
}
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] strong {
    color: #4ade80 !important;
}
[data-testid="stSidebar"] .stInfo {
    background: rgba(22,163,74,0.2) !important;
    border: 1px solid #16a34a !important;
    color: #bbf7d0 !important;
}

/* ══════════════════════════════════
   WATERMARK
══════════════════════════════════ */
[data-testid="stAppViewContainer"]::before {
    content: "MANISH TRAVEL PLANNER";
    position: fixed;
    top: 45%;
    left: 55%;
    transform: translate(-50%, -50%) rotate(-30deg);
    font-size: 4.5rem;
    font-weight: 900;
    color: rgba(74, 222, 128, 0.07);
    white-space: nowrap;
    pointer-events: none;
    z-index: 0;
    letter-spacing: 5px;
    text-transform: uppercase;
}
[data-testid="stAppViewContainer"]::after {
    content: "✈ MANISH ✈ TRAVEL ✈ PLANNER ✈ MANISH ✈ TRAVEL ✈ PLANNER";
    position: fixed;
    bottom: 10%;
    left: 55%;
    transform: translate(-50%, 0) rotate(-30deg);
    font-size: 1.8rem;
    font-weight: 700;
    color: rgba(74, 222, 128, 0.05);
    white-space: nowrap;
    pointer-events: none;
    z-index: 0;
    letter-spacing: 3px;
}

/* ══════════════════════════════════
   ALL TEXT COLOR
══════════════════════════════════ */
[data-testid="stAppViewContainer"] p,
[data-testid="stAppViewContainer"] li,
[data-testid="stAppViewContainer"] label,
[data-testid="stAppViewContainer"] span,
[data-testid="stAppViewContainer"] div {
    color: #dcfce7 !important;
}

/* ══════════════════════════════════
   TITLE
══════════════════════════════════ */
.main-title {
    text-align: center;
    font-size: 2.6rem;
    font-weight: 900;
    letter-spacing: 4px;
    text-transform: uppercase;
    padding: 15px 0 5px 0;
    background: linear-gradient(135deg, #4ade80, #86efac, #34d399);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.subtitle {
    text-align: center;
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 3px;
    color: #86efac !important;
    opacity: 0.8;
    margin-bottom: 3px;
}
.brand-tag {
    text-align: center;
    font-size: 0.8rem;
    letter-spacing: 3px;
    color: #4ade80 !important;
    font-weight: 700;
    text-transform: uppercase;
    margin-bottom: 10px;
}

/* ══════════════════════════════════
   SECTION TITLES
══════════════════════════════════ */
.section-title {
    font-size: 1.05rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: #4ade80 !important;
    margin-bottom: 10px;
    border-left: 4px solid #16a34a;
    padding-left: 10px;
}

/* ══════════════════════════════════
   WEATHER BOX
══════════════════════════════════ */
.weather-box {
    background: linear-gradient(135deg,
        rgba(5,46,22,0.9), rgba(20,83,45,0.9));
    border: 1.5px solid #16a34a;
    border-radius: 12px;
    padding: 12px 16px;
    margin: 8px 0 12px 0;
    font-size: 0.92rem;
    font-weight: 600;
    color: #bbf7d0 !important;
    line-height: 1.9;
    box-shadow: 0 4px 15px rgba(22,163,74,0.2);
}

/* ══════════════════════════════════
   POPULAR DESTINATION BUTTONS
   — ALL EQUAL SIZE, FIXED HEIGHT —
══════════════════════════════════ */
div[data-testid="column"] .stButton > button {
    background: linear-gradient(135deg, #14532d, #166534) !important;
    color: #86efac !important;
    font-size: 0.82rem !important;
    font-weight: 800 !important;
    height: 60px !important;
    min-height: 60px !important;
    max-height: 60px !important;
    padding: 0 8px !important;
    border-radius: 10px !important;
    border: 1.5px solid #16a34a !important;
    text-transform: uppercase !important;
    letter-spacing: 0.8px !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    transition: all 0.2s !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    width: 100% !important;
}
div[data-testid="column"] .stButton > button:hover {
    background: linear-gradient(135deg, #15803d, #16a34a) !important;
    color: white !important;
    border-color: #4ade80 !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(22,163,74,0.4) !important;
}

/* ══════════════════════════════════
   GENERATE BUTTON
══════════════════════════════════ */
.stButton > button {
    width: 100%;
    background: linear-gradient(135deg, #15803d, #16a34a, #22c55e) !important;
    color: white !important;
    font-size: 1.2rem !important;
    font-weight: 900 !important;
    padding: 18px 30px !important;
    border-radius: 14px !important;
    border: none !important;
    text-transform: uppercase !important;
    letter-spacing: 2px !important;
    box-shadow: 0 8px 32px rgba(22,163,74,0.5) !important;
    transition: all 0.3s !important;
}
.stButton > button:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 14px 40px rgba(22,163,74,0.7) !important;
}

/* ══════════════════════════════════
   SUCCESS HEADER
══════════════════════════════════ */
.success-header {
    background: linear-gradient(135deg, #059669, #10b981, #34d399);
    color: white !important;
    padding: 18px 25px;
    border-radius: 14px;
    font-size: 1.3rem;
    font-weight: 900;
    margin-bottom: 20px;
    text-align: center;
    text-transform: uppercase;
    letter-spacing: 3px;
    box-shadow: 0 8px 32px rgba(16,185,129,0.4);
}

/* ══════════════════════════════════
   RESULT BOX
══════════════════════════════════ */
.result-container {
    border: 1.5px solid #16a34a;
    border-radius: 16px;
    padding: 25px 30px;
    margin-bottom: 20px;
    background: rgba(5, 46, 22, 0.5);
}

/* ══════════════════════════════════
   DOWNLOAD BUTTON
══════════════════════════════════ */
.stDownloadButton > button {
    background: linear-gradient(135deg, #1e40af, #2563eb) !important;
    color: white !important;
    font-weight: 800 !important;
    font-size: 0.95rem !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
    border-radius: 10px !important;
    border: none !important;
    padding: 12px !important;
    box-shadow: 0 4px 15px rgba(37,99,235,0.4) !important;
    width: 100% !important;
}

/* ══════════════════════════════════
   INPUT FIELDS
══════════════════════════════════ */
.stTextInput input,
.stTextArea textarea,
.stNumberInput input {
    background: rgba(5, 46, 22, 0.7) !important;
    border: 1.5px solid #16a34a !important;
    border-radius: 8px !important;
    color: #dcfce7 !important;
}
.stTextInput input:focus,
.stTextArea textarea:focus {
    border-color: #4ade80 !important;
    box-shadow: 0 0 0 2px rgba(74,222,128,0.2) !important;
}
.stSelectbox > div > div {
    background: rgba(5, 46, 22, 0.7) !important;
    border: 1.5px solid #16a34a !important;
    color: #dcfce7 !important;
}

/* ══════════════════════════════════
   SLIDER
══════════════════════════════════ */
.stSlider [data-baseweb="slider"] div {
    background: #16a34a !important;
}

/* ══════════════════════════════════
   DIVIDER
══════════════════════════════════ */
hr {
    border-color: rgba(22,163,74,0.3) !important;
}

/* ══════════════════════════════════
   FOOTER
══════════════════════════════════ */
.footer {
    text-align: center;
    text-transform: uppercase;
    letter-spacing: 2px;
    opacity: 0.5;
    font-size: 0.75rem;
    margin-top: 5px;
    color: #4ade80 !important;
}
.footer-brand {
    text-align: center;
    text-transform: uppercase;
    letter-spacing: 3px;
    font-size: 0.7rem;
    color: #4ade80 !important;
    opacity: 0.6;
    margin-top: 3px;
}
</style>
""", unsafe_allow_html=True)


# ── SIDEBAR ──
with st.sidebar:
    st.markdown(
        "<h2 style='color:#4ade80 !important;text-transform:uppercase;"
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
    4. ENTER **TRAVEL DATES**
    5. PICK YOUR **INTERESTS**
    6. CLICK **GENERATE** AND WAIT!
    7. **SHARE** ON WHATSAPP!
    """)
    st.markdown("---")
    st.markdown("### ✈️ FEATURES")
    st.markdown("""
    - 🗺️ DAY-BY-DAY ITINERARY
    - 🌤️ LIVE WEATHER INFO
    - 🏨 HOTEL RECOMMENDATIONS
    - 🍽️ RESTAURANT PICKS
    - 💰 MULTI-CURRENCY BUDGET
    - 💡 LOCAL TRAVEL TIPS
    - 📱 WHATSAPP SHARING
    - 📥 DOWNLOAD ITINERARY
    """)
    st.markdown("---")
    st.markdown(
        "<div style='text-align:center;color:#4ade80 !important;"
        "font-size:0.75rem;text-transform:uppercase;letter-spacing:2px;'>"
        "© MANISH TRAVEL PLANNER<br>ALL RIGHTS RESERVED</div>",
        unsafe_allow_html=True
    )

# ── HEADER ──
st.markdown('<div class="main-title">🌍 AI TRAVEL ITINERARY PLANNER</div>',
            unsafe_allow_html=True)
st.markdown('<div class="subtitle">YOUR PERSONAL AI TRAVEL AGENT — POWERED BY GROQ + TAVILY</div>',
            unsafe_allow_html=True)
st.markdown('<div class="brand-tag">— BY MANISH TRAVEL PLANNER —</div>',
            unsafe_allow_html=True)
st.markdown("---")

# ══════════════════════════════════════
# POPULAR DESTINATIONS — EQUAL SIZE
# ══════════════════════════════════════
st.markdown('<div class="section-title">🔥 POPULAR DESTINATIONS — CLICK TO AUTO-FILL</div>',
            unsafe_allow_html=True)

if "selected_destination" not in st.session_state:
    st.session_state.selected_destination = ""

# Fixed list — 12 destinations in 6 columns x 2 rows
popular_destinations = [
    ("🗼", "PARIS"),      ("🗽", "NEW YORK"),
    ("🏯", "TOKYO"),      ("🕌", "DUBAI"),
    ("🏛️", "ROME"),       ("🌴", "BALI"),
    ("🐘", "KERALA"),     ("⛩️", "RAJASTHAN"),
    ("🏔️", "MANALI"),     ("🌊", "GOA"),
    ("🏰", "LONDON"),     ("🗺️", "SINGAPORE"),
]

# 6 columns — each button same width and height
dest_cols = st.columns(6)
for i, (emoji, city) in enumerate(popular_destinations):
    with dest_cols[i % 6]:
        if st.button(
            f"{emoji}\n{city}",
            key=f"dest_{i}",
            use_container_width=True
        ):
            st.session_state.selected_destination = city.title()
            st.rerun()

st.markdown("---")

# ── INPUT FORM ──
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
    # WEATHER — Always shows when destination typed
    # ══════════════════════════════════════
    if destination and len(destination.strip()) > 2:
        with st.spinner("🌤️ FETCHING LIVE WEATHER..."):
            try:
                r1 = requests.get(
                    f"https://wttr.in/{destination}?format=3",
                    timeout=6
                )
                r2 = requests.get(
                    f"https://wttr.in/{destination}?format=%C+%t",
                    timeout=6
                )
                r3 = requests.get(
                    f"https://wttr.in/{destination}?format=💧+Humidity:+%h",
                    timeout=6
                )
                if r1.status_code == 200 and "Unknown" not in r1.text:
                    st.markdown(
                        f'<div class="weather-box">'
                        f'🌤️ <strong>LIVE WEATHER — {destination.upper()}</strong><br>'
                        f'📍 {r1.text.strip()}<br>'
                        f'🌡️ CONDITIONS: {r2.text.strip() if r2.status_code==200 else "—"}<br>'
                        f'{r3.text.strip() if r3.status_code==200 else ""}'
                        f'</div>',
                        unsafe_allow_html=True
                    )
            except Exception:
                st.markdown(
                    '<div class="weather-box">'
                    '🌤️ WEATHER DATA TEMPORARILY UNAVAILABLE'
                    '</div>',
                    unsafe_allow_html=True
                )

    duration = st.slider("📅 TRIP DURATION (DAYS)", 1, 14, 3)

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
            "INR": ("e.g. 50000",  "₹20,000 – ₹2,00,000"),
            "USD": ("e.g. 1500",   "$500 – $10,000"),
            "EUR": ("e.g. 1200",   "€500 – €8,000"),
            "GBP": ("e.g. 1000",   "£400 – £7,000"),
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
            st.caption(f"**{tier}**")
        except Exception:
            pass

    budget = f"{currency} {budget_amount}" if budget_amount else f"{currency} (not specified)"

with col2:
    travel_dates = st.text_input("🗓️ TRAVEL DATES", placeholder="e.g. June 10–17, 2025")
    travelers    = st.number_input("👥 NUMBER OF TRAVELERS", 1, 20, 2)
    interests    = st.multiselect("❤️ YOUR INTERESTS", [
        "🏛️ HISTORY & CULTURE",  "🍽️ FOOD & DINING",
        "🎨 ART & MUSEUMS",       "🌿 NATURE & OUTDOORS",
        "🛍️ SHOPPING",            "🎭 NIGHTLIFE",
        "🏖️ BEACH & RELAXATION",  "🏔️ ADVENTURE & SPORTS",
        "📸 PHOTOGRAPHY",         "👨‍👩‍👧 FAMILY FRIENDLY"
    ], default=["🍽️ FOOD & DINING", "🎨 ART & MUSEUMS"])

special_requirements = st.text_area(
    "💬 SPECIAL REQUIREMENTS (OPTIONAL)",
    placeholder="e.g. Vegetarian food, travelling with friends...",
    height=80
)
st.markdown("---")


# ── GENERATOR ──
def generate_itinerary(destination, duration, budget, travel_dates,
                        travelers, interests, special_requirements):
    tavily = TavilyClient(api_key=TAVILY_API_KEY)
    try:
        res = tavily.search(
            query=f"best things to do hotels restaurants {destination} travel guide",
            max_results=3, search_depth="basic"
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

Real-time info about {destination}: {web_info}

Create detailed {duration}-day itinerary:
- Destination: {destination}
- Dates: {travel_dates}
- Budget: {budget}
- Travelers: {travelers}
- Interests: {interests_text}
- Notes: {special_text}

Show ALL prices in {curr_symbol} AND USD.

## 🌍 DESTINATION OVERVIEW
## 📅 DAY-BY-DAY ITINERARY
### DAY 1 — [THEME]
- **MORNING:** ...
- **AFTERNOON:** ...
- **EVENING:** ...
[All {duration} days]
## 🏨 HOTEL RECOMMENDATIONS (3 options with prices)
## 🍽️ MUST-TRY RESTAURANTS (5 with prices in {curr_symbol})
## 💰 BUDGET BREAKDOWN (with TOTAL for {travelers} travelers)
## 💡 TOP TRAVEL TIPS (5 tips)
## 🚗 GETTING AROUND (transport costs in {curr_symbol})
"""

    resp = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "Expert travel planner. Detailed itineraries with accurate local prices."},
            {"role": "user",   "content": prompt}
        ],
        max_tokens=3000,
        temperature=0.7
    )
    return resp.choices[0].message.content


# ── GENERATE BUTTON ──
generate_btn = st.button(
    "🚀 GENERATE MY TRAVEL ITINERARY!",
    use_container_width=True
)

if generate_btn:
    if not destination:
        st.error("⚠️ PLEASE ENTER A DESTINATION OR CLICK A POPULAR ONE ABOVE!")
    elif not travel_dates:
        st.error("⚠️ PLEASE ENTER YOUR TRAVEL DATES!")
    elif not budget_amount:
        st.error("⚠️ PLEASE ENTER YOUR BUDGET AMOUNT!")
    else:
        with st.spinner("🔍 AI IS SEARCHING THE WEB & CRAFTING YOUR PERFECT TRIP... ⏳"):
            try:
                result = generate_itinerary(
                    destination, duration, budget,
                    travel_dates, travelers,
                    interests, special_requirements
                )

                st.markdown("---")
                st.markdown(
                    '<div class="success-header">'
                    '✅ YOUR PERSONALIZED ITINERARY IS READY!'
                    '</div>',
                    unsafe_allow_html=True
                )
                st.markdown(
                    '<div class="result-container">',
                    unsafe_allow_html=True
                )
                st.markdown(result)
                st.markdown('</div>', unsafe_allow_html=True)

                st.markdown("---")
                st.markdown(
                    '<div class="section-title">📤 SAVE OR SHARE YOUR ITINERARY</div>',
                    unsafe_allow_html=True
                )

                dl_col, wa_col = st.columns(2)

                with dl_col:
                    st.download_button(
                        label="📥 DOWNLOAD AS TEXT FILE",
                        data=result,
                        file_name=f"MANISH_{destination.replace(' ','_').upper()}_TRIP.txt",
                        mime="text/plain",
                        use_container_width=True
                    )

                with wa_col:
                    share_msg = (
                        f"✈️ *{duration}-DAY {destination.upper()} TRIP*\n"
                        f"━━━━━━━━━━━━━━━━━━\n"
                        f"📅 DATES: {travel_dates}\n"
                        f"👥 TRAVELERS: {travelers}\n"
                        f"💰 BUDGET: {budget}\n"
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
                        f'color:white;padding:13px 20px;border-radius:10px;'
                        f'font-weight:900;font-size:0.95rem;text-transform:uppercase;'
                        f'letter-spacing:1px;text-align:center;cursor:pointer;'
                        f'box-shadow:0 4px 20px rgba(34,197,94,0.5);margin-top:6px;">'
                        f'📱 SHARE ON WHATSAPP'
                        f'</div></a>',
                        unsafe_allow_html=True
                    )

            except Exception as e:
                st.error(f"❌ ERROR: {str(e)}")
                st.info("💡 PLEASE TRY AGAIN IN A FEW SECONDS!")

# ── FOOTER ──
st.markdown("---")
st.markdown(
    '<div class="footer">BUILT WITH ❤️ USING GROQ AI + TAVILY + STREAMLIT</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="footer-brand">© 2025 MANISH TRAVEL ITINERARY PLANNER — ALL RIGHTS RESERVED</div>',
    unsafe_allow_html=True
)
