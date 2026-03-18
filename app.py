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
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
/* ══════════════════════════════════════
   BACKGROUND — Soft gradient both modes
══════════════════════════════════════ */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(160deg, #0f0c29, #302b63, #24243e) !important;
}
[data-testid="stAppViewContainer"][data-theme="light"] {
    background: linear-gradient(160deg, #e8eaf6, #ede7f6, #f3e5f5) !important;
}

/* Sidebar background */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%) !important;
}

/* ══════════════════════════════════════
   WATERMARK — visible but subtle
══════════════════════════════════════ */
[data-testid="stAppViewContainer"]::before {
    content: "MANISH TRAVEL PLANNER";
    position: fixed;
    top: 45%;
    left: 50%;
    transform: translate(-50%, -50%) rotate(-30deg);
    font-size: 5rem;
    font-weight: 900;
    color: rgba(167, 139, 250, 0.09);
    white-space: nowrap;
    pointer-events: none;
    z-index: 0;
    letter-spacing: 6px;
    text-transform: uppercase;
}
[data-testid="stAppViewContainer"]::after {
    content: "✈ MANISH ✈ TRAVEL ✈ PLANNER ✈ MANISH ✈ TRAVEL ✈ PLANNER";
    position: fixed;
    bottom: 15%;
    left: 50%;
    transform: translate(-50%, 0) rotate(-30deg);
    font-size: 1.8rem;
    font-weight: 700;
    color: rgba(167, 139, 250, 0.06);
    white-space: nowrap;
    pointer-events: none;
    z-index: 0;
    letter-spacing: 4px;
}

