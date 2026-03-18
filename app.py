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
    /* ── WATERMARK BACKGROUND ── */
    .stApp::before {
        content: "MANISH TRAVEL ITINERARY PLANNER";
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%) rotate(-35deg);
        font-size: 4.5rem;
        font-weight: 900;
        color: rgba(167, 139, 250, 0.06);
        white-space: nowrap;
        pointer-events: none;
        z-index: 0;
        letter-spacing: 4px;
        text-transform: uppercase;
    }

    /* ── REPEAT WATERMARK ── */
    .stApp::after {
        content: "✈ MANISH ✈ TRAVEL PLANNER ✈ MANISH ✈ TRAVEL PLANNER";
        position: fixed;
        top: 20%;
        left: 50%;
        transform: translate(-50%, -50%) rotate(-35deg);
        font-size: 2rem;
        font-weight: 700;
        color: rgba(167, 139, 250, 0.04);
        white-space: nowrap;
        pointer-events: none;
        z-index: 0;
        letter-spacing: 6px;
        text-transform: uppercase;
    }

    /* ── MAIN TITLE ── */
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

    /* ── SUBTITLE ── */
    .subtitle {
        text-align: center;
        font-size: 0.95rem;
        text-transform: uppercase;
        letter-spacing: 3px;
        opacity: 0.6;
        margin-bottom: 5px;
        color: var(--text-color);
    }

    /* ── BRAND TAG ── */
    .brand-tag {
        text-align: center;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        color: #a78bfa;
        font-weight: 700;
        margin-bottom: 15px;
    }

    /* ── SECTION TITLE ── */
    .section-title {
        font-size: 1.2rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 2px;
        color: #a78bfa;
        margin-bottom: 10px;
        border-left: 4px solid #a78bfa;
        padding-left: 10px;
    }

    /* ── WEATHER BOX ── */
    .weather-box {
        background: linear-gradient(135deg, #1e1b4b44, #312e8144);
        border: 1px solid #6366f1;
        border-radius: 12px;
        padding: 10px 16px;
        margin-bottom: 12px;
        font-size: 0.95rem;
        font-weight: 600;
        color: var(--text-color);
    }

    /* ── POPULAR DEST BUTTONS ── */
    div[data-testid="column"] .stButton > button {
        background: linear-gradient(135deg, #1e1b4b, #312e81) !important;
        color: #a78bfa !important;
        font-size: 0.85rem !important;
        font-weight: 700 !important;
        padding: 8px 5px !important;
        border-radius: 8px !important;
        border: 1px solid #4f46e5 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        margin-top: 3px !important;
        transition: all 0.2s ease !important;
    }
    div[data-testid="column"] .stButton > button:hover {
        background: linear-gradient(135deg, #4f46e5, #7c3aed) !important;
        color: white !important;
        border-color: #a78bfa !important;
    }

    /* ── GENERATE BUTTON ── */
    .generate-btn .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #4f46e5, #7c3aed, #a855f7) !important;
        color: white !important;
        font-size: 1.2rem !important;
        font-weight: 900 !important;
        padding: 18px !important;
        border-radius: 14px !important;
        border: none !important;
        text-transform: uppercase !important;
        letter-spacing: 2px !important;
        box-shadow: 0 8px 32px rgba(99, 102, 241, 0.4) !important;
    }

    /* ── SUCCESS HEADER ── */
    .success-header {
        background: linear-gradient(135deg, #059669, #10b981, #34d399);
        color: white !important;
        padding: 18px 25px;
        border-radius: 14px;
        font-size: 1.4rem;
        font-weight: 900;
        margin-bottom: 20px;
        text-align: center;
        text-transform: uppercase;
        letter-spacing: 3px;
        box-shadow: 0 8px 32px rgba(16, 185, 129, 0.3);
    }

    /* ── RESULT BOX ── */
    .result-container {
        border: 1px solid #4f46e5;
        border-radius: 16px;
        padding: 25px 30px;
        margin-bottom: 20px;
        background: transparent;
    }

    /* ── ACTION BUTTONS ROW ── */
    .action-row {
        display: flex;
        gap: 15px;
        margin-top: 20px;
        margin-bottom: 10px;
    }
    .download-btn {
        flex: 1;
        background: linear-gradient(135deg, #1e40af, #3b82f6);
        color: white !important;
        padding: 14px 20px;
        border-radius: 10px;
        font-weight: 800;
        font-size: 1rem;
        text-align: center;
        text-transform: uppercase;
        letter-spacing: 1px;
        cursor: pointer;
        border: none;
    }
    .whatsapp-btn {
        flex: 1;
        display: block;
        background: linear-gradient(135deg, #15803d, #22c55e);
        color: white !important;
        padding: 14px 20px;
        border-radius: 10px;
        font-weight: 800;
        font-size: 1rem;
        text-align: center;
        text-transform: uppercase;
        letter-spacing: 1px;
        text-decoration: none !important;
        cursor: pointer;
    }
    .whatsapp-btn:hover {
        background: linear-gradient(135deg, #166534, #16a34a);
        color: white !important;
    }

    /* ── DIVIDER ── */
    hr {
        border-color: #4f46e544 !important;
    }

    /* ── FOOTER ── */
    .footer {
        text-align: center;
        text-transform: uppercase;
        letter-spacing: 2px;
        opacity: 0.4;
        font-size: 0.8rem;
        margin-top: 10px;
        color: var(--text-color);
    }
    .footer-brand {
        text-align: center;
        text-transform: uppercase;
        letter-spacing: 3px;
        font-size: 0.75rem;
        color: #a78bfa;
        opacity: 0.7;
        margin-top: 5px;
    }
</style>
""", unsafe_allow_html=True)


# ── SIDEBAR ──
with st.sidebar:
    st.markdown("## 🌍 MANISH TRAVEL PLANNER")
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
    1. CLICK A **POPULAR DESTINATION** OR TYPE YOUR OWN
    2. SET YOUR **TRIP DURATION**
    3. CHOOSE YOUR **CURRENCY & BUDGET**
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
        "<div style='text-align:center;color:#a78bfa;font-size:0.8rem;"
        "text-transform:uppercase;letter-spacing:2px;'>"
        "© MANISH TRAVEL PLANNER<br>ALL RIGHTS RESERVED"
        "</div>",
        unsafe_allow_html=True
    )

# ── HEADER ──
st.markdown('<div class="main-title">🌍 AI TRAVEL ITINERARY PLANNER</div>',
            unsafe_allow_html=True)
st.markdown('<div class="subtitle">✨ YOUR PERSONAL AI TRAVEL AGENT — POWERED BY GROQ + TAVILY</div>',
            unsafe_allow_html=True)
st.markdown('<div class="brand-tag">— BY MANISH TRAVEL PLANNER —</div>',
            unsafe_allow_html=True)
st.markdown("---")


# ════════════════════════════════════════
# FEATURE 1: POPULAR DESTINATIONS
# ════════════════════════════════════════
st.markdown('<div class="section-title">🔥 POPULAR DESTINATIONS — CLICK TO AUTO-FILL</div>',
            unsafe_allow_html=True)

# Initialize session state
if "selected_destination" not in st.session_state:
    st.session_state.selected_destination = ""
if "trigger_rerun" not in st.session_state:
    st.session_state.trigger_rerun = False

popular_destinations = [
    ("🗼", "Paris"),       ("🗽", "New York"),
    ("🏯", "Tokyo"),       ("🕌", "Dubai"),
    ("🏛️", "Rome"),        ("🌴", "Bali"),
    ("🐘", "Kerala"),      ("⛩️", "Rajasthan"),
    ("🏔️", "Manali"),      ("🌊", "Goa"),
    ("🏰", "London"),      ("🗺️", "Singapore"),
]

cols = st.columns(6)
for i, (emoji, city) in enumerate(popular_destinations):
    if cols[i % 6].button(
        f"{emoji} {city.upper()}",
        use_container_width=True,
        key=f"pop_{i}"
    ):
        st.session_state.selected_destination = city
        st.rerun()  # ✅ THIS IS THE FIX — forces page refresh + autofill

st.markdown("---")


# ── INPUT FORM ──
st.markdown('<div class="section-title">📝 TELL US ABOUT YOUR DREAM TRIP</div>',
            unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    # ✅ Auto-filled from session state
    destination = st.text_input(
        "🗺️ DESTINATION",
        value=st.session_state.selected_destination,
        placeholder="e.g. Goa, India  OR  click above!"
    )

    # Update session state if user types manually
    if destination != st.session_state.selected_destination:
        st.session_state.selected_destination = destination

    # ════════════════════════════════════════
    # FEATURE 2: LIVE WEATHER WIDGET
    # ════════════════════════════════════════
    if destination and len(destination) > 2:
        try:
            w1 = requests.get(
                f"https://wttr.in/{destination}?format=3",
                timeout=4
            )
            w2 = requests.get(
                f"https://wttr.in/{destination}?format=%C+%t+💧%h+humidity",
                timeout=4
            )
            if w1.status_code == 200:
                st.markdown(
                    f'<div class="weather-box">'
                    f'🌤️ <strong>LIVE WEATHER IN {destination.upper()}</strong><br>'
                    f'📍 {w1.text.strip()}<br>'
                    f'🌡️ {w2.text.strip() if w2.status_code == 200 else ""}'
                    f'</div>',
                    unsafe_allow_html=True
                )
        except Exception:
            pass

    duration = st.slider("📅 TRIP DURATION (DAYS)", 1, 14, 3)

    # ── BUDGET ──
    st.markdown("##### 💰 BUDGET")
    b1, b2 = st.columns([1, 2])
    with b1:
        currency = st.selectbox(
            "CURRENCY",
            ["₹ INR", "$ USD", "€ EUR", "£ GBP"],
            index=0
        )
    with b2:
        placeholders = {
            "INR": ("e.g. 50000", "₹20,000 – ₹2,00,000"),
            "USD": ("e.g. 1500",  "$500 – $10,000"),
            "EUR": ("e.g. 1200",  "€500 – €8,000"),
            "GBP": ("e.g. 1000",  "£400 – £7,000"),
        }
        curr_key    = [k for k in placeholders if k in currency][0]
        ph, hint    = placeholders[curr_key]
        budget_amount = st.text_input("AMOUNT", placeholder=ph, help=hint)

    if budget_amount:
        try:
            amt  = float(budget_amount.replace(",", ""))
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
        except:
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
    except:
        web_info = "Popular destination with great attractions and restaurants."

    groq_client    = Groq(api_key=GROQ_API_KEY)
    interests_text = ", ".join(interests) if interests else "General Sightseeing"
    special_text   = special_requirements or "None"
    curr_symbol    = budget.split()[0]

    prompt = f"""You are an expert AI Travel Planner with 20 years experience.

Real-time web info about {destination}:
{web_info}

Create a detailed {duration}-day itinerary for:
- Destination: {destination}
- Dates: {travel_dates}
- Budget: {budget}
- Travelers: {travelers}
- Interests: {interests_text}
- Special Notes: {special_text}

Show ALL prices in {curr_symbol} AND USD equivalent.

## 🌍 DESTINATION OVERVIEW
[4 sentences about the destination]

## 📅 DAY-BY-DAY ITINERARY
### DAY 1 — [THEME IN CAPS]
- **MORNING:** [activity + details]
- **AFTERNOON:** [activity + details]  
- **EVENING:** [dinner + details]
[All {duration} days, each with unique theme]

## 🏨 HOTEL RECOMMENDATIONS
1. **[HOTEL]** — [{curr_symbol} price / USD] — [why great]
2. **[HOTEL]** — [{curr_symbol} price / USD] — [why great]
3. **[HOTEL]** — [{curr_symbol} price / USD] — [why great]

## 🍽️ MUST-TRY RESTAURANTS
1. **[RESTAURANT]** — [cuisine] — [dish] — [{curr_symbol} cost]
2. **[RESTAURANT]** — [cuisine] — [dish] — [{curr_symbol} cost]
3. **[RESTAURANT]** — [cuisine] — [dish] — [{curr_symbol} cost]
4. **[RESTAURANT]** — [cuisine] — [dish] — [{curr_symbol} cost]
5. **[RESTAURANT]** — [cuisine] — [dish] — [{curr_symbol} cost]

## 💰 BUDGET BREAKDOWN
- **ACCOMMODATION:** [{curr_symbol}] per night
- **FOOD:** [{curr_symbol}] per day per person
- **ACTIVITIES:** [{curr_symbol}] total
- **TRANSPORT:** [{curr_symbol}] total
- **TOTAL ESTIMATE: [{curr_symbol}] for {travelers} TRAVELER(S)**

## 💡 TOP TRAVEL TIPS
1. [Local tip]
2. [Best time tip]
3. [Cultural etiquette]
4. [Safety tip]
5. [Money saving tip]

## 🚗 GETTING AROUND
[Transport options with costs in {curr_symbol}]
"""

    resp = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "Expert travel planner. Write detailed, specific itineraries with accurate local prices."},
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
                    'YOUR PERSONALIZED ITINERARY IS READY!'
                    '</div>',
                    unsafe_allow_html=True
                )

                # Result display
                st.markdown(
                    '<div class="result-container">',
                    unsafe_allow_html=True
                )
                st.markdown(result)
                st.markdown('</div>', unsafe_allow_html=True)

                st.markdown("---")

                # ── ACTION BUTTONS ──
                st.markdown(
                    '<div class="section-title">📤 SAVE OR SHARE YOUR ITINERARY</div>',
                    unsafe_allow_html=True
                )

                btn_col1, btn_col2 = st.columns(2)

                with btn_col1:
                    st.download_button(
                        label="📥 DOWNLOAD AS TEXT FILE",
                        data=result,
                        file_name=f"MANISH_TRAVEL_{destination.replace(' ','_').upper()}.txt",
                        mime="text/plain",
                        use_container_width=True
                    )

                with btn_col2:
                    # ════════════════════════════════════════
                    # FEATURE 3: WHATSAPP SHARE BUTTON
                    # ════════════════════════════════════════
                    share_msg = (
                        f"✈️ *{duration}-DAY {destination.upper()} TRIP PLAN*\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"📅 *DATES:* {travel_dates}\n"
                        f"👥 *TRAVELERS:* {travelers}\n"
                        f"💰 *BUDGET:* {budget}\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n\n"
                        f"{result[:600]}...\n\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"🌍 *PLAN YOUR TRIP FREE AT:*\n"
                        f"https://ai-travel-planner-h7f7ryewjbufa5tdvfewnu.streamlit.app\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"_BY MANISH TRAVEL PLANNER_ 🗺️"
                    )
                    wa_url = f"https://wa.me/?text={urllib.parse.quote(share_msg)}"

                    st.markdown(
                        f'<a href="{wa_url}" target="_blank" style="text-decoration:none;">'
                        f'<div style="background:linear-gradient(135deg,#15803d,#22c55e);'
                        f'color:white;padding:8px 20px;border-radius:8px;'
                        f'font-weight:800;font-size:1rem;text-transform:uppercase;'
                        f'letter-spacing:1px;text-align:center;cursor:pointer;'
                        f'box-shadow:0 4px 15px rgba(34,197,94,0.4);margin-top:4px;">'
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
