
import streamlit as st
import os
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain_community.tools.tavily_search import TavilySearchResults

# ✅ SAFE: Reads from Streamlit Secrets (NOT hardcoded!)
# No API keys written here — they live in Streamlit Cloud secrets
GROQ_API_KEY   = st.secrets["GROQ_API_KEY"]
TAVILY_API_KEY = st.secrets["TAVILY_API_KEY"]

os.environ["GROQ_API_KEY"]   = GROQ_API_KEY
os.environ["TAVILY_API_KEY"] = TAVILY_API_KEY

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

with st.sidebar:
    st.markdown("## 🌍 AI TRAVEL PLANNER")
    st.markdown("---")
    st.markdown("### ⚡ POWERED BY")
    st.markdown("""
    - 🧠 **GROQ** — LLaMA 3.1 AI Brain
    - 🔍 **TAVILY** — Real-Time Web Search
    - 🤖 **LANGCHAIN** — Agent Framework
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

st.markdown('<div class="main-title">🌍 AI TRAVEL ITINERARY PLANNER</div>',
            unsafe_allow_html=True)
st.markdown('<div class="subtitle">✨ YOUR PERSONAL AI TRAVEL AGENT — POWERED BY GROQ + TAVILY</div>',
            unsafe_allow_html=True)
st.markdown("---")

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

@st.cache_resource
def initialize_agent():
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0.5,
        api_key=GROQ_API_KEY,
        max_tokens=3000
    )
    search_tool = TavilySearchResults(
        max_results=2, search_depth="basic",
        api_key=TAVILY_API_KEY
    )
    tools = [search_tool]
    travel_prompt = PromptTemplate.from_template("""You are an expert AI Travel Planner.
Search ONCE then write a COMPLETE itinerary immediately.
RULES: Maximum 2 searches. After searching write Final Answer immediately.
Tools: {tools}
Format:
Question: travel request
Thought: I will search for key info
Action: {tool_names}
Action Input: best attractions hotels restaurants [destination]
Observation: results
Thought: I have enough info. Writing itinerary now.
Final Answer:
## 🌍 DESTINATION OVERVIEW
## 📅 DAY-BY-DAY ITINERARY
## 🏨 HOTEL RECOMMENDATIONS
## 🍽️ MUST-TRY RESTAURANTS
## 💰 BUDGET BREAKDOWN
## 💡 TOP TRAVEL TIPS
## 🚗 GETTING AROUND
Question: {input}
Thought: {agent_scratchpad}""")
    agent = create_react_agent(llm=llm, tools=tools, prompt=travel_prompt)
    return AgentExecutor(
        agent=agent, tools=tools, verbose=False,
        max_iterations=5, max_execution_time=120,
        handle_parsing_errors=True
    )

generate_btn = st.button("🚀 GENERATE MY TRAVEL ITINERARY!", use_container_width=True)

if generate_btn:
    if not destination:
        st.error("⚠️ PLEASE ENTER A DESTINATION!")
    elif not travel_dates:
        st.error("⚠️ PLEASE ENTER YOUR TRAVEL DATES!")
    else:
        interests_text = ", ".join(interests) if interests else "General Sightseeing"
        special_text   = special_requirements if special_requirements else "None"
        user_query = (
            f"{duration}-day trip to {destination}. "
            f"Dates: {travel_dates}. Budget: {budget}. "
            f"Travelers: {travelers}. Interests: {interests_text}. "
            f"Notes: {special_text}."
        )
        with st.spinner("🔍 AI IS PLANNING YOUR TRIP... PLEASE WAIT 30–60 SECONDS ⏳"):
            try:
                agent    = initialize_agent()
                response = agent.invoke({"input": user_query})
                result   = response.get("output", "")

                if "Agent stopped" in result or len(result) < 100:
                    llm_direct = ChatGroq(
                        model="llama-3.1-8b-instant",
                        temperature=0.5,
                        api_key=GROQ_API_KEY,
                        max_tokens=3000
                    )
                    result = llm_direct.invoke(
                        f"Create a detailed {duration}-day itinerary for "
                        f"{destination}. Dates:{travel_dates}. Budget:{budget}. "
                        f"Travelers:{travelers}. Interests:{interests_text}. "
                        f"Use UPPERCASE markdown headings for all sections."
                    ).content

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
                st.info("💡 TRY A SHORTER TRIP OR SIMPLER DESTINATION!")

st.markdown("---")
st.markdown(
    '<div class="footer">BUILT WITH ❤️ USING GROQ AI + TAVILY + LANGCHAIN + STREAMLIT</div>',
    unsafe_allow_html=True
)