/* ══════════════════════════════════════
   TITLE
══════════════════════════════════════ */
.main-title {
    text-align: center;
    font-size: 2.8rem;
    font-weight: 900;
    letter-spacing: 4px;
    text-transform: uppercase;
    padding: 15px 0 5px 0;
    background: linear-gradient(135deg, #a78bfa, #60a5fa, #34d399);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.subtitle {
    text-align: center;
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 3px;
    opacity: 0.6;
    color: #c4b5fd;
    margin-bottom: 3px;
}
.brand-tag {
    text-align: center;
    font-size: 0.8rem;
    letter-spacing: 3px;
    color: #a78bfa;
    font-weight: 700;
    text-transform: uppercase;
    margin-bottom: 10px;
}

/* ══════════════════════════════════════
   SECTION TITLES
══════════════════════════════════════ */
.section-title {
    font-size: 1.1rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: #a78bfa;
    margin-bottom: 10px;
    border-left: 4px solid #a78bfa;
    padding-left: 10px;
}

/* ══════════════════════════════════════
   WEATHER BOX
══════════════════════════════════════ */
.weather-box {
    background: linear-gradient(135deg, #1e1b4b99, #312e8199);
    border: 1.5px solid #6366f1;
    border-radius: 12px;
    padding: 10px 16px;
    margin: 8px 0 12px 0;
    font-size: 0.9rem;
    font-weight: 600;
    color: #e0e7ff;
    line-height: 1.8;
}

/* ══════════════════════════════════════
   POPULAR DESTINATION BUTTONS
══════════════════════════════════════ */
div[data-testid="column"] .stButton > button {
    background: linear-gradient(135deg, #312e81, #4338ca) !important;
    color: #c4b5fd !important;
    font-size: 0.8rem !important;
    font-weight: 700 !important;
    padding: 8px 4px !important;
    border-radius: 8px !important;
    border: 1px solid #6366f1 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
    margin-top: 4px !important;
    transition: all 0.2s !important;
}
div[data-testid="column"] .stButton > button:hover {
    background: linear-gradient(135deg, #4f46e5, #7c3aed) !important;
    color: white !important;
    border-color: #a78bfa !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 4px 15px rgba(99,102,241,0.4) !important;
}

/* ══════════════════════════════════════
   GENERATE BUTTON — BIG & COLORFUL
══════════════════════════════════════ */
.stButton > button[kind="primary"],
.stButton > button {
    width: 100%;
    background: linear-gradient(135deg, #4f46e5, #7c3aed, #a855f7) !important;
    color: white !important;
    font-size: 1.2rem !important;
    font-weight: 900 !important;
    padding: 18px 30px !important;
    border-radius: 14px !important;
    border: none !important;
    text-transform: uppercase !important;
    letter-spacing: 2px !important;
    box-shadow: 0 8px 32px rgba(99,102,241,0.5) !important;
    transition: all 0.3s !important;
}
.stButton > button:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 12px 40px rgba(99,102,241,0.7) !important;
}

/* ══════════════════════════════════════
   SUCCESS HEADER
══════════════════════════════════════ */
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

/* ══════════════════════════════════════
   RESULT BOX
══════════════════════════════════════ */
.result-container {
    border: 1px solid #4f46e544;
    border-radius: 16px;
    padding: 25px 30px;
    margin-bottom: 20px;
    background: rgba(30, 27, 75, 0.3);
}

/* ══════════════════════════════════════
   DOWNLOAD BUTTON
══════════════════════════════════════ */
.stDownloadButton > button {
    background: linear-gradient(135deg, #1e40af, #3b82f6) !important;
    color: white !important;
    font-weight: 800 !important;
    font-size: 0.95rem !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
    border-radius: 10px !important;
    border: none !important;
    padding: 12px 20px !important;
    box-shadow: 0 4px 15px rgba(59,130,246,0.4) !important;
    width: 100% !important;
}

/* ══════════════════════════════════════
   FOOTER
══════════════════════════════════════ */
.footer {
    text-align: center;
    text-transform: uppercase;
    letter-spacing: 2px;
    opacity: 0.4;
    font-size: 0.75rem;
    margin-top: 5px;
    color: #a78bfa;
}
.footer-brand {
    text-align: center;
    text-transform: uppercase;
    letter-spacing: 3px;
    font-size: 0.7rem;
    color: #a78bfa;
    opacity: 0.6;
    margin-top: 3px;
}

/* ══════════════════════════════════════
   INPUT FIELDS
══════════════════════════════════════ */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stNumberInput > div > div > input {
    background: rgba(30, 27, 75, 0.5) !important;
    border: 1px solid #4f46e5 !important;
    border-radius: 8px !important;
    color: white !important;
}
.stSelectbox > div > div {
    background: rgba(30, 27, 75, 0.5) !important;
    border: 1px solid #4f46e5 !important;
}
</style>
""", unsafe_allow_html=True)


# ── SIDEBAR ──
with st.sidebar:
    st.markdown(
        "<h2 style='color:#a78bfa;text-transform:uppercase;"
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
        "<div style='text-align:center;color:#a78bfa;font-size:0.75rem;"
        "text-transform:uppercase;letter-spacing:2px;'>"
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
# POPULAR DESTINATIONS
# ══════════════════════════════════════
st.markdown('<div class="section-title">🔥 POPULAR DESTINATIONS — CLICK TO AUTO-FILL</div>',
            unsafe_allow_html=True)

if "selected_destination" not in st.session_state:
    st.session_state.selected_destination = ""

popular_destinations = [
    ("🗼", "Paris"),    ("🗽", "New York"),  ("🏯", "Tokyo"),    ("🕌", "Dubai"),
    ("🏛️", "Rome"),     ("🌴", "Bali"),      ("🐘", "Kerala"),   ("⛩️", "Rajasthan"),
    ("🏔️", "Manali"),   ("🌊", "Goa"),       ("🏰", "London"),   ("🗺️", "Singapore"),
]

cols = st.columns(6)
for i, (emoji, city) in enumerate(popular_destinations):
    if cols[i % 6].button(
        f"{emoji} {city.upper()}",
        use_container_width=True,
        key=f"pop_{i}"
    ):
        st.session_state.selected_destination = city
        st.rerun()

st.markdown("---")

# ── INPUTS ──
st.markdown('<div class="section-title">📝 TELL US ABOUT YOUR DREAM TRIP</div>',
            unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    destination = st.text_input(
        "🗺️ DESTINATION",
        value=st.session_state.selected_destination,
        placeholder="e.g. Goa OR click above!"
    )
    if destination != st.session_state.selected_destination:
        st.session_state.selected_destination = destination

    # ── WEATHER WIDGET ──
    if destination and len(destination) > 2:
        try:
            w1 = requests.get(
                f"https://wttr.in/{destination}?format=3",
                timeout=5
            )
            w2 = requests.get(
                f"https://wttr.in/{destination}?format=%C+%t+💧+%h+humidity",
                timeout=5
            )
            if w1.status_code == 200 and destination.lower() not in w1.text.lower().replace(destination.lower(),""):
                st.markdown(
                    f'<div class="weather-box">'
                    f'🌤️ <strong>LIVE WEATHER — {destination.upper()}</strong><br>'
                    f'📍 {w1.text.strip()}<br>'
                    f'🌡️ {w2.text.strip() if w2.status_code == 200 else "—"}'
                    f'</div>',
                    unsafe_allow_html=True
                )
        except Exception:
            pass

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
        curr_key       = [k for k in ph_map if k in currency][0]
        ph, hint       = ph_map[curr_key]
        budget_amount  = st.text_input("AMOUNT", placeholder=ph, help=hint)

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
        web_info = "Popular destination with amazing attractions and restaurants."

    groq_client    = Groq(api_key=GROQ_API_KEY)
    interests_text = ", ".join(interests) if interests else "General Sightseeing"
    special_text   = special_requirements or "None"
    curr_symbol    = budget.split()[0]

    prompt = f"""You are an expert AI Travel Planner with 20 years experience.

Real-time web info about {destination}:
{web_info}

Create a detailed {duration}-day itinerary:
- Destination: {destination}
- Dates: {travel_dates}
- Budget: {budget}
- Travelers: {travelers}
- Interests: {interests_text}
- Special Notes: {special_text}

Show prices in {curr_symbol} AND USD equivalent.

## 🌍 DESTINATION OVERVIEW
[4 sentences about destination]

## 📅 DAY-BY-DAY ITINERARY
### DAY 1 — [THEME]
- **MORNING:** [activity + detail]
- **AFTERNOON:** [activity + detail]
- **EVENING:** [dinner + detail]
[All {duration} days with unique themes]

## 🏨 HOTEL RECOMMENDATIONS
1. **[HOTEL]** — [{curr_symbol}/USD] — [why great]
2. **[HOTEL]** — [{curr_symbol}/USD] — [why great]
3. **[HOTEL]** — [{curr_symbol}/USD] — [why great]

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
1. [local tip]
2. [attraction tip]
3. [cultural tip]
4. [safety tip]
5. [money saving tip]

## 🚗 GETTING AROUND
[Transport options with costs in {curr_symbol}]
"""

    resp = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "Expert travel planner. Detailed specific itineraries with accurate local prices."},
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
                    '<div class="success-header">✅ YOUR PERSONALIZED ITINERARY IS READY!</div>',
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

                # ── DOWNLOAD + WHATSAPP SIDE BY SIDE ──
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
                        f'<div style="'
                        f'background:linear-gradient(135deg,#15803d,#22c55e);'
                        f'color:white;'
                        f'padding:10px 20px;'
                        f'border-radius:10px;'
                        f'font-weight:900;'
                        f'font-size:0.95rem;'
                        f'text-transform:uppercase;'
                        f'letter-spacing:1px;'
                        f'text-align:center;'
                        f'cursor:pointer;'
                        f'box-shadow:0 4px 20px rgba(34,197,94,0.5);'
                        f'margin-top:6px;'
                        f'border:none;">'
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
