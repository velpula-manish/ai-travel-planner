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
    .main-title {
        text-align: center;
        font-size: 3rem;
        font-weight: 900;
        letter-spacing: 3px;
        text-transform: uppercase;
        padding: 20px 0 5px 0;
        color: var(--text-color);
    }
    .subtitle {
        text-align: center;
        font-size: 1rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        opacity: 0.75;
        margin-bottom: 10px;
        color: var(--text-color);
    }
    .section-title {
        font-size: 1.3rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        color: #a78bfa;
        margin-bottom: 10px;
    }
    .weather-box {
        background: linear-gradient(135deg, #667eea22, #764ba222);
        border: 1px solid #a78bfa;
        border-radius: 12px;
        padding: 12px 20px;
        margin-bottom: 15px;
        font-size: 1rem;
        font-weight: 600;
    }
    .popular-btn {
        margin-bottom: 15px;
    }
    .stButton > button {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        color: white !important;
        font-size: 1.1rem;
        font-weight: 800;
        padding: 15px;
        border-radius: 12px;
        border: none !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 10px;
    }
    .success-header {
        background: linear-gradient(135deg, #11998e, #38ef7d);
        color: white !important;
        padding: 15px 25px;
        border-radius: 12px;
        font-size: 1.3rem;
        font-weight: 800;
        margin-bottom: 20px;
        text-align: center;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    .whatsapp-btn {
        display: inline-block;
        background: #25D366;
        color: white !important;
        padding: 12px 25px;
        border-radius: 10px;
        font-weight: 800;
        font-size: 1rem;
        text-decoration: none;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 10px;
        text-align: center;
    }
    .whatsapp-btn:hover {
        background: #128C7E;
        color: white !important;
    }
    .footer {
        text-align: center;
        text-transform: uppercase;
        letter-spacing: 1px;
        opacity: 0.5;
        font-size: 0.85rem;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ── SIDEBAR ──
with st.sidebar:
    st.markdown("## 🌍 AI TRAVEL PLANNER")
    st.markdown("---")
    st.markdown("### ⚡ POWERED BY")
    st.markdown("""
    - 🧠 **GROQ** — LLaMA 3.1 AI Brain
    - 🔍 **TAVILY** — Real-Time Web Search
    - 🌤️ **WTTR.IN** — Live Weather Data
    - 🎨 **STREAMLIT** — Beautiful UI
    """)
    st.markdown("---")
    st.markdown("### 📌 HOW TO USE")
    st.markdown("""
    1. Click a **POPULAR DESTINATION** or type your own
    2. Set your **TRIP DURATION**
    3. Choose your **CURRENCY & BUDGET**
    4. Enter **TRAVEL DATES**
    5. Pick your **INTERESTS**
    6. Click **GENERATE** and wait!
    7. **SHARE** on WhatsApp!
    """)
    st.markdown("---")
    st.markdown("### ✈️ FEATURES")
    st.markdown("""
    - 🗺️ Day-by-day itinerary
    - 🌤️ Live weather info
    - 🏨 Hotel recommendations
    - 🍽️ Restaurant picks
    - 💰 Multi-currency budget
    - 💡 Local travel tips
    - 📱 WhatsApp sharing
    """)
    st.markdown("---")
    st.info("🤖 AI searches the web in real-time for the latest travel info!")

# ── HEADER ──
st.markdown('<div class="main-title">🌍 AI TRAVEL ITINERARY PLANNER</div>',
            unsafe_allow_html=True)
st.markdown('<div class="subtitle">✨ YOUR PERSONAL AI TRAVEL AGENT — POWERED BY GROQ + TAVILY</div>',
            unsafe_allow_html=True)
st.markdown("---")


# ════════════════════════════════════════
# FEATURE 1: POPULAR DESTINATIONS BUTTONS
# ════════════════════════════════════════
st.markdown('<div class="section-title">🔥 POPULAR DESTINATIONS</div>',
            unsafe_allow_html=True)
st.caption("Click any destination to auto-fill OR type your own below!")

# Initialize session state for destination
if "selected_destination" not in st.session_state:
    st.session_state.selected_destination = ""

# Popular destinations list
popular_destinations = [
    "🗼 Paris",      "🗽 New York",   "🏯 Tokyo",      "🕌 Dubai",
    "🏛️ Rome",       "🌴 Bali",       "🐘 Kerala",     "⛩️ Rajasthan",
    "🏔️ Manali",     "🌊 Goa",        "🏰 London",     "🗺️ Singapore"
]

# Display buttons in 4 columns
cols = st.columns(4)
for i, place in enumerate(popular_destinations):
    # Extract just the city name (remove emoji)
    city_name = " ".join(place.split(" ")[1:])
    if cols[i % 4].button(place, use_container_width=True, key=f"dest_{i}"):
        st.session_state.selected_destination = city_name

st.markdown("---")


# ── INPUT FORM ──
st.markdown('<div class="section-title">📝 TELL US ABOUT YOUR DREAM TRIP</div>',
            unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    # Destination input — auto-filled if popular button clicked
    destination = st.text_input(
        "🗺️ DESTINATION",
        value=st.session_state.selected_destination,
        placeholder="e.g. Paris, France or type any city"
    )

    # ════════════════════════════════════════
    # FEATURE 2: LIVE WEATHER WIDGET
    # ════════════════════════════════════════
    if destination:
        try:
            # wttr.in gives free weather — no API key needed!
            weather_url = f"https://wttr.in/{destination}?format=3"
            weather_response = requests.get(weather_url, timeout=5)

            if weather_response.status_code == 200:
                weather_text = weather_response.text.strip()

                # Get more detailed weather
                weather_detail_url = f"https://wttr.in/{destination}?format=%C+%t+%h+humidity"
                weather_detail = requests.get(weather_detail_url, timeout=5)
                detail_text = weather_detail.text.strip() if weather_detail.status_code == 200 else ""

                st.markdown(
                    f'<div class="weather-box">'
                    f'🌤️ <strong>LIVE WEATHER</strong><br>'
                    f'📍 {weather_text}<br>'
                    f'💧 {detail_text}'
                    f'</div>',
                    unsafe_allow_html=True
                )
        except Exception:
            # Silently fail — weather is bonus feature
            pass

    duration = st.slider("📅 TRIP DURATION (DAYS)", 1, 14, 3)

    # ── BUDGET ──
    st.markdown("##### 💰 BUDGET")
    b_col1, b_col2 = st.columns([1, 2])

    with b_col1:
        currency = st.selectbox(
            "CURRENCY",
            options=["₹ INR", "$ USD", "€ EUR", "£ GBP"],
            index=0
        )
    with b_col2:
        if "INR" in currency:
            placeholder = "e.g. 50000"
            hint = "Typical range: ₹20,000 – ₹2,00,000"
        elif "USD" in currency:
            placeholder = "e.g. 1500"
            hint = "Typical range: $500 – $10,000"
        elif "EUR" in currency:
            placeholder = "e.g. 1200"
            hint = "Typical range: €500 – €8,000"
        else:
            placeholder = "e.g. 1000"
            hint = "Typical range: £400 – £7,000"

        budget_amount = st.text_input("AMOUNT", placeholder=placeholder, help=hint)

    if budget_amount:
        try:
            amt = float(budget_amount.replace(",", ""))
            if "INR" in currency:
                if amt < 30000:       tier = "🟢 BUDGET TRIP"
                elif amt < 80000:     tier = "🟡 MODERATE TRIP"
                elif amt < 150000:    tier = "🟠 COMFORTABLE TRIP"
                else:                 tier = "🔴 LUXURY TRIP"
            else:
                if amt < 800:         tier = "🟢 BUDGET TRIP"
                elif amt < 2500:      tier = "🟡 MODERATE TRIP"
                elif amt < 5000:      tier = "🟠 COMFORTABLE TRIP"
                else:                 tier = "🔴 LUXURY TRIP"
            st.caption(f"**{tier}**")
        except:
            pass

    budget = f"{currency} {budget_amount}" if budget_amount else f"{currency} (not specified)"

with col2:
    travel_dates = st.text_input("🗓️ TRAVEL DATES", placeholder="e.g. June 10–17, 2025")
    travelers    = st.number_input("👥 NUMBER OF TRAVELERS", 1, 20, 2)
    interests    = st.multiselect("❤️ YOUR INTERESTS", [
        "🏛️ History & Culture", "🍽️ Food & Dining",
        "🎨 Art & Museums",     "🌿 Nature & Outdoors",
        "🛍️ Shopping",          "🎭 Nightlife",
        "🏖️ Beach & Relaxation","🏔️ Adventure & Sports",
        "📸 Photography",       "👨‍👩‍👧 Family Friendly"
    ], default=["🍽️ Food & Dining", "🎨 Art & Museums"])

special_requirements = st.text_area(
    "💬 SPECIAL REQUIREMENTS (OPTIONAL)",
    placeholder="e.g. Vegetarian food, travelling with friends...",
    height=80
)
st.markdown("---")


# ── ITINERARY GENERATOR ──
def generate_itinerary(destination, duration, budget, travel_dates,
                        travelers, interests, special_requirements):

    tavily = TavilyClient(api_key=TAVILY_API_KEY)
    try:
        search_results = tavily.search(
            query=f"best things to do hotels restaurants in {destination} travel tips",
            max_results=3,
            search_depth="basic"
        )
        web_info = ""
        for r in search_results.get("results", []):
            web_info += f"\n- {r.get('title','')}: {r.get('content','')[:300]}"
    except Exception:
        web_info = "Popular destination with great attractions, hotels and restaurants."

    groq_client    = Groq(api_key=GROQ_API_KEY)
    interests_text = ", ".join(interests) if interests else "General Sightseeing"
    special_text   = special_requirements if special_requirements else "None"

    prompt = f"""You are an expert AI Travel Planner with 20 years of experience.

Real-time web information about {destination}:
{web_info}

Create a detailed {duration}-day travel itinerary for:
- Destination: {destination}
- Travel Dates: {travel_dates}
- Budget: {budget}
- Number of Travelers: {travelers}
- Interests: {interests_text}
- Special Requirements: {special_text}

IMPORTANT: Show ALL prices in BOTH {budget.split()[0]} AND USD.

## 🌍 DESTINATION OVERVIEW
[3-4 sentences about the destination]

## 📅 DAY-BY-DAY ITINERARY
### DAY 1 - [Theme]
- **MORNING:** [Activity with details]
- **AFTERNOON:** [Activity with details]
- **EVENING:** [Dinner with details]
[Continue for all {duration} days]

## 🏨 HOTEL RECOMMENDATIONS
1. **[Hotel]** — [Price in {budget.split()[0]} & USD] — [Why great]
2. **[Hotel]** — [Price in {budget.split()[0]} & USD] — [Why great]
3. **[Hotel]** — [Price in {budget.split()[0]} & USD] — [Why great]

## 🍽️ MUST-TRY RESTAURANTS
1. **[Restaurant]** — [Cuisine] — [Dish] — [Cost in {budget.split()[0]}]
2. **[Restaurant]** — [Cuisine] — [Dish] — [Cost in {budget.split()[0]}]
3. **[Restaurant]** — [Cuisine] — [Dish] — [Cost in {budget.split()[0]}]
4. **[Restaurant]** — [Cuisine] — [Dish] — [Cost in {budget.split()[0]}]
5. **[Restaurant]** — [Cuisine] — [Dish] — [Cost in {budget.split()[0]}]

## 💰 BUDGET BREAKDOWN
- **Accommodation:** [Amount] per night
- **Food:** [Amount] per day per person
- **Activities:** [Amount] total
- **Local Transport:** [Amount] total
- **TOTAL ESTIMATE: [Amount] for {travelers} traveler(s)**

## 💡 TOP TRAVEL TIPS
1. [Destination tip]
2. [Best time for attractions]
3. [Cultural etiquette]
4. [Safety tip]
5. [Money saving tip]

## 🚗 GETTING AROUND
[3-4 sentences about local transport with costs]
"""

    response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are an expert travel planner. Write detailed, specific, helpful itineraries with accurate local prices."},
            {"role": "user",   "content": prompt}
        ],
        max_tokens=3000,
        temperature=0.7
    )
    return response.choices[0].message.content


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
        with st.spinner("🔍 AI IS SEARCHING THE WEB & PLANNING YOUR TRIP... 30–60 SECONDS ⏳"):
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

                # ── Display Result ──
                st.markdown(result)
                st.markdown("---")

                # ── ACTION BUTTONS ROW ──
                action_col1, action_col2 = st.columns(2)

                with action_col1:
                    # Download Button
                    st.download_button(
                        label="📥 DOWNLOAD AS TEXT FILE",
                        data=result,
                        file_name=f"itinerary_{destination.replace(' ','_')}.txt",
                        mime="text/plain",
                        use_container_width=True
                    )

                with action_col2:
                    # ════════════════════════════════════════
                    # FEATURE 3: WHATSAPP SHARE BUTTON
                    # ════════════════════════════════════════
                    # Create share message
                    share_message = (
                        f"✈️ *MY {duration}-DAY {destination.upper()} TRIP PLAN*\n\n"
                        f"📅 Dates: {travel_dates}\n"
                        f"👥 Travelers: {travelers}\n"
                        f"💰 Budget: {budget}\n\n"
                        f"🤖 Generated by AI Travel Planner\n\n"
                        f"{result[:800]}...\n\n"
                        f"🌍 Plan your trip at:\n"
                        f"https://ai-travel-planner-h7f7ryewjbufa5tdvfewnu.streamlit.app"
                    )

                    # Encode for WhatsApp URL
                    encoded_message = urllib.parse.quote(share_message)
                    whatsapp_url    = f"https://wa.me/?text={encoded_message}"

                    # WhatsApp button
                    st.markdown(
                        f'<a href="{whatsapp_url}" target="_blank" style="text-decoration:none;">'
                        f'<div style="background:#25D366;color:white;padding:14px;'
                        f'border-radius:10px;font-weight:800;font-size:1rem;'
                        f'text-transform:uppercase;letter-spacing:1px;'
                        f'text-align:center;cursor:pointer;margin-top:8px;">'
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
