%%writefile app.py

import streamlit as st
import os
from groq import Groq
from tavily import TavilyClient

# ── API KEYS FROM STREAMLIT SECRETS ──
GROQ_API_KEY   = st.secrets["GROQ_API_KEY"]
TAVILY_API_KEY = st.secrets["TAVILY_API_KEY"]

# ── PAGE CONFIG ──
st.set_page_config(
    page_title="AI Travel Planner ✈️",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── STYLING ──
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
        margin-bottom: 15px;
    }
    .stButton > button {
        width: 100%;
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
    - 🎨 **STREAMLIT** — Beautiful UI
    """)
    st.markdown("---")
    st.markdown("### 📌 HOW TO USE")
    st.markdown("""
    1. Enter your **DESTINATION**
    2. Set your **TRIP DURATION**
    3. Choose your **BUDGET**
    4. Pick your **INTERESTS**
    5. Click **GENERATE** and wait!
    """)
    st.markdown("---")
    st.markdown("### ✈️ FEATURES")
    st.markdown("""
    - 🗺️ Day-by-day itinerary
    - 🏨 Hotel recommendations
    - 🍽️ Restaurant picks
    - 💰 Budget breakdown
    - 💡 Local travel tips
    """)
    st.markdown("---")
    st.info("🤖 AI searches the web in real-time for the latest travel info!")

# ── HEADER ──
st.markdown('<div class="main-title">🌍 AI TRAVEL ITINERARY PLANNER</div>',
            unsafe_allow_html=True)
st.markdown('<div class="subtitle">✨ YOUR PERSONAL AI TRAVEL AGENT — POWERED BY GROQ + TAVILY</div>',
            unsafe_allow_html=True)
st.markdown("---")

# ── INPUT FORM ──
st.markdown('<div class="section-title">📝 TELL US ABOUT YOUR DREAM TRIP</div>',
            unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    destination = st.text_input("🗺️ DESTINATION", placeholder="e.g. Paris, France")
    duration    = st.slider("📅 TRIP DURATION (DAYS)", 1, 14, 3)
    budget      = st.selectbox("💰 BUDGET RANGE", [
        "Budget ($500–$1000)", "Moderate ($1000–$2500)",
        "Comfortable ($2500–$5000)", "Luxury ($5000+)"
    ], index=1)

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


# ── CORE FUNCTION: Search + Generate ──
def generate_itinerary(destination, duration, budget, travel_dates,
                        travelers, interests, special_requirements):
    """
    Step 1: Search web with Tavily
    Step 2: Send results to Groq to write itinerary
    No LangChain needed — direct API calls!
    """

    # ── STEP 1: Search with Tavily ──
    tavily = TavilyClient(api_key=TAVILY_API_KEY)

    search_query = (
        f"best things to do hotels restaurants in {destination} "
        f"travel tips budget {budget}"
    )

    try:
        search_results = tavily.search(
            query=search_query,
            max_results=3,
            search_depth="basic"
        )
        # Extract text from results
        web_info = ""
        for r in search_results.get("results", []):
            web_info += f"\n- {r.get('title','')}: {r.get('content','')[:300]}"
    except Exception:
        web_info = f"Popular destination with great attractions, hotels and restaurants."

    # ── STEP 2: Generate with Groq ──
    groq_client = Groq(api_key=GROQ_API_KEY)

    interests_text = ", ".join(interests) if interests else "General Sightseeing"
    special_text   = special_requirements if special_requirements else "None"

    prompt = f"""You are an expert AI Travel Planner with 20 years of experience.

Here is real-time web information about {destination}:
{web_info}

Using this information, create a detailed {duration}-day travel itinerary for:
- Destination: {destination}
- Travel Dates: {travel_dates}
- Budget: {budget}
- Number of Travelers: {travelers}
- Interests: {interests_text}
- Special Requirements: {special_text}

Write a complete, detailed itinerary with EXACTLY these sections
using UPPERCASE headings:

## 🌍 DESTINATION OVERVIEW
[Write 3-4 sentences about the destination]

## 📅 DAY-BY-DAY ITINERARY
### DAY 1 - [Theme]
- **MORNING:** [Specific activity with details]
- **AFTERNOON:** [Specific activity with details]
- **EVENING:** [Dinner recommendation with details]

[Continue for all {duration} days with different activities each day]

## 🏨 HOTEL RECOMMENDATIONS
1. **[Hotel Name]** — [Price range] — [Why it's great]
2. **[Hotel Name]** — [Price range] — [Why it's great]
3. **[Hotel Name]** — [Price range] — [Why it's great]

## 🍽️ MUST-TRY RESTAURANTS
1. **[Restaurant]** — [Cuisine type] — [Must-try dish]
2. **[Restaurant]** — [Cuisine type] — [Must-try dish]
3. **[Restaurant]** — [Cuisine type] — [Must-try dish]
4. **[Restaurant]** — [Cuisine type] — [Must-try dish]
5. **[Restaurant]** — [Cuisine type] — [Must-try dish]

## 💰 BUDGET BREAKDOWN
- **Accommodation:** $X per night
- **Food:** $X per day per person
- **Activities:** $X total
- **Local Transport:** $X total
- **TOTAL ESTIMATE: $X for {travelers} traveler(s)**

## 💡 TOP TRAVEL TIPS
1. [Important tip about the destination]
2. [Best time to visit specific attractions]
3. [Cultural etiquette or local customs]
4. [Safety or health tip]
5. [Money saving tip]

## 🚗 GETTING AROUND
[3-4 sentences about local transport options, costs, and recommendations]
"""

    response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": "You are an expert travel planner. Always write detailed, specific, and helpful travel itineraries."
            },
            {
                "role": "user",
                "content": prompt
            }
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
        st.error("⚠️ PLEASE ENTER A DESTINATION!")
    elif not travel_dates:
        st.error("⚠️ PLEASE ENTER YOUR TRAVEL DATES!")
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
                st.markdown(result)

                st.download_button(
                    "📥 DOWNLOAD ITINERARY AS TEXT FILE",
                    data=result,
                    file_name=f"itinerary_{destination.replace(' ','_')}.txt",
                    mime="text/plain"
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
